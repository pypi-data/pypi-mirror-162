# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsPolicy(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct policy service
        """

        super().__init__(**kwargs, client_type="iam")
        self.policy = resource

    def get_inventory(self) -> Any:
        """ """

        response = self.conn.list_policies(Scope="Local")
        policies = [
            {**item, "type": "policy", "Scope": "Local"}
            for item in response.get("Policies", [])
        ]

        aws_support_policy = self.conn.get_policy(
            PolicyArn="arn:aws:iam::aws:policy/AWSSupportAccess"
        ).get("Policy")
        policies.append({**aws_support_policy, "type": "policy", "Scope": "AWS"})
        return policies

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        policy = {
            **self.policy,
            "Document": self.conn.get_policy_version(
                PolicyArn=self.policy.get("Arn"),
                VersionId=self.policy.get("DefaultVersionId"),
            )
            .get("PolicyVersion")
            .get("Document"),
            **self.get_entity_for_policy(self.policy.get("Arn")),
        }

        return policy

    def get_entity_for_policy(self, arn):
        resp = self.conn.list_entities_for_policy(PolicyArn=arn)
        del resp["ResponseMetadata"]
        return resp


def register() -> None:
    factory.register("policy", AwsPolicy)
