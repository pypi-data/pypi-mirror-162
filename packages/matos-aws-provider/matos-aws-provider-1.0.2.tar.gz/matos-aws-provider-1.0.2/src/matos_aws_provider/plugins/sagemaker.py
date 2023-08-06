# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsSagemaker(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        super().__init__(**kwargs, client_type="sagemaker")
        self.sagemaker_instance = resource

    def get_inventory(self) -> Any:
        """ """

        resources = self.conn.list_notebook_instances().get("NotebookInstances")
        resources = [{**resource, "type": "sagemaker"} for resource in resources]
        return resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        sagemaker_instance = None
        if self.sagemaker_instance.get("NotebookInstanceName") is not None:
            sagemaker_instance = {
                **self.sagemaker_instance,
                **self.describe_notebook_instance(
                    self.sagemaker_instance.get("NotebookInstanceName")
                ),
            }

        return sagemaker_instance

    def describe_notebook_instance(self, instance_name):
        resp = self.conn.describe_notebook_instance(NotebookInstanceName=instance_name)
        if "ResponseMetadata" in resp:
            del resp["ResponseMetadata"]
        return resp


def register() -> None:
    factory.register("sagemaker", AwsSagemaker)
