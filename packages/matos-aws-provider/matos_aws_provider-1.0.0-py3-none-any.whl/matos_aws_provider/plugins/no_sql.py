# -*- coding: utf-8 -*-
from matos_aws_provider.lib import factory
from typing import Dict, Any
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsDynamoDB(BaseProvider):
    def __init__(
        self,
        resource: Dict,
        **kwargs,
    ) -> None:
        """ """
        super().__init__(**kwargs, client_type="dynamodb")

        try:
            self.application_autoscaling = self.client("application-autoscaling")
            self.ddb = resource

        except Exception as ex:
            logger.error(ex)

    def get_inventory(self) -> Any:
        response = self.conn.list_tables()
        dynamodbs = [
            {"name": item, "type": "no_sql"} for item in response.get("TableNames", [])
        ]
        return dynamodbs

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        dynamo_db = {
            **self.conn.describe_table(TableName=self.ddb.get("name")).get("Table", {}),
            "TableAutoScalingDescription": self.get_table_replica_auto_scaling(),
            "ContinuousBackupsDescription": self.get_continuous_backups(),
            "ScalableTargets": self.get_autoscaling_scalable_targets(),
            "type": "no_sql",
        }

        return dynamo_db

    def get_table_replica_auto_scaling(self):
        try:
            resp = self.conn.describe_table_replica_auto_scaling(
                TableName=self.ddb.get("name")
            )
        except Exception as ex:
            logger.error(f"{ex} ==== no sql auto scaling")
            resp = {}
        return resp.get("TableAutoScalingDescription")

    def get_continuous_backups(self):
        try:
            resp = self.conn.describe_continuous_backups(TableName=self.ddb.get("name"))
        except Exception as ex:
            logger.error(f"{ex} ===== no sql continuous backups")
            resp = {}
        return resp.get("ContinuousBackupsDescription")

    def get_autoscaling_scalable_targets(self):
        try:
            resp = self.application_autoscaling.describe_scalable_targets(
                ServiceNamespace="dynamodb",
                ResourceIds=self.get_autoscaling_resources(),
            )
        except Exception as ex:
            logger.error(f" {ex} ===== no sql continuous backups")
            resp = {}
        return resp.get("ScalableTargets", [])

    def get_autoscaling_resources(self):
        resources = [f"table/{self.ddb.get('name')}"]
        for index in self.ddb.get("GlobalSecondaryIndexes"):
            resources.append(f"table/{self.ddb.get('name')}/{index['IndexName']}")
        return resources


def register() -> None:
    factory.register("no_sql", AwsDynamoDB)
