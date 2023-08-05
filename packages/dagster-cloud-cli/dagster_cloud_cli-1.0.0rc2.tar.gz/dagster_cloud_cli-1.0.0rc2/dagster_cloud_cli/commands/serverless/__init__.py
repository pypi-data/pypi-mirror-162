import base64
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List

import dagster._check as check
import pkg_resources
from dagster._utils import file_relative_path
from dagster_cloud_cli import gql, ui
from dagster_cloud_cli.config_utils import (
    DEPLOYMENT_CLI_OPTIONS,
    dagster_cloud_options,
    get_location_document,
)
from dagster_cloud_cli.utils import add_options
from typer import Argument, Option, Typer

app = Typer(help="Build and deploy your code to Dagster Cloud.")

_DOCKER_OPTIONS = {
    "source_directory": (
        Path,
        Option(
            None,
            "--source-directory",
            "-d",
            exists=False,
            help="Source directory to build for the image.",
        ),
    ),
}

_ENV_VAR_OPTIONS = {
    "env": (
        List[str],
        Option(
            [],
            "--env",
            exists=False,
            help="Environment variable to be defined in image, in the form of `MY_ENV_VAR=hello`",
        ),
    ),
}


@contextmanager
def _template_dockerfile(env_vars):
    DOCKERFILE_TEMPLATE = pkg_resources.resource_filename(
        "dagster_cloud_cli", "commands/serverless/Dockerfile"
    )
    with open(DOCKERFILE_TEMPLATE, "r", encoding="utf-8") as template:
        dockerfile_content = "\n".join(
            [template.read(), *[f"ENV {env_var}" for env_var in env_vars]]
        )
        yield bytes(dockerfile_content, "utf-8")


def _build_image(source_directory, image, registry_info, env_vars):
    registry = registry_info["registry_url"]
    with _template_dockerfile(env_vars) as dockerfile_content:
        cmd = [
            "docker",
            "build",
            source_directory,
            "-t",
            f"{registry}:{image}",
            "-f",
            "-",
            "--platform",
            "linux/amd64",
        ]
        return subprocess.run(cmd, input=dockerfile_content, check=True).returncode


@app.command(name="build", short_help="Build image for Dagster Cloud code location.")
@dagster_cloud_options(allow_empty=True, requires_url=True)
@add_options(_DOCKER_OPTIONS)
@add_options(_ENV_VAR_OPTIONS)
def build_command(
    api_token: str,
    url: str,
    location_load_timeout: int,  # pylint: disable=unused-argument
    agent_heartbeat_timeout: int,  # pylint: disable=unused-argument
    image: str = Argument(None, help="Image name."),
    **kwargs,
):
    """Add or update the image for a repository location in the workspace."""
    source_directory = str(kwargs.get("source_directory"))
    env_vars = kwargs.get("env", [])
    _verify_docker()

    with gql.graphql_client_from_url(url, api_token) as client:
        ecr_info = gql.get_ecr_info(client)
        registry = ecr_info["registry_url"]
        retval = _build_image(source_directory, image, ecr_info, env_vars)
        if retval == 0:
            ui.print(f"Built image {registry}:{image}")


def _upload_image(image, registry_info):
    registry = registry_info["registry_url"]
    aws_token = registry_info["aws_auth_token"]
    username, password = base64.b64decode(aws_token).decode("utf-8").split(":")
    subprocess.check_output(
        f"echo {str(password)} | docker login --username {str(username)} --password-stdin {registry}",
        shell=True,
    )
    return subprocess.call(
        ["docker", "push", f"{registry}:{image}"], stderr=sys.stderr, stdout=sys.stdout
    )


@app.command(
    name="upload",
    short_help="Upload the built code location image to Dagster Cloud's image repository.",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
def upload_command(
    api_token: str,
    url: str,
    location_load_timeout: int,  # pylint: disable=unused-argument
    agent_heartbeat_timeout: int,  # pylint: disable=unused-argument
    image: str = Argument(None, help="Image name."),
    **kwargs,  # pylint: disable=unused-argument
):
    """Add or update the image for a repository location in the workspace."""

    _verify_docker()

    with gql.graphql_client_from_url(url, api_token) as client:
        ecr_info = gql.get_ecr_info(client)
        registry = ecr_info["registry_url"]
        retval = _upload_image(image, ecr_info)
        if retval == 0:
            ui.print(f"Pushed image {image} to {registry}")


@app.command(
    name="registry-info",
    short_help="Get registry information and temporary creds for an image repository",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
def registry_info_command(
    api_token: str,
    url: str,
    location_load_timeout: int,  # pylint: disable=unused-argument
    agent_heartbeat_timeout: int,  # pylint: disable=unused-argument
    **kwargs,  # pylint: disable=unused-argument
):
    """Add or update the image for a repository location in the workspace. Used by GH action to
    authenticate to the image registry"""

    with gql.graphql_client_from_url(url, api_token) as client:
        ecr_info = gql.get_ecr_info(client)
        registry_url = ecr_info["registry_url"]
        aws_access_key_id = ecr_info["aws_access_key_id"]
        aws_secret_access_key = ecr_info["aws_secret_access_key"]
        aws_region = ecr_info.get("aws_region", "us-west-2")
        aws_token = ecr_info["aws_auth_token"]
        username, password = base64.b64decode(aws_token).decode("utf-8").split(":")

        ui.print(
            f"""REGISTRY_URL={registry_url}
AWS_ACCESS_KEY_ID={aws_access_key_id}
AWS_SECRET_ACCESS_KEY={aws_secret_access_key}
AWS_DEFAULT_REGION={aws_region}
AWS_ECR_USERNAME={username}
AWS_ECR_PASSWORD={password}
"""
        )


@app.command(
    name="deploy",
    short_help="Add a code location from a local directory",
)
@dagster_cloud_options(allow_empty=True, requires_url=True)
@add_options(_ENV_VAR_OPTIONS)
@add_options(DEPLOYMENT_CLI_OPTIONS)
def deploy_command(
    api_token: str,
    url: str,
    location_load_timeout: int,  # pylint: disable=unused-argument
    agent_heartbeat_timeout: int,  # pylint: disable=unused-argument
    source_directory: Path = Argument(".", help="Source directory."),
    **kwargs,  # pylint: disable=unused-argument
):
    """Add or update the image for a repository location in the workspace."""

    location_name = kwargs.get("location_name")
    if not location_name:
        raise ui.error(
            "No location name provided. You must specify the location name as an argument."
        )

    if not source_directory:
        raise ui.error("No source directory provided.")

    _verify_docker()

    env_vars = kwargs.get("env", [])

    with gql.graphql_client_from_url(url, api_token) as client:
        ecr_info = gql.get_ecr_info(client)
        registry = ecr_info["registry_url"]

        image = kwargs.get("image")
        if not image:
            image = location_name

        retval = _build_image(source_directory, image, ecr_info, env_vars)
        if retval != 0:
            return

        retval = _upload_image(image, ecr_info)
        if retval != 0:
            return

        location_args = {**kwargs, "image": f"{registry}:{image}"}
        location_document = get_location_document(location_name, location_args)
        gql.add_or_update_code_location(client, location_document)
        ui.print(f"Added or updated location {location_name}.")


def _verify_docker():
    if subprocess.call("docker -v", shell=True) != 0:
        raise ui.error("Docker must be installed locally to deploy to Dagster Cloud Serverless")
