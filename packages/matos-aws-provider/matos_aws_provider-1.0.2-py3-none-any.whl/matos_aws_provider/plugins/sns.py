# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsSNS(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct SNS service
        """

        super().__init__(**kwargs, client_type="sns")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        topics = []

        def list_topics(topics, next_token=None):
            if next_token:
                response = self.conn.list_topics(NextToken=next_token)
            else:
                response = self.conn.list_topics()
            topics += [{**item, "type": "sns"} for item in response.get("Topics", [])]
            if "NextToken" in response:
                list_topics(topics, response["NextToken"])

        list_topics(topics)
        return topics

    def get_resources(self) -> Any:
        """
        Fetches sns details.
        """

        resource = {**self.resource}
        resource["TopicAttributes"] = self.get_topic_attributes(
            self.resource["TopicArn"]
        )
        resource["TopicSubscriptions"] = self.list_subscriptions_by_topic(
            self.resource["TopicArn"]
        )
        for subscription in resource.get("TopicSubscriptions", []):
            subscription["SubscriptionAttributes"] = self.get_subscription_attributes(
                subscription["SubscriptionArn"]
            )

        return resource

    def get_topic_attributes(self, topic_arn):
        response = self.conn.get_topic_attributes(TopicArn=topic_arn)
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("Attributes")

    def list_subscriptions_by_topic(self, topic_arn):
        response = self.conn.list_subscriptions_by_topic(TopicArn=topic_arn)
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("Subscriptions", [])

    def get_subscription_attributes(self, subscription_arn):
        response = self.conn.get_subscription_attributes(
            SubscriptionArn=subscription_arn
        )
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("Attributes", [])


def register() -> Any:
    factory.register("sns", AwsSNS)
