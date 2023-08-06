# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsElasticsearch(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct elastic search service
        """
        self.es_domain = resource
        super().__init__(**kwargs, client_type="es")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = self.conn.list_domain_names().get("DomainNames")
        return [{**resource, "type": "elasticsearch"} for resource in resources]

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """

        resource = {
            **self.es_domain,
            **self.describe_elasticsearch_domain(self.es_domain.get("DomainName")),
        }

        return resource

    def describe_elasticsearch_domain(self, domain_name):
        resp = self.conn.describe_elasticsearch_domain(DomainName=domain_name)
        del resp["ResponseMetadata"]
        return resp.get("DomainStatus")


def register() -> Any:
    factory.register("elasticsearch", AwsElasticsearch)
