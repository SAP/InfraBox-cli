import os

from infraboxcli.log import logger

def check_env_cli_token(args):
    token = os.environ.get('INFRABOX_CLI_TOKEN', None)
    if not token:
        logger.error('INFRABOX_CLI_TOKEN env var must be set')
        exit(1)

    args.token = token

def check_env_project_id(args):
    project_id = os.environ.get('INFRABOX_CLI_PROJECT_ID', None)
    if not project_id:
        logger.error('INFRABOX_CLI_PROJECT_ID env var must be set')
        exit(1)

    args.project_id = project_id
