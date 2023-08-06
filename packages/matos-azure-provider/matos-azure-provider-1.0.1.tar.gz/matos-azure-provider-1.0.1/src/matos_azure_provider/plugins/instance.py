# -*- coding: utf-8 -*-
from matos_azure_provider.lib import factory
from typing import Any, Dict
from matos_azure_provider.lib.base_provider import BaseProvider


class AzureInstance(BaseProvider):

    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct instance service
        """

        self.resource = resource
        super().__init__(**kwargs, client_type="instance")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """
        resources = [item.as_dict() for item in self.conn.virtual_machines.list_all()]
        resources = [{"type": 'instance', 'name': resource['name']} for resource in resources]
        return resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        None
        return: dictionary object.
        """
        resources = [self.scrub(item) for item in self.conn.virtual_machines.list_all()]
        resources = [resource for resource in resources if resource.get('name', '') == self.resource.get('name')]
        return resources[0] if len(resources) > 0 else self.resource


def register() -> Any:
    factory.register("instance", AzureInstance)
