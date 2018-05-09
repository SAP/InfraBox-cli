import requests

from infraboxcli.log import logger

session = requests.Session()
connection_error_message = 'Can\'t connect to the remote. Please, check your connection or remote url.'


def get(url, headers=None, cookies_handler=None, verify=None, timeout=60):
    try:
        response = session.get(url, headers=headers, verify=verify, timeout=timeout)
    except requests.ConnectionError:
        logger.error(connection_error_message)
        exit(1)
    except Exception as e:
        logger.error(e.message)
        exit(1)

    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response


def post(url, data, headers=None, cookies_handler=None, verify=None, timeout=60):
    try:
        response = session.post(url, json=data, headers=headers, verify=verify, timeout=timeout)
    except requests.ConnectionError:
        logger.error(connection_error_message)
        exit(1)
    except Exception as e:
        logger.error(e.message)
        exit(1)

    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response


def delete(url, headers=None, cookies_handler=None, verify=None, timeout=60):
    try:
        response = session.delete(url, headers=headers, verify=verify, timeout=timeout)
    except requests.ConnectionError:
        logger.error(connection_error_message)
        exit(1)
    except Exception as e:
        logger.error(e.message)
        exit(1)

    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response
