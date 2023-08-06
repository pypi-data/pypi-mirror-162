# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.config import INSTANCE_TYPE_CONFIG
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsInstance(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct instance service
        """

        super().__init__(**kwargs, client_type="ec2")
        self.iam = self.client("iam")
        self.ssm = self.client("ssm")
        self.instance_ids = resource.get("instance_id") or resource.get("name")
        self._iam_instance_profiles = None

    def get_inventory(self) -> Any:
        """ """

        resources = self.conn.describe_instances()
        reservations = resources["Reservations"]

        instances = []

        for reservation in reservations:
            for instance in reservation.get("Instances", []):
                instances.append(
                    {
                        "type": "instance",
                        "instance_id": instance["InstanceId"],
                        "name": instance["InstanceId"],
                        "location": instance["Placement"]["AvailabilityZone"],
                    }
                )
        return instances

    @property
    def iam_instance_profiles(self):
        if not self._iam_instance_profiles:
            self._iam_instance_profiles = self.iam.list_instance_profiles().get(
                "InstanceProfiles"
            )

        return self._iam_instance_profiles

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        instances_details = self.get_describe_instances()
        instances_details = self.get_instance_details(instances_details)
        return instances_details

    def get_describe_instances(self):
        if self.instance_ids:
            instance_details = self.conn.describe_instances(
                InstanceIds=self.instance_ids
            )
        else:
            instance_details = self.conn.describe_instances()

        return instance_details

    def get_instance_details(self, instances_details):
        reservations = instances_details.get("Reservations")
        if reservations and isinstance(reservations, list):
            instances = [
                instance.get("Instances")[0]
                for instance in reservations
                if instance.get("Instances")
            ]
            for instance_details in instances:
                self.update_volume_details(instance_details)
                instance_type = instance_details.get("InstanceType")
                instance_config = INSTANCE_TYPE_CONFIG.get(instance_type)
                instance_details["InstanceMemory"] = {
                    "total": instance_config["memory"] if instance_config else 0,
                    "unit": "GB",
                }
                iam_instance_profile_id = instance_details.get(
                    "IamInstanceProfile", {}
                ).get("Id")
                if iam_instance_profile_id:
                    iam_instance_profile_details = self.get_iam_instance_profile(
                        iam_instance_profile_id
                    )
                    instance_details[
                        "IamInstanceProfile"
                    ] = iam_instance_profile_details

                ssm_info = self.get_ssm_info(instance_details.get("InstanceId"))
                if ssm_info:
                    instance_details["SSM"] = ssm_info
                    instance_details[
                        "ssm_patch_compliance"
                    ] = self.get_compliance_status(
                        instance_details.get("InstanceId"), "Patch"
                    )
                    instance_details[
                        "ssm_association_compliance"
                    ] = self.get_compliance_status(
                        instance_details.get("InstanceId"), "Association"
                    )

                if self.instance_ids and instance_details.get("InstanceId") in self.instance_ids:
                    return instance_details
            return instances

    def get_ssm_info(self, instance_id):
        result = []
        try:
            result = self.ssm.describe_instance_associations_status(
                InstanceId=instance_id
            ).get("InstanceAssociationStatusInfos", [])
        except Exception as ex:
            logger.error(f"{ex}===== fetch instance information for SSM")

        return result

    def get_compliance_status(self, resource_id, compliance_type):
        response = self.ssm.list_compliance_items(
            ResourceIds=[resource_id],
            Filters=[{"Key": "ComplianceType", "Values": [compliance_type]}],
            MaxResults=1,
        )
        if "ResponseMetadata" in response:
            del response["ResponseMetadata"]
        return response.get("ComplianceItems", [])

    def update_volume_details(self, instance_details):
        """
        Update instance details with additional volumes data.
        """
        volume_ids = [
            vol["Ebs"]["VolumeId"] for vol in instance_details["BlockDeviceMappings"]
        ]
        volumes = self.conn.describe_volumes(VolumeIds=volume_ids)
        volumes = volumes.get("Volumes")
        total_size = 0
        volumes_data = []
        if volumes:
            for vol in volumes:
                volumes_data.append(vol)
                total_size += vol.get("Size")
            if volumes_data:
                instance_details["BlockDeviceMappings"] = {
                    "DiskSize": {"total": total_size, "unit": "GB"},
                    "Volumes": volumes_data,
                }

    def get_iam_instance_profile(self, profile_id):
        try:
            profiles = [
                profile
                for profile in self.iam_instance_profiles
                if profile.get("InstanceProfileId") == profile_id
            ]
        except Exception as ex:
            logger.error(f" {ex} ====== iam instance profile fetch error")
            return {}
        return profiles[0]


def register() -> None:
    factory.register("instance", AwsInstance)
