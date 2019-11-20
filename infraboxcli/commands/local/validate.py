import json
import os

import click
import yaml

import infraboxcli
from infraboxcli.local_project_dependencies.FilesValidation import validate_json
from infraboxcli.log import logger


@click.command()
def validate():
    """
    Validates infrabox.json or infrabox.yaml.
    Also checks the local project's config.
    """
    config = infraboxcli.local_project_dependencies.LocalProjectConfig.load()

    # Validating the infrabox file
    if not os.path.isfile(config.infrabox_file):
        logger.error('%s does not exist' % config.infrabox_file)

    with open(config.infrabox_file, 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            f.seek(0)
            data = yaml.load(f)
        validate_json(data)

    logger.info("No issues found in infrabox file %s" % config.infrabox_file)

    # Checks the remote url
    if not config.infrabox_url:
        logger.warn("Please use the \"local config\" command to setup the remote url for this project.")

    # Checks the project's id / tokens for this project
    if not config.project_id:
        logger.warn("Please use the \"local config\" command to setup id for this project.")
    else:
        config.check_tokens()
