import requests

session = requests.Session()


def get(url, headers=None, cookies_handler=None, verify=None, timeout=60):
    response = session.get(url, headers=headers, verify=verify, timeout=timeout)
    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response


def post(url, data, headers=None, cookies_handler=None, verify=None, timeout=60):
    response = session.post(url, json=data, headers=headers, verify=verify, timeout=timeout)
    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response


def delete(url, headers=None, cookies_handler=None, verify=None, timeout=60):
    response = session.delete(url, headers=headers, verify=verify, timeout=timeout)
    if cookies_handler:
        cookies_handler(url, session.cookies.get_dict())
    return response
