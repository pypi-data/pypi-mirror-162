# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsSecurityHub(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct security hub service
        """

        super().__init__(**kwargs, client_type="securityhub")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        hub = []

        def getSecurityHub(hub, next_token=None):
            try:
                if next_token:
                    response = self.conn.describe_hub(NextToken=next_token)
                else:
                    response = self.conn.describe_hub()
                hub += [{**response, "type": "securityhub"}]
                if "NextToken" in response:
                    getSecurityHub(hub, response["NextToken"])
            except Exception as ex:
                logger.error(f"Error {ex}")
                hub = []  # security hub not enabled.

        getSecurityHub(hub)
        return hub

    def get_resources(self) -> Any:
        """
        Fetches securityhub details.
        """

        return {
            "AutoEnableControls": self.resource.get("AutoEnableControls"),
            "HubArn": self.resource.get("HubArn"),
            "SubscribedAt": self.resource.get("SubscribedAt"),
            "type": self.resource.get("type"),
        }


def register() -> Any:
    factory.register("securityhub", AwsSecurityHub)
