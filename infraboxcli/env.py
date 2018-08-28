import os
import textwrap

import jwt

from infraboxcli.log import logger
from infraboxcli.dashboard.local_config import get_current_remote_url, get_current_project_name


def check_project_root(args):
    if 'project_root' not in args:
        logger.error("infrabox.json not found in current or any parent directory")
        exit(1)


def check_env_url(args):
    if not args.url:
        current_remote_url = get_current_remote_url()
        if current_remote_url:
            args.url = current_remote_url
            return True

        error_msg = textwrap.dedent("\
            Remote URL is not specified. Either set INFRABOX_URL env var or specify an url via `--url` argument.")
        logger.error(error_msg)
        exit(1)


def check_env_cli_token(args):
    check_env_url(args)

    token = os.environ.get('INFRABOX_CLI_TOKEN', None)
    if not token:
        logger.error('INFRABOX_CLI_TOKEN env var must be set')
        exit(1)

    args.token = token

    t = jwt.decode(token, verify=False)
    args.project_id = t['project']['id']

    if not args.remote_project_name:
        current_config_project_name = get_current_project_name()
        if current_config_project_name:
            args.remote_project_name = current_config_project_name
            args.using_default_project = True


    return True
