import unittest

from matos_azure_provider.provider import Provider


class TestDiscoveryPlugin(unittest.TestCase):
    def setUp(self):

        self.service_type_map = {
            "cluster": "cluster",
            "instance": "instance",
            "network": "network",
            "sql": "sql"
        }

    def test_check_plugins_type_pass(self):
        provider = Provider()
        for key_type, client_type in self.service_type_map.items():
            discovery_service = provider.service_factory.create(
                {"type": key_type}
            )
            self.assertEqual(discovery_service.client_type, client_type)


if __name__ == "__main__":
    unittest.main()
