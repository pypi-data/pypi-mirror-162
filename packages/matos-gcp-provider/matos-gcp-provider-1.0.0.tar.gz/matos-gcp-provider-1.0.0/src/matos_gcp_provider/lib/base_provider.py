# -*- coding: utf-8 -*-
from typing import Any
from google.cloud import asset_v1p5beta1
from google.protobuf.json_format import MessageToDict
from matos_gcp_provider.lib.auth import Connection
from matos_gcp_provider.lib.log import get_logger


logger = get_logger()


class BaseProvider(Connection):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.content_type = asset_v1p5beta1.ContentType.RESOURCE

    def _get_assets(
            self,
            project_id: str,
            *asset_types,
    ):

        request = {
            "asset_types": asset_types,
            "parent": f"projects/{project_id}",
            "content_type": self.content_type
        }

        assets = []
        next_page_token = None

        while True:

            if next_page_token:
                request["page_token"] = next_page_token

            response = self.client.list_assets(request=request)
            response_dict = MessageToDict(response._pb)
            page_assets = response_dict.get("assets") or []
            assets.extend(page_assets)

            next_page_token = response_dict.get("nextPageToken")

            if not next_page_token:
                break

        return assets

    def get_inventory(self) -> Any:
        raise NotImplementedError
