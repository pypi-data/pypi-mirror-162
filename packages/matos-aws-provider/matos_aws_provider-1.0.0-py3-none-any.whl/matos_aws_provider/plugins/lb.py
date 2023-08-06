# -*- coding: utf-8 -*-
from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsLb(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cluster service
        """

        super().__init__(**kwargs, client_type="elb")
        self.elbv2 = self.client("elbv2")
        self.elb = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        resources = self.conn.describe_load_balancers()
        elb = [
            {"type": "lb", **lb, "Type": "classic"}
            for lb in resources.get("LoadBalancerDescriptions", [])
        ]

        resources = self.elbv2.describe_load_balancers()
        elbv2 = [{"type": "lb", **lb} for lb in resources.get("LoadBalancers", [])]

        return elb + elbv2

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        if self.elb.get("Type") in ["classic"]:
            elb = {
                **self.elb,
                "Attributes": self.get_elbv1_attributes(
                    self.elb.get("LoadBalancerName")
                ),
            }
        else:
            elb = {
                **self.elb,
                "Attributes": self.get_attributes(),
                "Listeners": self.get_listeners(),
                "TargetGroups": self.get_target_groups(),
            }

        return elb

    def get_attributes(self):
        resp = self.elbv2.describe_load_balancer_attributes(
            LoadBalancerArn=self.elb.get("LoadBalancerArn")
        )

        attributes = resp.get("Attributes", [])
        attr_data = {}
        for attr in attributes:
            attr_data[attr.get("Key")] = attr.get("Value")
        return attr_data

    def get_listeners(self):
        resources = []
        try:
            resp = self.elbv2.describe_listeners(
                LoadBalancerArn=self.elb.get("LoadBalancerArn")
            )
            listeners = resp.get("Listeners", [])
            for listener in listeners:
                try:
                    rules = self.elbv2.describe_rules(
                        ListenerArn=listener.get("ListenerArn")
                    ).get("Rules", [])
                except Exception as ex:
                    logger.error(f"Error {ex}")
                    rules = []

                try:
                    sslPolicies = self.elbv2.describe_ssl_policies(
                        Names=[listener.get("SslPolicy")]
                    ).get("SslPolicies", [])
                    sslPolicy = (
                        sslPolicies[0]
                        if sslPolicies
                        else {"Name": listener.get("SslPolicy")}
                    )
                except Exception as ex:
                    logger.error(f"Error {ex}")
                    sslPolicy = {"Name": listener.get("SslPolicy")}

                resources.append({**listener, "SslPolicy": sslPolicy, "Rules": rules})
        except Exception as ex:
            logger.error(f"{ex}=== fetch elb listener issue")

        return resources

    def get_target_groups(self):
        resources = []
        try:
            target_groups = self.elbv2.describe_target_groups(
                LoadBalancerArn=self.elb.get("LoadBalancerArn")
            ).get("TargetGroups", [])
            for target in target_groups:
                arn = target.get("TargetGroupArn")
                # target group attrs
                tg_attrs = self.elbv2.describe_target_group_attributes(
                    TargetGroupArn=arn
                ).get("Attributes")
                attr = {}
                for att in tg_attrs:
                    attr[att.get("Key")] = att.get("Value")
                # target health
                target_health = self.elbv2.describe_target_health(
                    TargetGroupArn=arn
                ).get("TargetHealthDescriptions", [])
                resources.append(
                    {
                        **target,
                        "Attributes": attr,
                        "TargetHealthDescriptions": target_health,
                    }
                )
        except Exception as ex:
            logger.error(f"{ex}===== target group fetch error")

        return resources

    def get_elbv1_attributes(self, name):
        attr = {}
        try:
            attr = self.conn.describe_load_balancer_attributes(
                LoadBalancerName=name
            ).get("LoadBalancerAttributes")
        except Exception as ex:
            logger.error(f"{ex}=== fetch elb v1 attributes")

        return attr


def register() -> Any:
    factory.register("lb", AwsLb)
