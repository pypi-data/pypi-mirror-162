# -*- coding: utf-8 -*-
import botocore
import json
from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsCloudtrail(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        super().__init__(**kwargs, client_type="cloudtrail")
        try:
            self.logs = self.client("logs")
            self.watch = self.client("cloudwatch")
            self.s3 = self.client("s3")
            self.s3_control = self.client("s3control")
            self.sts = self.client("sts")
            self.trail = resource

        except Exception as ex:
            logger.error(ex)

    def get_inventory(self) -> Any:
        def fetch_cloudtrails(cloudtrail_list=None, continue_token: str = None):
            request = {}
            if continue_token:
                request["NextToken"] = continue_token
            response = self.conn.list_trails(**request)
            continue_token = response.get("NextToken", None)
            current_cloudtrails = [] if not cloudtrail_list else cloudtrail_list
            current_cloudtrails.extend(response.get("Trails", []))

            return current_cloudtrails, continue_token

        try:
            cloudtrails, nextToken = fetch_cloudtrails()

            while nextToken:
                cloudtrails = fetch_cloudtrails(cloudtrails, nextToken)
        except Exception as ex:
            logger.error(f"cloudtrail: {ex}")
            return []

        cloudtrail_resources = []
        for cloudtrail in cloudtrails:
            detail = {
                "name": cloudtrail.get("Name", ""),
                "arn": cloudtrail.get("TrailARN"),
                "region": cloudtrail.get("HomeRegion"),
                "type": "log_monitor",
            }
            cloudtrail_resources.append(detail)
        return cloudtrail_resources

    def get_resources(self) -> Any:
        """
        Fetches CloudTrail details.

        Args:
        return: dictionary object.
        """
        trail_arn = self.trail["arn"]
        response = self.conn.describe_trails(trailNameList=[trail_arn])
        trail_data = {"type": "cloudtrail", **response.get("trailList", [{}])[0]}
        log_group_arn = trail_data.get("CloudWatchLogsLogGroupArn")
        home_region = trail_data.get("HomeRegion")
        trail_data["event_selectors"] = self.get_trail_event_selector(trail_arn)
        if trail_data.get("S3BucketName"):
            trail_data["S3BucketLogging"] = self.get_s3_bucket_logging(
                trail_data.get("S3BucketName")
            )
            trail_data["S3PublicAccessBlock"] = self.get_s3_public_access_block(
                trail_data.get("S3BucketName")
            )
            trail_data["S3BucketPolicy"] = self.get_s3_bucket_policy(
                trail_data.get("S3BucketName")
            )
            trail_data["S3BucketACL"] = self.get_s3_bucket_acl(
                trail_data.get("S3BucketName")
            )
            account_id = self.sts.get_caller_identity()["Account"]
            trail_data["S3BucketAccessPoints"] = self.get_s3_bucket_access_points(
                account_id, trail_data.get("S3BucketName")
            )
            for access_point in trail_data["S3BucketAccessPoints"]:
                access_point_details = self.get_s3_access_point(
                    account_id, access_point["Name"]
                )
                access_point[
                    "PublicAccessBlockConfiguration"
                ] = access_point_details.get("PublicAccessBlockConfiguration")
                access_point["Policy"] = self.get_s3_access_point_policy(
                    account_id, access_point["Name"]
                )

        if log_group_arn:
            log_group = self.get_log_group(log_group_arn, home_region)
            log_group_name = log_group.get("logGroupName")
            if log_group_name:
                metric_filters = self.get_metric_filters(log_group_name)
                metric_filters = [
                    {
                        **metric,
                        "metricTransformations": [
                            {
                                **data,
                                "metricAlarms": self.get_alarms_for_metric(
                                    data.get("metricName"), data.get("metricNamespace")
                                ),
                            }
                            for data in metric.get("metricTransformations", [])
                        ],
                    }
                    for metric in metric_filters
                ]
                log_group["metricFilters"] = metric_filters
            trail_data["CloudWatchLogGroup"] = log_group

        return trail_data

    def get_log_group(self, arn, home_region):
        def fetch_log_group(log_list=None, continueToken=None):
            request = {}
            if continueToken:
                request["nextToken"] = continueToken
                request["Region"] = "us-east-1"
            self.logs = self.client("logs", region_name=home_region)
            response = self.logs.describe_log_groups(**request)
            continueToken = response.get("NextToken", None)
            current_logs = [] if not log_list else log_list
            current_logs.extend(response.get("logGroups", []))

            return current_logs, continueToken

        try:
            logs, nextToken = fetch_log_group()

            while nextToken:
                logs = fetch_log_group(logs, nextToken)
        except Exception as ex:
            logger.error(f"cloudwatchlogs log group: {ex}")
            return {}
        logs = [log for log in logs if log.get("arn") == arn]
        return logs[0] if logs else {}

    def get_metric_filters(self, logGroupName):
        def fetch_metric_filters(
            metric_filter_list=None, continueToken=None, name=None
        ):
            request = {}
            if continueToken:
                request["nextToken"] = continueToken
                request["logGroupName"] = name
            response = self.logs.describe_metric_filters(**request)
            continueToken = response.get("NextToken", None)
            current_metric_filters = (
                [] if not metric_filter_list else metric_filter_list
            )
            current_metric_filters.extend(response.get("metricFilters", []))

            return current_metric_filters, continueToken

        try:
            metric_filters, nextToken = fetch_metric_filters(name=logGroupName)

            while nextToken:
                metric_filters = fetch_metric_filters(
                    metric_filters, nextToken, logGroupName
                )
        except Exception as ex:
            logger.error(f"cloudwatchlogs log group metric filter: {ex}")
            return {}

        return metric_filters

    def get_alarms_for_metric(self, metricName, filterNamespace):
        response = self.watch.describe_alarms_for_metric(
            MetricName=metricName, Namespace=filterNamespace
        )
        return response.get("MetricAlarms")

    def get_trail_event_selector(self, trail_arn):
        response = self.conn.get_event_selectors(TrailName=trail_arn)
        return response.get("EventSelectors", [])

    def get_s3_bucket_logging(self, bucket_name):
        try:
            response = self.s3.get_bucket_logging(Bucket=bucket_name)
            return response.get("LoggingEnabled", {})
        except Exception as e:
            logger.error(f"Error in getting cloudtrail trail logging bucket {e} ")
        return {}

    def get_s3_public_access_block(self, bucket_name):
        try:
            response = self.s3.get_public_access_block(Bucket=bucket_name)
            return response.get("PublicAccessBlockConfiguration", {})
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
                return {
                    "BlockPublicAcls": False,
                    "BlockPublicPolicy": False,
                    "IgnorePublicAcls": False,
                    "RestrictPublicBuckets": False,
                }
        return {}

    def get_s3_bucket_policy(self, bucket_name):
        try:
            response = self.s3.get_bucket_policy(Bucket=bucket_name)
            policy = response.get("Policy", json.dumps({}))
            return json.loads(policy)
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in getting bucket policy {e}")
        return {}

    def get_s3_bucket_acl(self, bucket_name):
        try:
            response = self.s3.get_bucket_acl(Bucket=bucket_name)
            if "ResponseMetadata" in response:
                del response["ResponseMetadata"]
            return response
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in getting bucket ACL {e}")
        return {}

    def get_s3_bucket_access_points(self, account_id, bucket_name):
        try:
            response = self.s3_control.list_access_points(
                AccountId=account_id, Bucket=bucket_name
            )
            if "ResponseMetadata" in response:
                del response["ResponseMetadata"]
            return response.get("AccessPointList")
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in getting bucket s3 {e}")
            return []

    def get_s3_access_point_policy(self, account_id, access_point_name):
        try:
            response = self.s3_control.get_access_point_policy(
                AccountId=account_id, Name=access_point_name
            )
            if "ResponseMetadata" in response:
                del response["ResponseMetadata"]
            return response.get("Policy")
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in getting bucket s3 access point policy {e}")
            return json.dumps({})

    def get_s3_access_point(self, account_id, access_point_name):
        try:
            response = self.s3_control.get_access_point(
                AccountId=account_id, Name=access_point_name
            )
            if "ResponseMetadata" in response:
                del response["ResponseMetadata"]
            return response
        except botocore.exceptions.ClientError as e:
            logger.error(f"Error in getting bucket s3 access point {e}")
            return {}


def register() -> None:
    factory.register("log_monitor", AwsCloudtrail)
