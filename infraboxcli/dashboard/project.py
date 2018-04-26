from infraboxcli.dashboard.cli_client import get, post, delete
from infraboxcli.dashboard.user import get_user_headers
import infraboxcli.env

from infraboxcli.log import logger

api_projects_endpoint_url = '/api/v1/projects/'


def delete_project(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id
    response = get(url, get_user_headers())

    return response


def list_collaborators(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/collaborators'
    response = get(url, get_user_headers())

    if args.verbose:
        logger.info('Collaborators:')
        msg = ""
        for collaborator in response.json():
            msg += 'Username: %s' % collaborator['username']\
                   + '\nE-mail: %s' % collaborator['email']\
                   + '\n---\n'
        logger.log(msg, print_header=False)

    return response


def add_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/collaborators'
    data = { 'username': args.username }

    response = post(url, data, get_user_headers())
    logger.info(response.json()['message'])

    return response


def remove_collaborator(args):
    infraboxcli.env.check_env_cli_token(args)

    args.verbose = False
    all_project_collaborators = list_collaborators(args).json()
    collaborator_id = None
    for collaborator in all_project_collaborators:
        if collaborator['username'] == args.username:
            collaborator_id = collaborator['id']
            break

    if collaborator_id is None:
        logger.info('Specified user is not in collaborators list.')
        return

    url = args.url + api_projects_endpoint_url + args.project_id + '/collaborators/' +  collaborator_id
    response = delete(url, get_user_headers())
    logger.info(response.json()['message'])

    return response


def list_secrets(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/secrets'

    response = get(url, get_user_headers())
    if args.verbose:
        logger.info('Secrects:')
        msg = ""
        for secret in response.json():
            msg += 'Name: %s' % secret['name']\
                   + '\nId: %s' % secret['id']\
                   + '\n---\n'
        logger.log(msg, print_header=False)

    return response


def get_secret_id_by_name(args):
    args.verbose = False
    all_secrets = list_secrets(args).json()

    for secret in all_secrets:
        if args.name == secret['name']:
            return secret['id']

    return None


def add_secret(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/secrets'
    data = {'name': args.name, 'value': args.value}

    response = post(url, data, get_user_headers())
    logger.info(response.json()['message'])

    return response


def delete_secret(args):
    if args.id:
        delete_secret_by_id(args)
    elif args.name:
        delete_secret_by_name(args)
    else:
        logger.error('Please, provide either token id or description.')


def delete_secret_by_name(args):
    infraboxcli.env.check_env_cli_token(args)

    secret_id = get_secret_id_by_name(args)

    if not secret_id:
        logger.info('Secret with such a name does not exist.')
        return

    args.id = secret_id
    return delete_secret_by_id(args)


def delete_secret_by_id(args):
    infraboxcli.env.check_env_cli_token(args)

    url = args.url + api_projects_endpoint_url + args.project_id + '/secrets/' + args.id
    response = delete(url, get_user_headers())
    logger.info(response.json()['message'])

    return response


def list_project_tokens(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/tokens'

    response = get(url, get_user_headers())
    if args.verbose:
        logger.info('Project tokens:')
        msg = ""
        for project_token in response.json():
            msg += 'Description: %s' % project_token['description']\
                   + '\nId: %s' % project_token['id']\
                   + '\nScope push: %s' % project_token['scope_push']\
                   + '\nScope pull: %s' % project_token['scope_pull']\
                   + '\n---\n'
        logger.log(msg, print_header=False)

    return response


def get_project_token_id_by_description(args):
    args.verbose = False
    all_project_tokens = list_project_tokens(args).json()

    for project_token in all_project_tokens:
        if args.description == project_token['description']:
            return project_token['id']

    return None


def add_project_token(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/tokens'

    data = {
        'description': args.description,
        #TODO<Steffen> when scope push/pull functionality is implemented,
        # delete following 2 lines and uncomment next 2 lines
        'scope_push': True,
        'scope_pull': True
        #'scope_push': args.scope_push,
        #'scope_pull': args.scope_pull
    }

    response = post(url, data, get_user_headers())

    if response.status_code != 200:
        logger.error(response.json()['message'])
        return

    # Print project token to the CLI
    logger.info('Authentication Token:'
                + '\nPlease save your token at a secure place. We will not show it to you again.\n\n\n')
    logger.log(response.json()['data']['token'])

    return response


def delete_project_token(args):
    if args.id:
        delete_project_token_by_id(args)
    elif args.description:
        delete_project_token_by_description(args)
    else:
        logger.error('Please, provide either token id or description.')


def delete_project_token_by_description(args):
    infraboxcli.env.check_env_cli_token(args)
    token_id = get_project_token_id_by_description(args)

    if not token_id:
        logger.info('Token with such a description does not exist.')
        return

    args.id = token_id
    return delete_project_token_by_id(args)


def delete_project_token_by_id(args):
    infraboxcli.env.check_env_cli_token(args)
    url = args.url + api_projects_endpoint_url + args.project_id + '/tokens/' + args.id
    response = delete(url, get_user_headers())

    logger.info(response.json()['message'])

    return response
