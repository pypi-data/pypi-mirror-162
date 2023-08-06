# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
import botocore


class AwsS3Control(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct s3 control service
        """

        super().__init__(**kwargs, client_type="sts")
        self.s3control_con = self.client("s3control")
        self.s3control = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        caller_identity = self.conn.get_caller_identity()
        try:
            response = self.s3control_con.get_public_access_block(
                AccountId=caller_identity["Account"]
            )
            resources = response.get("PublicAccessBlockConfiguration", {})
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                resources = {
                    "BlockPublicAcls": False,
                    "BlockPublicPolicy": False,
                    "IgnorePublicAcls": False,
                    "RestrictPublicBuckets": False,
                }
        return [{**resources, "type": "s3control"}]

    def get_resources(self) -> Any:
        """
        Fetches s3control details.
        """

        s3control = {**self.s3control, "AccountId": self.get_account_id()}

        return s3control

    def get_account_id(self):
        return self.conn.get_caller_identity()["Account"]


def register() -> Any:
    factory.register("s3control", AwsS3Control)
