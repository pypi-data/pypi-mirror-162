# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger
import botocore

logger = get_logger()


class AwsDax(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        super().__init__(**kwargs, client_type="dax")
        self.dax = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        try:
            response = self.conn.describe_clusters()
            resources = response.get("Clusters", {})
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error getting cluster {e}")
            return []
        return [{**resource, "type": "dax"} for resource in resources]

    def get_resources(self) -> Any:
        """
        Fetches dax details.
        """

        dax = {**self.dax}

        return dax


def register() -> Any:
    factory.register("dax", AwsDax)
