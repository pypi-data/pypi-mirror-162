# -*- coding: utf-8 -*-
from matos_azure_provider.lib import factory
from typing import Any, Dict
from matos_azure_provider.lib.base_provider import BaseProvider


class AzureSql(BaseProvider):

    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct storage service
        """

        self.resource = resource
        super().__init__(**kwargs, client_type="sql")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """
        resources = [item.as_dict() for item in self.conn.servers.list()]
        resources = [{"type": 'sql', 'name': resource['name']} for resource in resources]
        return resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.
        Args:
        None
        return: dictionary object.
        """
        resource = None
        for item in self.conn.servers.list():
            objitem = self.scrub(item)
            if objitem.get('name', '') == self.resource.get('name'):
                obj_rg_name = objitem['id'].split('/')[-5]
                obj_name = objitem['name']
                sqlbdlist = []
                for sqldbitem in self.conn.databases.list_by_server(obj_rg_name, obj_name):
                    sqldb = self.scrub(sqldbitem)
                    sqldb["Bckup_retention_policies"] = [self.scrub(sqldbbkitem) for sqldbbkitem in
                                                         self.conn.backup_short_term_retention_policies.list_by_database(
                                                             obj_rg_name, obj_name, sqldb["name"])]
                    sqlbdlist.append(sqldb)
                objitem["Firewall_rules"] = [self.scrub(fwitem) for fwitem in
                                             self.conn.firewall_rules.list_by_server(obj_rg_name, obj_name)]
                objitem["failover_groups"] = [self.scrub(fgitem) for fgitem in
                                              self.conn.failover_groups.list_by_server(obj_rg_name, obj_name)]
                objitem["Databases"] = sqlbdlist
                resource = objitem
            # sqllist.append(objitem)

        # resources = [self.scrub(item) for item in self.conn.servers.list()]
        # resources = [resource for resource in resources if resource.get('name', '') == self.resource.get('name')]
        return resource if resource else self.resource


def register() -> Any:
    factory.register("sql", AzureSql)
