# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsCloudFront(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloud front service
        """

        super().__init__(**kwargs, client_type="cloudfront")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_distributions()
        return [
            {**item, "type": "cloudfront"}
            for item in response.get("DistributionList", {}).get("Items", [])
        ]

    def get_resources(self) -> Any:
        """
        Fetches cloudfront details.
        """

        resource = {**self.resource, **self.get_distribution(self.resource["Id"])}

        return resource

    def get_distribution(self, distribution_id):
        response = self.conn.get_distribution(Id=distribution_id)
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("Distribution", {})


def register() -> Any:
    factory.register("cloudfront", AwsCloudFront)
