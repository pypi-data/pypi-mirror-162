import click

from .operations import (
    aws_pull_config,
    aws_push_config,
    gcp_pull_config,
    gcp_push_config,
)

name = "Datateer CLI config commands"


@click.group(help="Commands related to configuration")
def config():
    pass


@config.command(
    help="Pulls configuration down from a Datateer environment and puts it into the configuration directory"
)
@click.option(
    "-d",
    "--config-dir",
    default=".datateer",
    help="will pull the config into this directory and overwrite what is there",
)
@click.option(
    "-r",
    "--region",
    envvar="REGION",
    help="(defaults to env var REGION)",
)
@click.option(
    "-e",
    "--environment",
    envvar="DATATEER_ENV",
    type=click.Choice(["prod", "stg", "qa", "int"], case_sensitive=False),
    required=True,
    help="The target Datateer environment (defaults to env var DATATEER_ENV)",
)
@click.option(
    "-b",
    "--config-bucket",
    help="Until the GCP implementation saves the config bucket name for us to dynamically retrieve it, we must rely on the caller to provide it",
)
@click.option(
    "-c",
    "--cloud",
    type=click.Choice(["aws", "gcp"], case_sensitive=False),
    required=True,
)
def pull(config_dir, region, environment, cloud, config_bucket):
    if cloud == "aws":
        aws_pull_config(config_dir, region, environment)
    elif cloud == "gcp":
        gcp_pull_config(config_dir, config_bucket, region)
    else:
        raise Exception(f'Value "{cloud}" was not recognized for argument "cloud"')


@config.command(
    help="Pushes configuration up to a Datateer environment from the configuration directory"
)
@click.option(
    "-d",
    "--config-dir",
    default=".datateer",
    help="will pull the config into this directory and overwrite what is there",
)
@click.option(
    "-r",
    "--region",
    envvar="REGION",
    help="(defaults to env var REGION)",
)
@click.option(
    "-e",
    "--environment",
    envvar="DATATEER_ENV",
    type=click.Choice(["prod", "stg", "qa", "int"], case_sensitive=False),
    required=True,
    help="The target Datateer environment (defaults to env var DATATEER_ENV)",
)
@click.option(
    "-b",
    "--config-bucket",
    help="Until the GCP implementation saves the config bucket name for us to dynamically retrieve it, we must rely on the caller to provide it",
)
@click.option(
    "-c",
    "--cloud",
    type=click.Choice(["aws", "gcp"], case_sensitive=False),
    required=True,
)
def push(config_dir, region, environment, cloud, config_bucket):
    if cloud == "aws":
        aws_push_config(config_dir, region, environment)
    elif cloud == "gcp":
        gcp_push_config(config_dir, config_bucket, region)
