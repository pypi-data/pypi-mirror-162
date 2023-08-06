# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsRestApi(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct api gateway service
        """

        super().__init__(**kwargs, client_type="apigateway")
        self.resource = resource

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.get_rest_apis()
        return [{**item, "type": "rest_api"} for item in response.get("items", [])]

    def get_resources(self) -> Any:
        """
        Fetches rest api gateways details.
        """
        finalStages = []

        stages = self.conn.get_stages(restApiId=self.resource.get("id")).get("item")
        resources = self.conn.get_resources(
            restApiId=self.resource.get("id"), embed=["methods"]
        ).get("items")
        try:
            for stage in stages:
                if stage.get("clientCertificateId"):
                    certificate_details = self.conn.get_client_certificate(
                        clientCertificateId=stage.get("clientCertificateId")
                    )
                    finalStages.append(
                        {
                            **stage,
                            "CertificateExpirationDate": certificate_details.get(
                                "expirationDate"
                            ),
                        }
                    )
                else:
                    finalStages.append(
                        {
                            **stage,
                        }
                    )
        except Exception as ex:
            logger.error(f"Error {ex}")
            finalStages = []

        resource = {
            **self.resource,
            "stages": finalStages,
            "resources": resources,
            "region": self.region,
        }

        return resource


def register() -> Any:
    factory.register("rest_api", AwsRestApi)
