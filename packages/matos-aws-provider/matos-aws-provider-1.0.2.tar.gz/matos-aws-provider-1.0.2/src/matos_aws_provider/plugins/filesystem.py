# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsFilesystem(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """

        self.filesystem = resource
        self.filesystem_details = {}
        super().__init__(**kwargs, client_type="efs")

    def get_inventory(self) -> Any:
        """ """

        resources = self.conn.describe_file_systems()
        files = resources["FileSystems"]

        filesystem_resources = []
        for file in files:
            filesystem_resources.append(
                {
                    "type": "filesystem",
                    **file,
                }
            )
        return filesystem_resources

    def get_resources(self) -> Any:
        """ """

        backup_policy = {}

        try:
            response = self.conn.describe_backup_policy(
                FileSystemId=self.filesystem["FileSystemId"]
            )
            backup_policy = response["BackupPolicy"]
        except Exception as ex:
            # PolicyNotFound
            logger.error(f"Policy not found {ex}")

        self.filesystem_details = {
            **self.filesystem,
            "BackupPolicy": backup_policy,
        }
        return self.filesystem_details


def register() -> None:
    factory.register("filesystem", AwsFilesystem)
