# -*- coding: utf-8 -*-
from typing import Any, Dict
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsAnalyzer(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        super().__init__(**kwargs, client_type="accessanalyzer")
        self.analyzer = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = self.conn.list_analyzers().get("analyzers")
        resources = [{**resource, "type": "analyzer"} for resource in resources]
        resources = resources if resources else [{"type": "analyzer", "empty": True}]
        return resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        analyzer = {**self.analyzer}
        return analyzer


def register() -> Any:
    """Register class method

    Returns:
        Any: register class
    """
    factory.register("analyzer", AwsAnalyzer)
