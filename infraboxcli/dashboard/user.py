import getpass
import json

from infraboxcli.log import logger
from infraboxcli.dashboard.cli_client import post, get
from infraboxcli.dashboard.external import get_current_user_token, save_user_token, delete_current_user_token
from pyinfrabox.utils import validate_url
import infraboxcli.env


api_endpoint_url = '/api/v1/'

def get_user_token():
    return get_current_user_token()

def get_user_headers():
    return {'Authorization': 'token %s' % get_user_token()}

def login(args):
    if args.remote_url:
        args.url = args.remote_url

    if args.remote_url and not validate_url(args.remote_url):
        logger.error('Invalid url.')
        exit(1)

    infraboxcli.env.check_env_url(args)

    email = args.email
    password = args.password

    if email is None:
        email = raw_input("Email: ")
        # Don't allow to pass password without email
        password = None

    if password is None:
        password = getpass.getpass('Password: ')

    data = { "email": email, "password": password}

    url = args.url + api_endpoint_url + 'account/login'
    response = post(url, data, cookies_handler=save_user_token)

    return response


def logout(args):
    token_deleted = delete_current_user_token(args)

    if token_deleted:
        logger.info('Successfully logged out.')
    else:
        logger.info('Already logged out.')
