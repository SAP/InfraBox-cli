import getpass
import json

from infraboxcli.dashboard.cli_client import post, get
from infraboxcli.dashboard.external import load_current_user_token, save_user_token

url_base = 'http://localhost:8080/api/v1/user/'

def get_user_token():
    return load_current_user_token()

def get_user_headers():
    return {'Authorization': 'token %s' % get_user_token()}

def login(args):
    email = raw_input("Email: ")
    password = getpass.getpass('Password: ')

    data = {"email": email, "password": password}

    url = 'http://localhost:8080/api/v1/account/login'
    response = post(url, data, cookies_handler=save_user_token)

    return response

def get_id_by_name(username):
    url = url_base + "id/" + username
    response = get(url, headers=get_user_headers())

    if response.status_code != 200:
        print(response.json()['message'])
        raise Exception(response.status_code)

    # remove quotes
    user_id = response.json()['data']['user_id']

    return user_id
