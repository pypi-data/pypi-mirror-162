# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsDocdb(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct Docdb service
        """
        self.resource = resource
        super().__init__(**kwargs, client_type="docdb")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.describe_db_clusters()
        return [{**item, "type": "docdb"} for item in response.get("DBClusters", [])]

    def get_resources(self) -> Any:
        """
        Fetches doc db details.
        """
        Parameters = self.conn.describe_db_cluster_parameters(
            DBClusterParameterGroupName=self.resource.get("DBClusterParameterGroup")
        ).get("Parameters")
        DBClusterSnapshots = self.conn.describe_db_cluster_snapshots(
            DBClusterIdentifier=self.resource.get("DBClusterIdentifier")
        ).get("DBClusterSnapshots")
        finalSnapshots = []
        try:
            for snapshot in DBClusterSnapshots:
                snapshotAttribute = self.conn.describe_db_cluster_snapshot_attributes(
                    DBClusterSnapshotIdentifier=snapshot.get(
                        "DBClusterSnapshotIdentifier"
                    )
                ).get("DBClusterSnapshotAttributesResult")
                finalSnapshots.append(
                    {
                        **snapshot,
                        "DBClusterSnapshotAttributes": snapshotAttribute.get(
                            "DBClusterSnapshotAttributes"
                        ),
                    }
                )
        except Exception as e:
            logger.error(f"error describe db cluster snapshot {e}")
            finalSnapshots = []

        resource = {
            **self.resource,
            "Parameters": Parameters,
            "DBClusterSnapshots": finalSnapshots,
        }
        return resource


def register() -> Any:
    factory.register("docdb", AwsDocdb)
