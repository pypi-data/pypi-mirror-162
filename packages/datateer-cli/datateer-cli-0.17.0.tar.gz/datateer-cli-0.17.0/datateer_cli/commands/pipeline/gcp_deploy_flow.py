import glob
import logging
import os
import tempfile
from importlib import find_loader, import_module
from pathlib import Path
from shutil import copy, copytree, ignore_patterns
from typing import Dict

import click
import pathspec
import yaml

from datateer_cli.commands.config import operations

DOCKERFILE_TEMPLATES_DIR = Path(__file__).parent.joinpath("flow")


def do_deploy(
    flow,
    gcp_project,
    gcp_region,
    client_code,
    environment,
    custom_modules=[],  # list of tuples: full_path, rel_path
    prefect_api_key=None,
    deploy_key_prefect_lib=None,
    prefect_results_bucket=None,
    debug=False,
):
    deploy_key_prefect_lib = deploy_key_prefect_lib or os.getenv(
        "DEPLOY_KEY_PREFECT_LIB"
    )
    if deploy_key_prefect_lib is None:
        raise Exception("deploy_key_prefect_lib is None but is required in do_deploy")

    prefect_api_key = prefect_api_key or os.getenv("PREFECT__CLOUD__API_KEY")
    if prefect_api_key is None:
        raise Exception(
            "prefect_api_key is required, either through a CLI parameter or an environment variable PREFECT__CLOUD__API_KEY"
        )

    if prefect_results_bucket is None:
        click.echo(
            "prefect_results_bucket in do_deploy is None, so the results of this flow's run will not be captured anywhere"
        )
    if os.getenv("MELTANO_DATABASE_URI") is None:
        print(
            "MELTANO_DATABASE_URI is None, so this flow will not attempt to connect to a meltano database"
        )
    else:
        print(
            f'MELTANO_DATABASE_URI is populated with value {os.getenv("MELTANO_DATABASE_URI")[0:12]}***'
        )

    # expensive loads, so defer until now
    from prefect.client.client import Client
    from prefect.executors import LocalExecutor

    # from prefect.environments import LocalEnvironment
    from prefect.run_configs import KubernetesRun
    from prefect.storage import Docker

    dockerfile_path = copy(os.path.join(DOCKERFILE_TEMPLATES_DIR, "Dockerfile"), ".")
    copy(os.path.join(DOCKERFILE_TEMPLATES_DIR, ".dockerignore"), ".")

    flow.storage = Docker(
        registry_url=image_registry_url(gcp_project, gcp_region),
        python_dependencies=["boto3"],
        dockerfile=dockerfile_path,
        image_name=flow.name,
        image_tag="latest",
        files={
            full_path: os.path.join("/datateer/modules", module_path)
            for full_path, module_path in custom_modules
        },
        env_vars={
            "DATATEER_ENV": environment,
            "PYTHONPATH": "$PYTHONPATH:/datateer/modules/",
        },
        build_kwargs={
            "buildargs": {
                # during the build process, the build script runs "meltano install." By default, this command runs against an internal Sqlite database
                # To make sure this runs against the production meltano database, we ensure this env var exists and contains the connection string
                "MELTANO_DATABASE_URI": os.getenv("MELTANO_DATABASE_URI"),
                "DEPLOY_KEY_PREFECT_LIB": deploy_key_prefect_lib,
            }
        },
    )

    env_vars = {"DATATEER_ENV": environment}
    if prefect_results_bucket is not None:
        env_vars["PREFECT_RESULTS_BUCKET"] = prefect_results_bucket

    flow.run_config = KubernetesRun(
        cpu_request=".5",
        cpu_limit="1",
        memory_request="2G",
        memory_limit="8G",
        service_account_name="prefect",
    )

    flow.executor = LocalExecutor()

    Client().create_project(client_code)
    flow.register(
        project_name=client_code,
        # add the environment label and the client label to restrict which agents will run this
        labels=[environment, client_code],
    )


def image_registry_url(gcp_project, gcp_region, include_https=False):
    """Builds a well formed docker registry URL
    Arguments:
        gcp_project {string} -- the GCP project id
        gcp_region {string} -- the Region region e.g. us-central1

    Keyword Arguments:
        include_https {bool} -- True to include the https:// prefix, false to leave off (default: {False})

    Returns:
        string -- A well formed docker registry URL
    """
    registry = f"{gcp_region}-docker.pkg.dev/{gcp_project}/prefect-flows/"
    return f"https://{registry}" if include_https else registry
