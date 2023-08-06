# -*- coding: utf-8 -*-
import os
import json
from azure.identity import ClientSecretCredential
from matos_azure_provider.config import AZURE_CLIENT_MANAGER
from matos_azure_provider.lib.log import get_logger

logger = get_logger()


class Connection:
    def __init__(self,
                 **kwargs) -> None:

        svc_account_filename = "azure_account.json"
        azure_svc_account_path = os.getenv("AZURE_SVC_ACCOUNT_PATH", "credentials")
        self._azure_svc_account_file = os.path.join(azure_svc_account_path, svc_account_filename)
        try:
            azure_credentials = json.load(open(self._azure_svc_account_file))
        except Exception as ex:
            AZURE_CRED_EXCEPTION = "Not found account service json for Azure - credentials/azure_account.json"
            logger.error(AZURE_CRED_EXCEPTION + str(ex))
            return

        self.tenant_id = azure_credentials.get("tenantId", "")
        self.client_id = azure_credentials.get("clientId", "")
        self.client_secret = azure_credentials.get("clientSecret", "")
        self.subscription_id = azure_credentials.get("subscription_id", "")
        self._credential = None

    def client(self, service_name: str):
        """"""
        client_class = AZURE_CLIENT_MANAGER.get(service_name, None)
        return client_class(self.credential, self.subscription_id) if client_class else None

    @property
    def credential(self):
        if not self._credential:
            self._credential = ClientSecretCredential(
                client_id=self.client_id,
                client_secret=self.client_secret,
                tenant_id=self.tenant_id)
        return self._credential

    def scrub(self, x):
        org = x.as_dict()
        backup = vars(x)
        for k in backup:
            if backup[k] is None:
                backup[k] = 'None'
            elif k in org.keys():
                backup[k] = org[k]
        return backup
