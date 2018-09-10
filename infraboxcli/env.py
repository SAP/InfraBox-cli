import os
import jwt
import textwrap

from infraboxcli.log import logger
from infraboxcli.dashboard.local_config import get_current_remote_url, get_current_project_name


def check_env_url(args):
    if not args.url:
        current_remote_url = get_current_remote_url()
        if current_remote_url:
            args.url = current_remote_url
            return True

        error_msg = textwrap.dedent("\
            Remote URL is not specified. Either set INFRABOX_URL env var "
            + "or specify an url via `--url` argument.")
        logger.error(error_msg)
        exit(1)


def check_env_cli_token(args):
    check_env_url(args)
    if __check_project_name_set(args):
        return True

    token = os.environ.get('INFRABOX_CLI_TOKEN', None)
    if not token:
        logger.error('INFRABOX_CLI_TOKEN env var must be set')
        exit(1)

    args.token = token

    t = jwt.decode(token, verify=False)
    args.project_id = t['project']['id']

    return True


def __check_project_name_set(args):
    # Use project name from config only if no extra project name was provided
    if not args.project_name:
        current_config_project_name = get_current_project_name(args)
        if current_config_project_name:
            args.project_name = current_config_project_name
            args.using_default_project = True

    return args.project_name


