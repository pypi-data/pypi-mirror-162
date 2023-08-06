# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest

from matos_azure_provider.lib import loader, factory
from matos_azure_provider.plugins import get_package
from matos_azure_provider.plugins.cluster import AzureCluster
from matos_azure_provider.plugins.instance import AzureInstance
from matos_azure_provider.plugins.storage import AzureStorage
from matos_azure_provider.plugins.network import AzureNetwork
from matos_azure_provider.plugins.sql import AzureSql
from matos_azure_provider.provider import Provider


class TestResourcePlugin(unittest.TestCase):
    def setUp(self):
        self.resource_types = {
            "cluster": AzureCluster,
            "instance": AzureInstance,
            "storage": AzureStorage,
            "network": AzureNetwork,
            "sql": AzureSql
        }

    def test_get_plugins_pass(self):
        provider = Provider()
        plugin_map = provider.service_factory.fetch_plugins()
        for key, obj_register in self.resource_types.items():
            self.assertEqual(obj_register, plugin_map.get(key))

    def test_fetch_plugins_with_exception(self):
        loader.load_plugins(get_package())
        with self.assertRaises(ValueError):
            factory.create({"type": "1234"})


if __name__ == "__main__":
    unittest.main()
