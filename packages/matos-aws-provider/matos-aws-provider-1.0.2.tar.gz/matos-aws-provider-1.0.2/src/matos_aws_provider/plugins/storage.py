# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger
import botocore

logger = get_logger()


class AwsStorage(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        super().__init__(**kwargs, client_type="s3")
        self.bucket = resource

    def get_inventory(self) -> Any:
        """ """

        buckets = self.conn.list_buckets()
        owner = buckets["Owner"]

        bucket_resources = []
        for bucket in buckets["Buckets"]:
            detail = {
                "name": bucket.get("Name", ""),
                "type": "storage",
                "creationDate": bucket.get("CreationDate", ""),
                "owner": {
                    "displayName": owner.get("DisplayName", ""),
                    "id": owner.get("ID", ""),
                },
            }
            bucket_resources.append(detail)
        return bucket_resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        self.bucket = {
            **self.bucket,
            "type": "bucket",
            "policy": self.get_bucket_policy_list(),
            "metric_configuration": self.get_bucket_metrics_configuration_list(),
            "inventory_configuration": self.get_bucket_inventory_configuration_list(),
            "intelligent_tiering_configuration": self.get_bucket_intelligent_tiering_configurations_list(),
            "acl": self.get_bucket_acl(),
            "policy_status": self.get_bucket_policy_status(),
            # "object": self.get_object_list(),
            "lifecycle": self.get_bucket_lifecycle(),
            "encryption": self.get_bucket_encryption(),
            "versioning": self.get_bucket_versioning(),
            "tagging": self.get_bucket_tagging(),
            "location": self.get_bucket_location(),
            "logging": self.get_bucket_logging(),
            "public_access_block": self.get_bucket_public_access_block(),
            "ownership": self.get_bucket_ownership(),
            "notification": self.get_bucket_notification_configuration(),
            "replicationConfiguration": self.get_bucket_replication(),
        }
        return self.bucket

    def get_bucket_replication(self):
        try:
            replication = self.conn.get_bucket_replication(
                Bucket=self.bucket.get("name")
            ).get("ReplicationConfiguration")
        except Exception as ex:
            logger.warning(f"{ex} ======= fetch bucket replication")
            replication = None
        return replication

    def get_bucket_notification_configuration(self):
        try:
            resp = self.conn.get_bucket_notification_configuration(
                Bucket=self.bucket.get("name")
            )
            del resp["ResponseMetadata"]
            return resp
        except botocore.exceptions.ClientError as e:
            logger.warning(f"error {e}")
            return {}

    def get_bucket_policy_list(self):
        bucket_name = self.bucket["name"]
        try:
            policies = self.conn.get_bucket_policy(Bucket=bucket_name)
            policy = policies["Policy"]
        except Exception as ex:
            logger.error(f"{bucket_name} policy error: {ex}")
            policy = {}

        return policy

    def get_bucket_ownership(self):
        bucket_name = self.bucket["name"]
        try:
            ownership = self.conn.get_bucket_ownership_controls(Bucket=bucket_name)
            rules = ownership["OwnershipControls"]["Rules"]
        except Exception as ex:
            logger.error(f"{bucket_name} Ownership controls error: {ex}")
            rules = []

        return rules

    def get_bucket_public_access_block(self):
        bucket_name = self.bucket["name"]
        try:
            resp = self.conn.get_public_access_block(Bucket=bucket_name)
            publicAccessBlock = resp.get("PublicAccessBlockConfiguration", {})
        except Exception as ex:
            logger.error(f"{bucket_name} public access block error: {ex}")
            publicAccessBlock = {}

        return publicAccessBlock

    def get_bucket_location(self):
        bucket_name = self.bucket["name"]
        try:
            resp = self.conn.get_bucket_location(Bucket=bucket_name)
            location = resp["LocationConstraint"]
        except Exception as ex:
            logger.error(f"{bucket_name} location getting error: {ex}")
            location = ""

        return location

    def fetch_metric_config(self, metrics=None, continuationToken: str = None):
        request = {
            "Bucket": self.bucket["name"],
            # "ExpectedBucketOwner": self.bucket['owner']['id']
        }
        if continuationToken:
            request["ContinuationToken"] = continuationToken
        response = self.conn.list_bucket_metrics_configurations(**request)
        nextContinuationToken = response.get("NextContinuationToken", None)
        current_metrics = [] if not metrics else metrics
        current_metrics.extend(response.get("MetricsConfigurationList", []))

        return current_metrics, nextContinuationToken

    def get_bucket_metrics_configuration_list(self):
        try:
            metrics, nextContinuationToken = self.fetch_metric_config()

            while nextContinuationToken:
                metrics, nextContinuationToken = self.fetch_metric_config(
                    metrics, nextContinuationToken
                )

        except Exception as ex:
            logger.error(f"{self.bucket['name']} metric configuration: {ex}")
            return []

        return metrics

    def fetch_inventory_config(self, metrics=None, continuationToken: str = None):
        request = {
            "Bucket": self.bucket["name"],
            # "ExpectedBucketOwner": self.bucket['owner']['id']
        }
        if continuationToken:
            request["ContinuationToken"] = continuationToken
        response = self.conn.list_bucket_inventory_configurations(**request)
        nextContinuationToken = response.get("NextContinuationToken", None)
        current_inventories = [] if not metrics else metrics
        current_inventories.extend(response.get("InventoryConfigurationList", []))

        return current_inventories, nextContinuationToken

    def get_bucket_inventory_configuration_list(self):
        try:
            inventories, nextContinuationToken = self.fetch_inventory_config()

            while nextContinuationToken:
                inventories, nextContinuationToken = self.fetch_inventory_config(
                    inventories, nextContinuationToken
                )

        except Exception as ex:
            logger.warning(f"{self.bucket['name']} inventory configuration: {ex}")
            return []

        return inventories

    def fetch_intelligent_tiering_config(
        self, tierings=None, continuationToken: str = None
    ):
        request = {
            "Bucket": self.bucket["name"],
            # "ExpectedBucketOwner": self.bucket['owner']['id']
        }
        if continuationToken:
            request["ContinuationToken"] = continuationToken
        response = self.conn.list_bucket_inventory_configurations(**request)
        nextContinuationToken = response.get("NextContinuationToken", None)
        current_tierings = [] if not tierings else tierings
        current_tierings.extend(response.get("IntelligentTieringConfigurationList", []))

        return current_tierings, nextContinuationToken

    def get_bucket_intelligent_tiering_configurations_list(self):
        try:
            tiering, nextContinuationToken = self.fetch_intelligent_tiering_config()

            while nextContinuationToken:
                tiering, nextContinuationToken = self.fetch_intelligent_tiering_config(
                    tiering, nextContinuationToken
                )

        except Exception as ex:
            logger.error(f"{self.bucket['name']} intelligent tiering configuration: {ex}")
            return []

        return tiering

    def get_bucket_acl(self):
        try:
            response = self.conn.get_bucket_acl(Bucket=self.bucket["name"])
            del response["ResponseMetadata"]
        except Exception as ex:
            logger.error(f"{self.bucket['name']} bucket ACL: {ex}")
            response = {}
        return response

    def get_bucket_encryption(self):
        try:
            response = self.conn.get_bucket_encryption(Bucket=self.bucket["name"])
            del response["ResponseMetadata"]
        except Exception as ex:
            logger.error(f"{self.bucket['name']} bucket encryption: {ex}")
            response = {}
        return response

    def get_bucket_versioning(self):
        try:
            response = self.conn.get_bucket_versioning(Bucket=self.bucket["name"])
            del response["ResponseMetadata"]
        except Exception as ex:
            logger.error(f"{self.bucket['name']} bucket versioning: {ex}")
            response = {}
        return response

    def get_bucket_tagging(self):
        try:
            response = self.conn.get_bucket_tagging(Bucket=self.bucket["name"])
            del response["ResponseMetadata"]
        except Exception as ex:
            logger.error(f"{self.bucket['name']} bucket tagging: {ex}")
            response = {}
        return response

    def get_bucket_policy_status(self):
        try:
            response = self.conn.get_bucket_policy_status(Bucket=self.bucket["name"])
            del response["ResponseMetadata"]
        except Exception as ex:
            logger.error(f"{self.bucket['name']} policy status: {ex}")
            response = {}
        return response

    def get_object_acl(self, key):
        try:
            response = self.conn.get_object_acl(Bucket=self.bucket["name"], Key=key)
        except Exception as ex:
            logger.warning(f"{self.bucket['name']} object acl: {ex}")
            response = {}
        return response

    def get_object_list(self):
        try:
            response = self.conn.list_objects(Bucket=self.bucket["name"])
        except Exception as ex:
            logger.error(f"{self.bucket['name']} object list: {ex}")
            response = {}
        object_list = response.get("Contents", [])
        objects = []
        for object in object_list:
            object_acl = self.get_object_acl(object["Key"])
            del object_acl["ResponseMetadata"]
            objects.append({**object, "Acl": object_acl})
        return objects

    def get_bucket_lifecycle(self):
        try:
            response = self.conn.get_bucket_lifecycle(Bucket=self.bucket["name"])
        except Exception as ex:
            logger.error(f"{self.bucket['name']} bucket lifecycle: {ex}")
            response = {}
        return response

    def get_bucket_logging(self):
        try:
            response = self.conn.get_bucket_logging(Bucket=self.bucket["name"])
        except Exception as ex:
            logger.warning(f"{self.bucket['name']} bucket logging: {ex}")
            response = {}
        return response.get("LoggingEnabled")


def register() -> None:
    factory.register("storage", AwsStorage)
