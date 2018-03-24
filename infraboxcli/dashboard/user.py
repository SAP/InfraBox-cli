import getpass

from cli_client import post, get
from external import load_current_user_token, save_user_token

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

def id_by_neme(username):
    url = url_base + "id/" + username
    response = get(url, headers=get_user_headers())

    return response.text
