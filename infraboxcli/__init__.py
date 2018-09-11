import argparse
import os
import sys

from infraboxcli.graph import graph
from infraboxcli.init import init
from infraboxcli.list_jobs import list_jobs
from infraboxcli.log import logger
from infraboxcli.pull import pull
from infraboxcli.push import push
from infraboxcli.run import run
from infraboxcli.validate import validate

from infraboxcli.dashboard import user
from infraboxcli.dashboard import project
from infraboxcli.dashboard import remotes
from infraboxcli.dashboard import local_config
from infraboxcli.install import install_infrabox

version = '0.7.5'

def main():
    username = 'unknown'

    if os.name != 'nt':
        import pwd
        username = pwd.getpwuid(os.getuid()).pw_name

    parser = argparse.ArgumentParser(prog="infrabox")
    parser.add_argument("--url",
                        required=False,
                        default=os.environ.get('INFRABOX_URL', None),
                        help="Address of the API server")
    parser.add_argument("--ca-bundle",
                        required=False,
                        default=os.environ.get('INFRABOX_CA_BUNDLE', None),
                        help="Path to a CA_BUNDLE file or directory with certificates of trusted CAs")
    parser.add_argument("-f", dest='infrabox_file', required=False, type=str,
                        help="Path to an infrabox.json or infrabox.yaml file")
    sub_parser = parser.add_subparsers(help='sub-command help')

    # version
    version_init = sub_parser.add_parser('version', help='Show the current version')
    version_init.set_defaults(version=version)

    # init
    parser_init = sub_parser.add_parser('init', help='Create a simple project')
    parser_init.set_defaults(is_init=True)
    parser_init.set_defaults(func=init)

    # push
    parser_push = sub_parser.add_parser('push', help='Push a local project to InfraBox')
    parser_push.add_argument("--show-console", action='store_true', required=False,
                             help="Show the console output of the jobs")
    parser_push.set_defaults(show_console=False)
    parser_push.set_defaults(validate_only=False)
    parser_push.set_defaults(func=push)

    # pull
    parser_pull = sub_parser.add_parser('pull', help='Pull a remote job')
    parser_pull.set_defaults(is_pull=True)
    parser_pull.add_argument("--job-id", required=True)
    parser_pull.add_argument("--no-container", required=False, dest='pull_container', action='store_false',
                             help="Only the inputs will be downloaded but not the actual container. Implies --no-run.")
    parser_pull.set_defaults(pull_container=True)

    parser_pull.add_argument("--no-run", required=False, dest='run_container', action='store_false',
                             help="The container will not be run.")
    parser_pull.set_defaults(run_container=True)
    parser_pull.set_defaults(func=pull)

    # graph
    parser_graph = sub_parser.add_parser('graph', help='Generate a graph of your local jobs')
    parser_graph.set_defaults(func=graph)

    # validate
    validate_graph = sub_parser.add_parser('validate', help='Validate infrabox.json or infrabox.yaml')
    validate_graph.set_defaults(func=validate)

    # list
    list_job = sub_parser.add_parser('list', help='List all available jobs')
    list_job.set_defaults(func=list_jobs)

    # install
    install = sub_parser.add_parser('install', help='Setup InfraBox')
    install.set_defaults(is_install=True)
    install.set_defaults(func=install_infrabox)

    # run
    parser_run = sub_parser.add_parser('run', help='Run your jobs locally')
    parser_run.add_argument("job_name", nargs="?", type=str,
                            help="Job name to execute")
    parser_run.add_argument("--no-rm", action='store_true', required=False,
                            help="Does not run 'docker-compose rm' before building")
    parser_run.add_argument("--build-arg", required=False, type=str, nargs='?',
                            help="Set docker build arguments", action='append')
    parser_run.add_argument("--env", required=False, type=str, nargs='?',
                            help="Override environment variables", action='append')
    parser_run.add_argument("--env-file", required=False, type=str, default=None,
                            help="Environment file to override environment values")
    parser_run.add_argument("-t", dest='tag', required=False, type=str,
                            help="Docker image tag")
    parser_run.add_argument("-c", "--children", action='store_true',
                            help="Also run children of a job")
    parser_run.add_argument("--local-cache", required=False, type=str,
                            default="/tmp/{}/infrabox/local-cache".format(username),
                            help="Path to the local cache")
    parser_run.add_argument("--memory", required=False, type=float,
                            help="Override a memory limit for your job")
    parser_run.add_argument("--cpu", required=False, type=float,
                            help="Override a cpu limit for your job")
    parser_run.add_argument("--unlimited", action='store_true', required=False,
                            help="Do not apply cpu and mem limits.")
    parser_run.set_defaults(no_rm=False)
    parser_run.set_defaults(func=run)

    # Project
    parser_project = sub_parser.add_parser('project', help='Manage your project')
    parser_project.add_argument('--project-name', dest='remote_project_name', required=False, type=str)
    parser_project.set_defaults(project_command=True)
    sub_project = parser_project.add_subparsers(dest='project')

    # Project list
    parser_projects_list = sub_project.add_parser('list', help='Get a list of all your projects')
    parser_projects_list.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_projects_list.set_defaults(func=project.list_projects)

    # Project status
    parser_projects_list = sub_project.add_parser('status', help='Get some info about your current project')
    parser_projects_list.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_projects_list.set_defaults(func=project.print_status)

    # Create project
    parser_project_create = sub_project.add_parser('create', help='Create a new project')
    parser_project_create.add_argument('--name', required=True, type=str,
                                       help='Name of the project you want to create')
    parser_project_create.add_argument('--type', required=True, type=str,
                                       help='Name of the project { upload, github, gerrit } you want to create')
    parser_project_create.add_argument('--public', required=False, default=False, action='store_true',
                                       help='Make your project public')
    parser_project_create.add_argument('--private', required=False, default=False, action='store_true',
                                       help='Make your project private')
    parser_project_create.set_defaults(func=project.create_project)

    parser_project_delete = sub_project.add_parser('delete', help='Delete a project')
    parser_project_delete.add_argument('--name', required=False, type=str,
                                       help='Name of the project you want to delete')
    parser_project_delete.add_argument('--id', required=False, type=str,
                                       help='Id of the project you want to delete')
    parser_project_delete.set_defaults(func=project.delete_project)

    # Collaborators
    parser_collaborators = sub_project.add_parser('collaborators', help='Add or remove collaborators for your project')
    sub_collaborators = parser_collaborators.add_subparsers()

    parser_list_collaborators = sub_collaborators.add_parser('list', help='Show collaborators list')
    parser_list_collaborators.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_list_collaborators.set_defaults(func=project.list_collaborators)

    parser_add_collaborator = sub_collaborators.add_parser('add', help='Add a collaborator')
    parser_add_collaborator.add_argument('--username', required=True, type=str,
                                         help='Username of the collaborator you want to add')
    parser_add_collaborator.set_defaults(func=project.add_collaborator)

    parser_remove_collaborator = sub_collaborators.add_parser('remove', help='Remove a collaborator')
    parser_remove_collaborator.add_argument('--username', required=True, type=str,
                                         help='Username of the collaborator you want to remove')
    parser_remove_collaborator.set_defaults(func=project.remove_collaborator)

    # Secrets
    parser_secrets = sub_project.add_parser('secrets', help='Create or delete secrets')
    sub_secrets = parser_secrets.add_subparsers()

    parser_list_secrets = sub_secrets.add_parser('list', help='Show all your secrets')
    parser_list_secrets.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_list_secrets.set_defaults(func=project.list_secrets)

    parser_create_secret = sub_secrets.add_parser('create', help='Create a secret')
    parser_create_secret.add_argument('--name', required=True, type=str, help='Name of the secret')
    parser_create_secret.add_argument('--value', required=True, type=str, help='Value of the secret')
    parser_create_secret.set_defaults(func=project.add_secret)

    parser_delete_secret = sub_secrets.add_parser('delete', help='Delete a secret')
    parser_delete_secret.add_argument('--name', required=False, type=str,
                                      help='Name of the secret you want to delete')
    parser_delete_secret.add_argument('--id', required=False, type=str,
                                      help='Id of the secret you want to delete')
    parser_delete_secret.set_defaults(func=project.delete_secret)

    # Tokens
    parsers_project_tokens = sub_project.add_parser('tokens', help='Manage your project tokens')
    sub_project_tokens = parsers_project_tokens.add_subparsers()

    parser_list_project_tokens = sub_project_tokens.add_parser('list', help='Show all your project tokens')
    parser_list_project_tokens.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_list_project_tokens.set_defaults(func=project.list_project_tokens)

    parser_add_project_token = sub_project_tokens.add_parser('create', help='Create a project token')
    parser_add_project_token.add_argument('--description', required=True, type=str,
                                          help='Description of the project token you want to create')
    #TODO<Steffen> when scope push/pull functionality is implemented, uncomment following 2 lines
    #parser_add_project_token.add_argument('--scope_push', required=False, default=True, type=str2bool, help='Scope push')
    #parser_add_project_token.add_argument('--scope_pull', required=False, default=True, type=str2bool, help='Scope pull')
    parser_add_project_token.set_defaults(func=project.add_project_token)

    parser_remove_project_token = sub_project_tokens.add_parser('delete', help='Delete a project token')
    parser_remove_project_token.add_argument('--id', required=False, type=str,
                                             help='Id of the project token you want to delete')
    parser_remove_project_token.add_argument('--description', required=False, type=str,
                                             help='Description of the project token you want to delete')
    parser_remove_project_token.set_defaults(func=project.delete_project_token)

    # Login
    parser_login = sub_parser.add_parser('login', help='Login to infrabox')
    parser_login.add_argument('remote_url', nargs='?', type=str, help='Name of remote')
    parser_login.add_argument('--email', required=False, default=None, type=str, help='Email of the user')
    parser_login.add_argument('--password', required=False, default=None, type=str, help='Password of the user')
    parser_login.set_defaults(func=user.login)

    # Logout
    parser_logout = sub_parser.add_parser('logout', help='Logout from current remote')
    parser_logout.set_defaults(func=user.logout)

    # Config
    parser_config = sub_parser.add_parser('config', help='Configure your infrabox')
    sub_config = parser_config.add_subparsers(dest='config')

    parser_config_current_project = sub_config.add_parser('set-current-project', help='Set new current project')
    parser_config_current_project.add_argument('project_name', nargs='?', type=str, help='Name of the project')
    parser_config_current_project.set_defaults(func=local_config.set_current_project_name)

    # Remotes
    parser_remotes = sub_parser.add_parser('remotes', help='Current remotes')
    sub_remotes = parser_remotes.add_subparsers()
    parser_remotes_list = sub_remotes.add_parser('list', help='Show your all remotes')
    parser_remotes_list.add_argument('--verbose', required=False, default=True, type=str2bool)
    parser_remotes_list.set_defaults(func=remotes.list_remotes)

    # Parse args
    args = parser.parse_args()

    if 'version' in args:
        print('infraboxcli %s' % version)
        return

    if "DOCKER_HOST" in os.environ:
        logger.error("DOCKER_HOST is set")
        logger.error("infrabox can't be used to run jobs on a remote machine")
        sys.exit(1)

    if args.ca_bundle:
        if args.ca_bundle.lower() == "false":
            args.ca_bundle = False
            # according to: https://stackoverflow.com/a/28002687/131120
            import requests.packages.urllib3 as urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        else:
            if not os.path.exists(args.ca_bundle):
                logger.error("INFRABOX_CA_BUNDLE: %s not found" % args.ca_bundle)
                sys.exit(1)

    if args.infrabox_file:
        if not os.path.exists(args.infrabox_file):
            logger.error('%s does not exist' % args.infrabox_file)
            sys.exit(1)

        p = os.path.abspath(args.infrabox_file)

        args.project_root = p[0:p.rfind('/')]
        args.infrabox_file_path = p
        args.project_name = os.path.basename(p)
    else:
        # Find infrabox.json
        p = os.getcwd()

        while p:
            tb = os.path.join(p, 'infrabox.json')
            if not os.path.exists(tb):
                tb = os.path.join(p, 'infrabox.yaml')
            if not os.path.exists(tb):
                p = p[0:p.rfind('/')]
            else:
                args.project_root = p
                args.infrabox_file_path = tb
                args.project_name = os.path.basename(p)
                break

    if 'job_name' not in args:
        args.children = True

    if 'project_root' not in args and 'is_init' not in args and 'is_pull' not in args and 'is_install' not in args:
        logger.error("infrabox.json or infrabox.yaml not found in current or any parent directory")
        sys.exit(1)

    # Run command
    args.func(args)


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
