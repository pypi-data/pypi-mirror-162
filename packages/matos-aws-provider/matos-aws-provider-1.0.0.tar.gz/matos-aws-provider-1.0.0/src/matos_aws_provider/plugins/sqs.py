# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsSQS(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct api gateway service
        """

        super().__init__(**kwargs, client_type="sqs")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_queues()
        return [{"url": item, "type": "sqs"} for item in response.get("QueueUrls", [])]

    def get_resources(self) -> Any:
        """
        Fetches SQS details.
        """
        attributes = self.conn.get_queue_attributes(
            QueueUrl=self.resource.get("url"), AttributeNames=["All"]
        ).get("Attributes")
        resource = {
            **attributes,
            "url": self.resource.get("url"),
            "QueueName": attributes.get("QueueArn").split(":")[-1],
            "AccountId": attributes.get("QueueArn").split(":")[-2],
        }
        return resource


def register() -> Any:
    factory.register("sqs", AwsSQS)
