from infraboxcli.dashboard.cli_client import get, post, delete
from infraboxcli.dashboard.user import get_id_by_name, get_user_headers
import infraboxcli.env

url_base = 'http://localhost:8080/api/v1/projects/'


def delete_project(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id
    response = get(url, get_user_headers())

    return response


def list_collaborators(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/collaborators'
    response = get(url, get_user_headers())

    print('=== Collaborators ===')
    for collaborator in response.json():
        print('Username: %s' % collaborator['username'])
        print('E-mail: %s' % collaborator['email'])
        print('---')

    return response


def add_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/collaborators'
    data = {'username': args.username}

    response = post(url, data, get_user_headers())
    print(response.json()['message'])

    return response


def remove_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)

    try:
        collaborator_id = get_id_by_name(args.username)
    except:
        return

    url = url_base + args.project_id + '/collaborators/' +  collaborator_id
    response = delete(url, get_user_headers())
    print(response.json()['message'])

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


def list_project_tokens(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/tokens'

    response = get(url, get_user_headers())
    print('=== Project tokens ===')
    for project_token in response.json():
        print('Description: %s' % project_token['description'])
        print('Id: %s' % project_token['id'])
        print('Scope push: %s' % project_token['scope_push'])
        print('Scope pull: %s' % project_token['scope_pull'])
        print('---')

    return response


def get_project_token_id_by_description(args):
    url = url_base + args.project_id + '/tokens/' + args.d

    response = get(url, get_user_headers())

    if response.status_code != 200:
        print(response.json()['message'])
        return

    return response.json()['data']['token_id']


def add_project_token(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/tokens'

    data = {
        'description': args.d,
        'scope_push': args.scope_push,
        'scope_pull': args.scope_pull
    }

    response = post(url, data, get_user_headers())

    if response.status_code != 200:
        print(response.json()['message'])
        return

    # Print project token to the CLI
    print('=== Authentication Token ===')
    print('Please save your token at a secure place. We will not show it to you again.\n\n')
    print(response.json()['data']['token'])

    return response


def delete_project_token(args):
    if args.id:
        delete_project_token_by_id(args)
    elif args.d:
        delete_project_token_by_description(args)
    else:
        print('Please, provide either token id or description.')


def delete_project_token_by_description(args):
    infraboxcli.env.check_env_cli_token(args)
    token_id = get_project_token_id_by_description(args)

    if not token_id:
        return

    args.id = token_id
    return delete_project_token_by_id(args)


def delete_project_token_by_id(args):
    infraboxcli.env.check_env_cli_token(args)
    url = url_base + args.project_id + '/tokens/' + args.id
    response = delete(url, get_user_headers())

    print(response.json()['message'])

    return response
