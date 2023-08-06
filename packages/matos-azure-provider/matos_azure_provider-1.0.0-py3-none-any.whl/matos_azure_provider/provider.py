from matos_azure_provider.lib.auth import Connection
from matos_azure_provider.plugins import get_package
from matos_azure_provider.lib import factory, loader
from matos_azure_provider.lib.log import get_logger
from typing import List, Any
import threading

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

        def fetch_discovery_details(rsc_type):
            service_discovery = self.service_factory.create({"type": rsc_type})
            result = service_discovery.get_inventory()

            if result is None:
                return

            lock.acquire()
            if isinstance(result, list):
                resources.extend(service_discovery.get_inventory())
            else:
                resources.append(service_discovery.get_inventory())
            lock.release()

        service_map = self.service_factory.fetch_plugins()
        for rsc_type in service_map.keys():
            thread = threading.Thread(target=fetch_discovery_details, args=(rsc_type,))
            thread.start()
            threads.append(thread)

        for t in threads:
            t.join()

        return resources

    def get_resource_inventories(self, resource_list: List[Any]):
        """
        Get resources data
        """
        resource_inventories = {}
        lock = threading.Lock()

        def fetch_resource_details(rsc):
            type = rsc.get('type')

            try:
                detail = self._get_assets_inventory(rsc)
                lock.acquire()
                resource_inventories[type] = [detail] if type not in resource_inventories \
                    else [*resource_inventories[type], detail]
                lock.release()
            except Exception as e:
                logger.error(f"{e}")

        threads = []
        for resource in resource_list:
            thread = threading.Thread(target=fetch_resource_details, args=(resource,))
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()
        return resource_inventories

    def _get_assets_inventory(self, resource, **kwargs):
        cloud_resource = self.service_factory.create(resource)
        resource_details = cloud_resource.get_resources()
        if resource_details:
            resource.update(details=resource_details)
        return resource
