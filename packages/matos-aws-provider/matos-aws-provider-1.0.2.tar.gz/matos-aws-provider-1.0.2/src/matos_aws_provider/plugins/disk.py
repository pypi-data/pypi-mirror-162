# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsDisk(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        super().__init__(**kwargs, client_type="ec2")
        self.disk = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.describe_volumes()
        volumes = [{**item, "type": "disk"} for item in response.get("Volumes", [])]
        return volumes

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        disk = {
            **self.disk,
        }

        return disk


def register() -> Any:
    factory.register("disk", AwsDisk)
