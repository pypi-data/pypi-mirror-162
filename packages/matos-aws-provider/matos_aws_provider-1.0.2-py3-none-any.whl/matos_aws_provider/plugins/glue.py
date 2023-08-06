# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsGlue(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct Glue service
        """

        super().__init__(**kwargs, client_type=None)
        self.resource = resource
        self.glue = self.client("glue")
        self.kms = self.client("kms")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        return [{"type": "glue"}]

    def get_resources(self) -> Any:
        """ """
        resource = {**self.resource}
        resource["Jobs"] = self.list_jobs()
        for job in resource["Jobs"]:
            if "SecurityConfiguration" in job:
                job["SecurityConfigurationDetails"] = self.get_security_configuration(
                    job["SecurityConfiguration"]
                )
        resource["DevEndpoints"] = self.list_dev_endpoints()
        for endpoint in resource["DevEndpoints"]:
            if "SecurityConfiguration" in endpoint:
                endpoint[
                    "SecurityConfigurationDetails"
                ] = self.get_security_configuration(endpoint["SecurityConfiguration"])
        resource[
            "DataCatalogueEncryptionSettings"
        ] = self.get_data_catalog_encryption_settings()
        if (
            resource["DataCatalogueEncryptionSettings"]
            .get("EncryptionAtRest", {})
            .get("CatalogEncryptionMode") != "DISABLED"
        ):
            resource["DataCatalogueEncryptionSettings"][
                "KeyDetails"
            ] = self.get_key_details(
                resource["DataCatalogueEncryptionSettings"]
                .get("EncryptionAtRest", {})
                .get("SseAwsKmsKeyId")
            )
        resource["Crawlers"] = self.list_crawlers()
        for crawler in resource["Jobs"]:
            if "CrawlerSecurityConfiguration" in crawler:
                crawler[
                    "SecurityConfigurationDetails"
                ] = self.get_security_configuration(
                    crawler["CrawlerSecurityConfiguration"]
                )
        resource["DataCatalogueResourcePolicy"] = self.get_resource_policy()
        resource["Connections"] = self.get_connections()
        return resource

    def list_jobs(self):
        jobs = []

        def get_jobs(next_token, jobs):
            resp = self.glue.get_jobs(NextToken=next_token)
            jobs += resp.get("Jobs", [])
            if resp.get("NextToken"):
                get_jobs(resp.get("NextToken"), jobs)

        resp = self.glue.get_jobs()
        jobs += resp.get("Jobs", [])
        if resp.get("NextToken"):
            get_jobs(resp.get("NextToken"), jobs)
        return jobs

    def list_dev_endpoints(self):
        endpoints = []

        def get_dev_endpoints(next_token, endpoints):
            resp = self.glue.get_dev_endpoints(NextToken=next_token)
            endpoints += resp.get("DevEndpoints", [])
            if resp.get("NextToken"):
                get_dev_endpoints(resp.get("NextToken"), endpoints)

        resp = self.glue.get_dev_endpoints()
        endpoints += resp.get("DevEndpoints", [])
        if resp.get("NextToken"):
            get_dev_endpoints(resp.get("NextToken"), endpoints)
        return endpoints

    def get_security_configuration(self, configuration_name):
        resp = self.glue.get_security_configuration(Name=configuration_name)
        return resp.get("SecurityConfiguration", {})

    def get_data_catalog_encryption_settings(self):
        resp = self.glue.get_data_catalog_encryption_settings()
        return resp.get("DataCatalogEncryptionSettings", {})

    def get_key_details(self, key_id):
        resp = self.kms.describe_key(KeyId=key_id)
        return resp.get("KeyMetadata", {})

    def list_crawlers(self):
        endpoints = []

        def get_crawlers(next_token, endpoints):
            resp = self.glue.get_crawlers(NextToken=next_token)
            endpoints += resp.get("Crawlers", [])
            if resp.get("NextToken"):
                get_crawlers(resp.get("NextToken"), endpoints)

        resp = self.glue.get_crawlers()
        endpoints += resp.get("Crawlers", [])
        if resp.get("NextToken"):
            get_crawlers(resp.get("NextToken"), endpoints)
        return endpoints

    def get_resource_policy(self, arn=None):
        # No ARN need to pass to get resource policy of data catalogue
        if arn:
            resp = self.glue.get_resource_policy(ResourceArn=arn)
        else:
            resp = self.glue.get_resource_policy()
        return resp

    def get_connections(self, catalog_id=None):
        # No ARN need to pass to get resource policy of data catalogue
        if catalog_id:
            resp = self.glue.get_connections(CatalogId=catalog_id)
        else:
            resp = self.glue.get_connections()
        return resp.get("ConnectionList")


def register() -> Any:
    factory.register("glue", AwsGlue)
