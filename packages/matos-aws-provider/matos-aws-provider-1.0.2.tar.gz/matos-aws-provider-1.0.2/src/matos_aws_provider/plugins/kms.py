# -*- coding: utf-8 -*-
import json
from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsKms(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        super().__init__(**kwargs, client_type="kms")
        self.kms = resource

    def get_inventory(self) -> Any:
        response = self.conn.list_keys()
        keys = [{**item, "type": "kms"} for item in response.get("Keys", [])]
        return keys

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        key_detail = {}
        try:
            key_detail = self.conn.describe_key(KeyId=self.kms.get("KeyId")).get(
                "KeyMetadata"
            )
        except Exception as e:
            logger.error(f"Error {e}")
        key_policies = []
        try:
            key_policy_names = self.conn.list_key_policies(
                KeyId=self.kms.get("KeyId")
            ).get("PolicyNames")
            key_policies = [
                json.loads(
                    self.conn.get_key_policy(
                        KeyId=self.kms.get("KeyId"), PolicyName=p_name
                    ).get("Policy")
                )
                for p_name in key_policy_names
            ]
        except Exception as e:
            logger.error(f"Error {e}")
        rotation_status = {}
        try:
            rotation_status = self.conn.get_key_rotation_status(
                KeyId=self.kms.get("KeyId")
            ).get("KeyRotationEnabled")
        except Exception as e:
            logger.error(f"Error {e}")
        self.kms = {
            **key_detail,
            "KeyPolicies": key_policies,
            "KeyRotationEnabled": rotation_status,
        }
        return self.kms


def register() -> None:
    factory.register("kms", AwsKms)
