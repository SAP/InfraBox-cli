import click

import infraboxcli
from infraboxcli.log import logger


@click.command()
def select():
    """Sets the selected project id in the env as the local project's id."""
    config = infraboxcli.local_project_dependencies.LocalProjectConfig.load()

    if config.project_id:
        logger.info("Successfully selected the local project.")
    else:
        logger.error("The local project's id is missing. Please use the \"local config\" command.")

    # Storing the project_id
    infraboxcli.CLI_SETTINGS.get_from_env(config.project_id, "project_id")
    infraboxcli.CLI_SETTINGS.save()
