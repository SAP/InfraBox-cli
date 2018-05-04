import os
import jwt
import textwrap

from infraboxcli.log import logger
from infraboxcli.dashboard.external import get_current_remote


def check_env_url(args):
    if not args.url:
        current_remote = get_current_remote()
        if current_remote:
            args.url = current_remote
            return

        error_msg = textwrap.dedent("\
            Remote URL is not specified. Either set INFRABOX_URL env var "
            + "or specify an url via `--url` argument.")
        logger.error(error_msg)
        exit(1)


def check_env_cli_token(args):
    check_env_url(args)

    # If we provided project name and enter this function for some reasons
    # just return from it
    if 'project_name' in args \
            and args.project_name \
            and 'project_command' in args \
            and args.project_command:
        exit(1)

    token = os.environ.get('INFRABOX_CLI_TOKEN', None)
    if not token:
        logger.error('INFRABOX_CLI_TOKEN env var must be set')
        exit(1)

    args.token = token

    t = jwt.decode(token, verify=False)
    args.project_id = t['project']['id']
