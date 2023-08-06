# -*- coding: utf-8 -*-
from typing import Any, Dict
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsLambda(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct function service
        """
        self.functions = resource
        super().__init__(**kwargs, client_type="lambda")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_functions()
        return [{**item, "type": "functions"} for item in response.get("Functions", [])]

    def get_resources(self) -> Any:
        """
        Fetches lambda funtions

        Args:
        return: dictionary object.
        """
        functions = {**self.functions}
        function_details = self.conn.get_function(
            FunctionName=functions.get("FunctionArn")
        )
        try:
            AttachedPolicies = self.conn.get_policy(
                FunctionName=functions.get("FunctionArn")
            )
        except Exception as e:
            logger.error(f"Error {e}")
            AttachedPolicies = []

        return {
            **functions,
            "FunctionDetails": function_details,
            "AttachedPolicies": AttachedPolicies,
        }


def register() -> Any:
    """register class method

    Returns:
        Any: register class
    """
    factory.register("functions", AwsLambda)
