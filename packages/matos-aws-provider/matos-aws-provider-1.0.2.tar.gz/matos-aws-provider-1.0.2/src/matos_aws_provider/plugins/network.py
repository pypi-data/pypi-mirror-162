# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider
from matos_aws_provider.lib.log import get_logger

logger = get_logger()


class AwsNetwork(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct cloudtrail service
        """
        self.network = resource
        super().__init__(**kwargs, client_type="ec2")

    def get_inventory(self) -> Any:
        def fetch_network(network_list=None, continueToken: str = None):
            request = {}
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_vpcs(**request)
            continueToken = response.get("NextToken", None)
            current_networks = [] if not network_list else network_list
            current_networks.extend(response.get("Vpcs", []))

            return current_networks, continueToken

        try:
            networks, nextToken = fetch_network()

            while nextToken:
                networks, nextToken = fetch_network(networks, nextToken)
        except Exception as ex:
            logger.error("network fetch error: ", ex)
            return []
        network_resources = []
        for network in networks:
            detail = {
                "id": network.get("VpcId", ""),
                "type": "network",
                "dhcp_options_id": network.get("DhcpOptionsId", ""),
                "owner_id": network.get("OwnerId", ""),
                "state": network.get("State", ""),
                "description": network.get("Description", ""),
                "tags": network.get("Tags", []),
                "is_default": network.get("isDefault", False),
                "cidr_block_association_set": network.get(
                    "CidrBlockAssociationSet", []
                ),
                "ipv6_cidr_block_association_set": network.get(
                    "Ipv6CidrBlockAssociationSet", []
                ),
                "instance_tenancy": network.get("InstanceTenancy", []),
            }
            network_resources.append(detail)
        return network_resources

    def get_resources(self) -> Any:
        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        subnets = self.get_subnet()
        network_acl = self.get_network_acl()

        self.network = {
            **self.network,
            "subnets": subnets,
            "network_acl": network_acl,
            "security_group": self.get_security_group(),
            "flow_logs": self.get_flow_logs(),
            "instance_sg": self.get_instance_sg_list(),
            "endpoints": self.get_vpc_endpoints(),
            "network_interfaces": self.get_network_interface(),
        }
        return self.network

    def get_network_interface(self):
        try:
            interfaces = self.conn.describe_network_interfaces(
                Filters=[{"Name": "vpc-id", "Values": [self.network.get("id")]}]
            ).get("NetworkInterfaces")
        except Exception as ex:
            interfaces = []
            logger.warning(f"{ex} ====== fetch network interface")
        interfaces = [
            {
                "NetworkInterfaceId": interface.get("NetworkInterfaceId"),
                "Status": interface.get("Status"),
                "OwnerId": interface.get("OwnerId"),
                "RequesterId": interface.get("RequesterId"),
            }
            for interface in interfaces
        ]

        return interfaces

    def get_vpc_endpoints(self):
        def fetch_vpc_endpoints(endpoints=None, continueToken: str = None):
            request = {
                "Filters": [{"Name": "vpc-id", "Values": [self.network.get("id")]}]
            }
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_vpc_endpoints(**request)
            continueToken = response.get("NextToken", None)
            current_endpoint = [] if not endpoints else endpoints
            current_endpoint.extend(response.get("VpcEndpoints", []))

            return current_endpoint, continueToken

        try:
            endpoint_list, nextToken = fetch_vpc_endpoints()

            while nextToken:
                endpoint_list, nextToken = fetch_vpc_endpoints(endpoint_list, nextToken)
        except Exception as ex:
            logger.error(f"network Endpoints fetch error: {ex}")
            return []

        return endpoint_list

    def get_instance_sg_list(self):
        instances = self.conn.describe_instances()
        instance_sg_list = [
            sg.get("GroupId")
            for reserve in instances.get("Reservations", [])
            for instance in reserve.get("Instances", [])
            for sg in instance.get("SecurityGroups", [])
        ]

        return instance_sg_list

    def get_subnet(self):
        def fetch_subnet(subnetwork_list=None, continueToken: str = None):
            request = {"Filters": [{"Name": "vpc-id", "Values": [self.network["id"]]}]}
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_subnets(**request)
            continueToken = response.get("NextToken", None)
            current_subnets = [] if not subnetwork_list else subnetwork_list
            current_subnets.extend(response.get("Subnets", []))

            return current_subnets, continueToken

        try:
            subnets, nextToken = fetch_subnet()

            while nextToken:
                subnets, nextToken = fetch_subnet(subnets, nextToken)
        except Exception as ex:
            logger.error(f"subnet fetch error: {ex}")
            return []

        return subnets

    def get_network_acl(self):
        def fetch_network_acl(acl_list=None, continueToken: str = None):
            request = {"Filters": [{"Name": "vpc-id", "Values": [self.network["id"]]}]}
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_network_acls(**request)
            continueToken = response.get("NextToken", None)
            current_acls = [] if not acl_list else acl_list
            current_acls.extend(response.get("NetworkAcls", []))

            return current_acls, continueToken

        try:
            acls, nextToken = fetch_network_acl()

            while nextToken:
                acls, nextToken = fetch_network_acl(acls, nextToken)
        except Exception as ex:
            logger.warning(f"network acl fetch error: {ex}")
            return []

        return acls

    def get_security_group(self):
        def fetch_security_group(sg_list=None, continueToken: str = None):
            request = {"Filters": [{"Name": "vpc-id", "Values": [self.network["id"]]}]}
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_security_groups(**request)
            continueToken = response.get("NextToken", None)
            current_sg = [] if not sg_list else sg_list
            current_sg.extend(response.get("SecurityGroups", []))

            return current_sg, continueToken

        try:
            sg_data, nextToken = fetch_security_group()

            while nextToken:
                sg_data, nextToken = fetch_security_group(sg_data, nextToken)
        except Exception as ex:
            logger.warning(f"network SG fetch error: {ex}")
            return []

        return sg_data

    def get_flow_logs(self):
        def fetch_flow_logs(flow_log_list=None, continueToken: str = None):
            request = {
                "Filters": [{"Name": "resource-id", "Values": [self.network["id"]]}]
            }
            if continueToken:
                request["NextToken"] = continueToken
            response = self.conn.describe_flow_logs(**request)
            continueToken = response.get("NextToken", None)
            current_flow_logs = [] if not flow_log_list else flow_log_list
            current_flow_logs.extend(response.get("FlowLogs", []))

            return current_flow_logs, continueToken

        try:
            flow_logs, nextToken = fetch_flow_logs()

            while nextToken:
                flow_logs, nextToken = fetch_flow_logs(flow_logs, nextToken)
        except Exception as ex:
            logger.warning(f"network Flow log fetch error: {ex}")
            return []

        return flow_logs


def register() -> None:
    factory.register("network", AwsNetwork)
