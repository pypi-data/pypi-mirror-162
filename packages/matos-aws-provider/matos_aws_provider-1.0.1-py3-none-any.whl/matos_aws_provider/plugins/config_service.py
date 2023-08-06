# -*- coding: utf-8 -*-
from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsConfigBase(BaseProvider):
    def __init__(
        self,
        resource: Dict,
        **kwargs,
    ) -> None:
        """ """
        super().__init__(**kwargs, client_type="config")
        self.config_service = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = self.conn.describe_configuration_recorder_status().get(
            "ConfigurationRecordersStatus"
        )
        return [{**resource, "type": "config_service"} for resource in resources]

    def get_resources(self) -> Any:
        """
        Fetches config service details.
        """

        config_service = {**self.config_service}

        return config_service


def register() -> None:
    factory.register("config_service", AwsConfigBase)
