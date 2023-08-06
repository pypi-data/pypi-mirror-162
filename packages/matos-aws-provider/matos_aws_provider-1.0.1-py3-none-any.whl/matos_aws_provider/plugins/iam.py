# -*- coding: utf-8 -*-
from matos_aws_provider.lib import factory
from typing import Any
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsIAM(BaseProvider):
    def __init__(
        self,
        resource: dict,
        **kwargs,
    ) -> None:
        """ """
        super().__init__(**kwargs, client_type="iam")

    def get_inventory(self) -> Any:
        return None

    def get_resources(self) -> Any:

        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        pwd_policy = None
        try:
            pwd_policy = self.conn.get_account_password_policy().get("PasswordPolicy")
        except Exception as ex:
            logger.error(f"{ex}==== password policy fetch error")
        user_data = {
            "type": "iam",
        }
        if pwd_policy:
            user_data["PasswordPolicy"] = pwd_policy
        return user_data


def register() -> None:
    factory.register("iam", AwsIAM)
