# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsLogMetric(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct log metric service
        """
        super().__init__(**kwargs, client_type="logs")
        self.resource = resource
        self.cloudwatch = self.client("cloudwatch")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.describe_log_groups()
        return [
            {**item, "type": "logs_metrics"} for item in response.get("logGroups", [])
        ]

    def get_resources(self) -> Any:
        """
        Fetches log metrics details.
        """
        metric_filters = self.get_metric_filters(self.resource.get("logGroupName"))
        try:
            metrics = []
            for metric in metric_filters:
                metricAlarms = []
                for data in metric.get("metricTransformations", []):
                    metricAlarms.append(
                        {
                            **data,
                            "metricAlarms": self.get_alarms_for_metric(
                                data.get("metricName"), data.get("metricNamespace")
                            ),
                        }
                    )
                metrics.append({**metric, "metricTransformations": metricAlarms})
        except Exception as ex:
            logger.error(f"Error {ex}")
            metrics = []

        return {**self.resource, "metricFilters": metrics}

    def get_metric_filters(self, logGroupName):
        def fetch_metric_filters(
            metric_filter_list=None, continueToken=None, name=None
        ):
            request = {}
            if continueToken:
                request["nextToken"] = continueToken
                request["logGroupName"] = name
            response = self.conn.describe_metric_filters(**request)
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
        response = self.cloudwatch.describe_alarms_for_metric(
            MetricName=metricName, Namespace=filterNamespace
        )
        return response.get("MetricAlarms")


def register() -> Any:
    factory.register("logs_metrics", AwsLogMetric)
