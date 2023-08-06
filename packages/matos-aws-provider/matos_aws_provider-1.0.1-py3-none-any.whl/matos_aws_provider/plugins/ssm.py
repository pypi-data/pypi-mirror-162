# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsSSM(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct SSM service
        """

        super().__init__(**kwargs, client_type="ssm")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_documents(
            Filters=[{"Key": "Owner", "Values": ["Self"]}]
        )
        return [
            {**item, "type": "ssm"} for item in response.get("DocumentIdentifiers", [])
        ]

    def get_resources(self) -> Any:
        """
        Fetches ssm details.
        """

        resource = {**self.resource}
        resource["shared_permissions"] = self.describe_document_permission(
            self.resource["Name"]
        )
        return resource

    def describe_document_permission(self, document_name, permission_type="Share"):
        response = self.conn.describe_document_permission(
            Name=document_name,
            PermissionType=permission_type,
        )
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response


def register() -> Any:
    factory.register("ssm", AwsSSM)
