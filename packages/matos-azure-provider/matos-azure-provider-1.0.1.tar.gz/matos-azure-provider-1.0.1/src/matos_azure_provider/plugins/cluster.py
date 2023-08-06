# -*- coding: utf-8 -*-
from matos_azure_provider.lib import factory
from typing import Any, Dict
from matos_azure_provider.lib.base_provider import BaseProvider
from datetime import datetime
import yaml
import ruamel.yaml
from kubernetes import client as kclient, config as kconfig
import base64


class AzureCluster(BaseProvider):

    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        self.resource = resource
        super().__init__(**kwargs, client_type="cluster")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = [item.as_dict() for item in self.conn.managed_clusters.list()]
        resources = [
            {
                "type": 'cluster',
                'name': resource['name'],
                "location": resource['location']
            } for resource in resources]
        return resources

    def replace_none_with(self, d, replacement=0):
        retval = {}
        for key, val in d.items():
            if val is None:
                retval[key] = replacement
            elif isinstance(val, dict):
                retval[key] = self.replace_none_with(val, replacement)
            elif isinstance(val, datetime):
                retval[key] = val.strftime("%m/%d/%Y, %H:%M:%S")
            elif isinstance(val, list):
                emtlist = []
                for lt in val:
                    if isinstance(lt, dict):
                        emtlist.append(self.replace_none_with(lt, replacement))
                retval[key] = emtlist
            else:
                retval[key] = val
        return retval

    def get_resources(self) -> Any:
        """
        Fetches cluster details.

        Args:
        cluster_name: name of the eks instance.

        return: dictionary object.
        """
        cluster_details = self.get_cluster_details()
        return cluster_details

    def get_cluster_client(self, cluster_info):
        rg_name = cluster_info.get('id', '').split('/')[-5]
        k8s_name = cluster_info.get('name')
        kubeconfig = self.conn.managed_clusters.list_cluster_admin_credentials(rg_name, k8s_name).kubeconfigs[0]
        k8s_kubeconfig = base64.b64decode((kubeconfig.as_dict())['value'])
        obj_data = ruamel.yaml.safe_load(k8s_kubeconfig)
        with open(f'{k8s_name}.yml', 'w') as f:
            yaml.dump(obj_data, f)
        kube_client = kconfig.load_kube_config(f'{k8s_name}.yml')
        k8s_client = kclient.ApiClient(kube_client)
        k8s_client_v1 = kclient.CoreV1Api(k8s_client)

        return k8s_client_v1

    def get_cluster_details(self):
        resources = [self.scrub(item) for item in self.conn.managed_clusters.list()]
        resources = [{
            **resource,
            "pod": self.replace_none_with(
                self.get_cluster_client(resource).list_pod_for_all_namespaces().to_dict(),
                replacement='None').get('items', []),
            "service": self.replace_none_with(
                self.get_cluster_client(resource).list_service_for_all_namespaces().to_dict(),
                replacement='None').get('items', []),
        } for resource in resources if resource.get('name', '') == self.resource.get('name')]
        return resources[0] if len(resources) > 0 else self.resource


def register() -> Any:
    factory.register("cluster", AzureCluster)
