# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsRedshift(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct redshift service
        """

        super().__init__(**kwargs, client_type="redshift")
        self.redshift = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.describe_clusters()
        return [{**item, "type": "redshift"} for item in response.get("Clusters", [])]

    def get_resources(self) -> Any:
        """
        Fetches redshift clusters
        Args:
        return: dictionary object.
        """
        redshift = {**self.redshift}
        redshift["ParameterGroups"] = self.describe_cluster_parameters(
            parameter_group_name=redshift.get("ClusterParameterGroups")[0].get(
                "ParameterGroupName"
            )
        ).get("Parameters")
        redshift["LoggingEnabled"] = self.get_logging_status(
            self.redshift.get("ClusterIdentifier")
        )
        return redshift

    def describe_cluster_parameters(self, parameter_group_name):
        return self.conn.describe_cluster_parameters(
            ParameterGroupName=parameter_group_name
        )

    def get_logging_status(self, cluster_identifier):
        return self.conn.describe_logging_status(
            ClusterIdentifier=cluster_identifier
        ).get("LoggingEnabled")


def register() -> Any:
    factory.register("redshift", AwsRedshift)
