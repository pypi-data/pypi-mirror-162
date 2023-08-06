# -*- coding: utf-8 -*-
from typing import Any, Dict
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsApiGateway(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct api gateway service
        """

        super().__init__(**kwargs, client_type="apigatewayv2")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.get_apis()
        return [{**item, "type": "apigateway"} for item in response.get("Items", [])]

    def get_resources(self) -> Any:
        """
        Fetches api gateways details.
        """
        stages = self.conn.get_stages(ApiId=self.resource.get("ApiId")).get("Items")

        resource = {**self.resource, "stages": stages}

        return resource


def register() -> Any:
    """Register class method

    Returns:
        Any: register class
    """
    factory.register("apigateway", AwsApiGateway)
