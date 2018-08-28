import getpass
from infraboxcli.log import logger
from infraboxcli.dashboard.cli_client import post
from infraboxcli.dashboard.external import get_current_user_token, save_user_token, delete_current_user_token
import infraboxcli.env

from pyinfrabox.utils import validate_url


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

    if not email:
        email = raw_input("Email: ")
        # Don't allow to pass password without email
        password = None

    if not password:
        password = getpass.getpass('Password: ')

    data = {"email": email, "password": password}

    url = args.url + api_endpoint_url + 'account/login'
    response = post(url, data, cookies_handler=save_user_token, verify=args.ca_bundle)

    return response


def logout(args):
    token_deleted = delete_current_user_token()

    if token_deleted:
        logger.info('Successfully logged out.')
    else:
        logger.info('Already logged out.')
