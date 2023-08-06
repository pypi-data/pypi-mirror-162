# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsGuardduty(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        super().__init__(**kwargs, client_type="guardduty")
        self.guardduty = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = self.conn.list_detectors().get("DetectorIds")
        return [
            {"detector_id": resource, "type": "guardduty"} for resource in resources
        ]

    def get_resources(self) -> Any:
        """
        Fetches guard duty details.
        """
        high_severity_criteria = {"Criterion": {"severity": {"Gte": 7}}}
        sort_criteria = {"AttributeName": "severity", "OrderBy": "DESC"}
        guardduty = {
            **self.guardduty,
            "high_severity_findings": self.get_findings(
                self.guardduty["detector_id"], high_severity_criteria, sort_criteria
            ),
        }

        return guardduty

    def get_findings(self, detector_id, finding_criteria, sort_criteria):
        response = self.conn.list_findings(
            DetectorId=detector_id,
            FindingCriteria=finding_criteria,
            SortCriteria=sort_criteria,
        )
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("FindingIds", [])


def register() -> Any:
    factory.register("guardduty", AwsGuardduty)
