from infraboxcli.dashboard.cli_client import get, post, delete
from infraboxcli.dashboard.user import id_by_neme, get_user_headers
import infraboxcli.env

url_base = 'http://localhost:8080/api/v1/projects/'


def delete_project(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id
    response = get(url, get_user_headers())

    return response


def collaborators(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/collaborators'
    response = get(url, get_user_headers())

    return response


def add_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/collaborators'
    data = {'username': args.username}

    response = post(url, data, get_user_headers())

    return response


def delete_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)
    collaborator_id = id_by_neme(args.username)

    url = url_base + args.project_id + '/collaborators/' + collaborator_id[1:-2]
    response = delete(url, get_user_headers())

    return response


def add_secret(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/secrets'
    data = {'name': args.name, 'value': args.value}

    response = post(url, data, get_user_headers())

    return response


def delete_secret(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/secrets/' + args.name
    response = delete(url, get_user_headers())

    return response


def add_token(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/tokens'
    data = {
        'description': args.d,
        'scope_push': args.scope_push,
        'scope_pull': args.scope_pull
    }

    response = post(url, data, get_user_headers())
    return response


def delete_token(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/tokens/' + args.id
    response = delete(url, get_user_headers())

    return response