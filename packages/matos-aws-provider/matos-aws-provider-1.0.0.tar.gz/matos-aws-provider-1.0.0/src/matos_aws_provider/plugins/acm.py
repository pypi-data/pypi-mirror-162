# -*- coding: utf-8 -*-
from matos_aws_provider.lib import factory
from typing import Any
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsACM(BaseProvider):
    def __init__(self, resource, **kwargs) -> None:
        """
        Construct acm service
        """

        super().__init__(**kwargs, client_type="acm")
        try:
            self.pcm_client = self.client("acm-pca")
            self.resource = resource
        except Exception as ex:
            logger.error(ex)

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        certificates = []

        def list_certificates(certificates, next_token=None):
            if next_token:
                response = self.conn.list_certificates(NextToken=next_token)
            else:
                response = self.conn.list_certificates()
            certificates += [
                {**item, "type": "acm"}
                for item in response.get("CertificateSummaryList", [])
            ]
            if "NextToken" in response:
                list_certificates(certificates, response["NextToken"])

        list_certificates(certificates)
        return certificates

    def get_resources(self):
        """
        Fetches certificate details.
        """
        resource = {
            **self.resource,
            **self.conn.describe_certificate(
                CertificateArn=self.resource["CertificateArn"]
            ).get("Certificate", {}),
        }
        if resource.get("CertificateAuthorityArn"):
            resource["CertificateAuthority"] = self.get_certificate_authority(
                resource.get("CertificateAuthorityArn")
            )
        return resource

    def get_certificate_authority(self, authority_arn):
        resp = self.pcm_client.describe_certificate_authority(
            CertificateAuthorityArn=authority_arn
        )
        return resp.get("CertificateAuthority", {})


def register() -> Any:
    factory.register("acm", AwsACM)
