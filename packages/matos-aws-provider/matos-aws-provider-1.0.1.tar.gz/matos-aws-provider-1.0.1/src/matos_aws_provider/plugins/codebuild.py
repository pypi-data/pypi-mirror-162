# -*- coding: utf-8 -*-

from matos_aws_provider.lib import factory
from typing import Any, Dict
from matos_aws_provider.lib.base_provider import BaseProvider


class AwsCodebuild(BaseProvider):
    def __init__(self, resource: Dict, **kwargs) -> None:
        """
        Construct codebuild service
        """
        self.resource = resource
        super().__init__(**kwargs, client_type="codebuild")

    def get_inventory(self) -> Any:
        """
        Service discovery
        """

        response = self.conn.list_projects()
        builddetails = (
            self.conn.batch_get_projects(names=response.get("projects", []))
            if len(response.get("projects", [])) > 0
            else []
        )
        credentails = self.conn.list_source_credentials().get("sourceCredentialsInfos")
        projects = (
            builddetails.get("projects", [])
            if len(response.get("projects", [])) > 0
            else []
        )
        return [
            {**item, "sourceCredentialsInfos": credentails, "type": "codebuild"}
            for item in projects
        ]

    def get_resources(self) -> Any:
        """
        Fetches code build details.
        """
        # fetch all builds id in descending order
        builds = self.conn.list_builds_for_project(
            projectName=self.resource.get("name")
        ).get("ids")
        # fetch first build details
        lastBuildDetails = [builds[0]] if len(builds) > 0 else []
        buildDetails = (
            self.conn.batch_get_builds(ids=lastBuildDetails).get("builds")
            if lastBuildDetails
            else []
        )
        return {
            **self.resource,
            "lastBuildDetails": buildDetails[0] if buildDetails else {},
        }


def register() -> Any:
    factory.register("codebuild", AwsCodebuild)
