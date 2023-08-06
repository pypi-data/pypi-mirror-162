# -*- coding: utf-8 -*-
from typing import Any, Dict
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsAppHosting(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        super().__init__(**kwargs, client_type="elasticbeanstalk")
        self.environment = resource
        self.environment_details = {}

    def get_inventory(self) -> Any:
        """
        Get inventory method
        """

        resources = self.conn.describe_environments()
        environments = resources["Environments"]

        environment_resources = []

        for environment in environments:
            environment_resources.append(
                {
                    "type": "apphosting",
                    **environment,
                }
            )
        return environment_resources

    def get_resources(self) -> Any:
        """ 
        Get resource method
        """

        settings = self.conn.describe_configuration_settings(
            ApplicationName=self.environment["ApplicationName"],
            EnvironmentName=self.environment["EnvironmentName"],
        )

        ConfigurationSettings = settings["ConfigurationSettings"]

        requied_options = ["ManagedActionsEnabled", "SystemType"]

        for ConfigurationSetting in ConfigurationSettings:
            OptionSettings = ConfigurationSetting["OptionSettings"]
            required_OptionSettings = []

            for OptionSetting in OptionSettings:
                if OptionSetting["OptionName"] in requied_options:
                    required_OptionSettings.append(OptionSetting)

            ConfigurationSetting["OptionSettings"] = required_OptionSettings

        self.environment_details = {
            **self.environment,
            "ConfigurationSettings": settings["ConfigurationSettings"],
        }
        return self.environment_details


def register() -> None:
    """Register class method"""
    factory.register("apphosting", AwsAppHosting)
