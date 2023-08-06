# -*- coding: utf-8 -*-
from typing import List, Any
import threading
from google.protobuf.json_format import MessageToDict
from google.cloud import asset_v1p5beta1
from matos_gcp_provider.lib.auth import Connection
from matos_gcp_provider.plugins import get_package
from matos_gcp_provider.lib import factory, loader
from matos_gcp_provider.lib.log import get_logger
from matos_gcp_provider.config import (
    RESOURCE_TYPE_REQUESTS,
    ASSET_TYPES,
    PLURAL_RESOURCE_TYPE_LIST,
    IAM_TYPE,
    POD_STATUS
)

logger = get_logger()


class Provider(Connection):
    """ """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        loader.load_plugins(get_package())
        self.service_factory = factory

    def get_assets(self, **kwargs):
        """
        Discover aws resources
        """
        threads = []
        resources = [{"type": "iam"}]
        lock = threading.Lock()

        def fetch_discovery_details(_rsc_type, _project_id):
            service_discovery = self.service_factory.create({"type": _rsc_type, "project_id": _project_id})
            result = service_discovery.get_inventory()

            if result is None:
                return

            with lock:
                if isinstance(result, list):
                    resources.extend(result)
                else:
                    resources.append(result)

        service_map = self.service_factory.fetch_plugins()
        for rsc_type in service_map.keys():
            project_ids = self._get_projects()

            for project_id in project_ids:
                thread = threading.Thread(target=fetch_discovery_details, args=(rsc_type, project_id))
                thread.start()
                threads.append(thread)

        for t in threads:
            t.join()

        return resources

    def get_resource_inventories(self, resource_list: List[Any]):
        """
        Get resources data
        """
        print(resource_list)
        resource_inventories = {}
        lock = threading.Lock()

        def fetch_resource_details(_resource_type):

            try:
                detail = self._get_assets_inventory({"type": _resource_type})
                with lock:
                    resource_inventories[_resource_type] = detail
            except Exception as e:
                logger.error("error fetch resource %s" % e)

        threads = []
        for resource_type in RESOURCE_TYPE_REQUESTS.keys():
            thread = threading.Thread(target=fetch_resource_details, args=(resource_type,))
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()

        return resource_inventories

    def _get_assets_inventory(self, resource, **kwargs):
        """
        Export Google Cloud get_assets_inventoryResources as an assets data.
        """

        resource_type = resource.get('type', '')
        project_id = resource.get('project_id', None)

        try:
            gcp_resources, next_page_token = self._get_resources(
                project_id, resource_type
            )

            while next_page_token:
                logger.info(f"Next page token identified: {next_page_token}")

                gcp_resources, next_page_token = self._get_resources(
                    project_id,
                    resource_type,
                    gcp_resources,
                    next_page_token
                )
            logger.info(f"Resources fetched from GCP.{resource_type}")
            resource['details'] = gcp_resources
        except Exception as ex:
            logger.error("Error while calling list_assets again. %s" % str(ex))
        return resource

    def _get_resources(
            self,
            project_id: str,
            resource_type: str,
            resources: dict = None,
            next_page_token: str = None,
    ):
        response_dict = None

        # Step by step will add the provision to fetch all resource type details e.g. pod, services etc.
        if not RESOURCE_TYPE_REQUESTS[resource_type]:
            return resources, None

        request = {
            "asset_types": RESOURCE_TYPE_REQUESTS[resource_type],
            "parent": f"projects/{project_id if project_id is not None else self.projectId}",
            "content_type": asset_v1p5beta1.ContentType.RESOURCE
        }

        if next_page_token:
            request["page_token"] = next_page_token
        try:
            response = self.client.list_assets(request=request)
            response_dict = MessageToDict(response._pb)
            assets = response_dict.get("assets") or []
            resources = resources or {}
        except Exception as ex:
            logger.error(" ************ exception on call list assets: %s" % str(ex))
            assets = []

        iam_assets = []
        iam_content_type = asset_v1p5beta1.ContentType.IAM_POLICY
        if resource_type in IAM_TYPE:
            try:
                request['content_type'] = iam_content_type
                response = self.client.list_assets(request=request)
                response_dict = MessageToDict(response._pb)
                iam_assets = response_dict.get("assets") or []
            except Exception as ex:
                logger.error("******* exception on call list assets for iam policy: %s" % str(ex))
                iam_assets = []

        for resource in assets:
            current_resource_type = ASSET_TYPES[resource["assetType"]]
            resource_type_plural = (
                f"{resource_type}s" if resource_type in PLURAL_RESOURCE_TYPE_LIST else resource_type
            )
            if resource_type == 'network':
                resource_data = resource['resource']['data']
                resource_name_split = resource_data.get('network', resource_data.get('selfLink')).split('/')
            else:
                resource_name_split = resource["name"].split("/")
            try:
                current_resource_name = resource_name_split[
                    resource_name_split.index(resource_type_plural) + 1
                    ]
            except Exception as ex:
                logger.warning("Error fetching resource network %s " % str(ex))
                current_resource_name = ""

            if resource_type != current_resource_type:
                resource[f"{resource_type}_name"] = current_resource_name

            if current_resource_type == "pods" and resource['resource']['data']['status']['phase'] not in POD_STATUS:
                continue

            if resource_type in IAM_TYPE:
                iam = [item for item in iam_assets if item['name'] == resource['name']]
                resource['iamPolicy'] = iam[0]['iamPolicy'] if len(iam) > 0 else {}

            existing_resources = resources.get(current_resource_type) or []
            existing_resources.append(resource)
            resources[current_resource_type] = existing_resources

        if response_dict:
            next_page_token = response_dict.get("nextPageToken")
        return resources, next_page_token
