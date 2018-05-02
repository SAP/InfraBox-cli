import os
import jwt
import textwrap

from infraboxcli.log import logger


def check_env_url(args):
    if not args.url:
        error_msg = textwrap.dedent("\
            Remote URL is not specified. Either set INFRABOX_URL env var "
            + "or specify an url via `--url` argument.")
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
