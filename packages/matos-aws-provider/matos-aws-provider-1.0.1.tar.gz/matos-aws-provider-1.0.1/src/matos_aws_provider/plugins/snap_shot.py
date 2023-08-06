# -*- coding: utf-8 -*-
from typing import Any, Dict
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsSnapshot(BaseProvider):
    """ Aws snap shot service

    Args:
        BaseProvider (BaseProvider): base provider class
    """
    def __init__(self, resource: Dict, **kwargs) -> None:
        """Construct cloudtrail service

        Args:
            resource (Dict): resource dict
        """

        super().__init__(**kwargs, client_type="iam")
        self.ec2 = self.client("ec2")
        self.snapshot = resource

    def get_inventory(self) -> Any:
        user = self.conn.list_users().get("Users", [])[0]
        owner_id = user.get("Arn").split(":")[-2]
        response = self.ec2.describe_snapshots(
            Filters=[
                {
                    "Name": "owner-id",
                    "Values": [
                        owner_id,
                    ],
                },
            ],
        )
        snapshots = [
            {**item, "type": "snapshot"} for item in response.get("Snapshots", [])
        ]
        return snapshots

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        snapshot = {
            **self.snapshot,
        }
        return snapshot


def register() -> None:
    """ register class """
    factory.register("snapshot", AwsSnapshot)
