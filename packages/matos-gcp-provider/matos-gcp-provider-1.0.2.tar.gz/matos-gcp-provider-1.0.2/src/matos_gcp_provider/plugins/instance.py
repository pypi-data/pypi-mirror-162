# -*- coding: utf-8 -*-
from matos_gcp_provider.lib import factory
from typing import Any, Dict
from matos_gcp_provider.lib.base_provider import BaseProvider
from ..config import ASSET_TYPES

INVERTED_TYPES = {x: y for y, x in ASSET_TYPES.items()}


class GCPInstance(BaseProvider):

    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct instance service
        """

        self.resource = resource
        self.resource_type = "instance"
        self.project_id = resource.pop("project_id")
        super().__init__(**kwargs)

    def get_inventory(self) -> Any:
        """
        Service discovery
        """
        resources = self._get_assets(self.project_id, INVERTED_TYPES[self.resource_type])
        instances = []

        for resource in resources:
            instances.append({
                'type': 'instance',
                'name': resource['resource']['data']['name'],
                'instance_id': resource['resource']['data']['id'],
                'project_id': self.project_id,
                'location': resource['resource']['data']['zone'].split('/')[-1],
            })

        return instances


def register() -> Any:
    factory.register("instance", GCPInstance)
