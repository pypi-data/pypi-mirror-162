# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsOpenSearch(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct open search service
        """

        self.opensearch = resource
        super().__init__(**kwargs, client_type="opensearch")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_domain_names()
        return [
            {**item, "type": "opensearch"} for item in response.get("DomainNames", [])
        ]

    def get_resources(self) -> Any:
        """
        Fetches opensearch details

        Args:
        return: dictionary object.
        """
        opensearch = {**self.opensearch}
        DomainStatus = self.conn.describe_domain(
            DomainName=opensearch.get("DomainName")
        ).get("DomainStatus")
        return {**opensearch, "DomainStatus": DomainStatus}


def register() -> Any:
    factory.register("opensearch", AwsOpenSearch)
