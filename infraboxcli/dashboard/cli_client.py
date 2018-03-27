import requests

session = requests.Session()


def get(url, headers=None, cookies_handler=None):
    response = session.get(url, headers=headers)
    if cookies_handler:
        cookies_handler(session.cookies.get_dict())
    return response


def post(url, data, headers=None, cookies_handler=None):
    response = session.post(url, json=data, headers=headers)
    if cookies_handler:
        cookies_handler(session.cookies.get_dict())
    return response


def delete(url, headers=None, cookies_handler=None):
    response = session.delete(url, headers=headers)
    if cookies_handler:
        cookies_handler(session.cookies.get_dict())
    return response