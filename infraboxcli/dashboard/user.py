import getpass
import json

from infraboxcli.dashboard.cli_client import post, get
from infraboxcli.dashboard.external import load_current_user_token, save_user_token

api_endpoint_url = '/api/v1/'

def get_user_token():
    return load_current_user_token()

def get_user_headers():
    return {'Authorization': 'token %s' % get_user_token()}

def login(args):
    email = raw_input("Email: ")
    password = getpass.getpass('Password: ')

    data = {"email": email, "password": password}

    url = args.url + api_endpoint_url + 'account/login'
    response = post(url, data, cookies_handler=save_user_token)

    return response

def get_id_by_name(username):
    url = args.url + api_endpoint_url + "user/id/" + username
    response = get(url, headers=get_user_headers())

    if response.status_code != 200:
        print(response.json()['message'])
        raise Exception(response.status_code)

    # remove quotes
    user_id = response.json()['data']['user_id']

    return user_id
