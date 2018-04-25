import os
import pickle
from os.path import expanduser

from infraboxcli.log import logger

home = expanduser("~")


def save_user_token(dict):
    try:
        f = open(home + '/.infra.data', 'rb')
        obj = pickle.load(f)
        f.close()

    except:
        obj = {}

    if 'token' not in dict.keys():
        logger.error('Unauthorized: invalid username and/or password.')
        exit(1)

    obj['current_user_token'] = dict['token']

    f = open(home + '/.infra.data', 'wb')
    pickle.dump(obj, f)
    f.close()


def load_current_user_token():
    try:
        f = open(home + '/.infra.data', 'rb')
        obj = pickle.load(f)
        f.close()
        curr_token = obj['current_user_token']
    except:
        raise EnvironmentError('Could not load current user token. Please log in')

    return curr_token


def load_current_project_token():
    try:
        f = open(home + '/.infra.data', 'rb')
        obj = pickle.load(f)
        f.close()
        curr_token = obj['current_project_token']
    except:
        raise EnvironmentError('Could not load current project token. Please set current project')

    return curr_token
