import argparse
import os
import sys

from infraboxcli.push import push
from infraboxcli.run import run
from infraboxcli.graph import graph
from infraboxcli.validate import validate
from infraboxcli.list_jobs import list_jobs
from infraboxcli.log import logger
from infraboxcli.init import init
from infraboxcli.pull import pull

version = '0.3.1'

def main():
    parser = argparse.ArgumentParser(prog="infrabox")
    parser.add_argument("--host", required=False, default=os.environ.get('INFRABOX_HOST', 'https://api.infrabox.net'), help="Address of the API server. Required if you want to use your own InfraBox Instance")
    parser.add_argument("--ca-bundle", required=False, default=os.environ.get('INFRABOX_CA_BUNDLE', None), help="Path to a CA_BUNDLE file or directory with certificates of trusted CAs")
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
    parser_pull.add_argument("--job-id", required=True)
    parser_pull.add_argument("--no-container", required=False, dest='pull_container', action='store_false',
                             help="Only the inputs will be downloaded but not the actual container. Implies --no-run.")
    parser_pull.set_defaults(pull_container=True)

    parser_pull.add_argument("--no-run", required=False, dest='run_container', action='store_false',
                             help="The container will not be run.")
    parser_pull.set_defaults(run_container=True)

    parser_pull.add_argument("-e", dest='environment', default=[], required=False,
                             action='append', type=str,
                             help="Add environment variable to jobs")
    parser_pull.set_defaults(func=pull)

    # graph
    parser_graph = sub_parser.add_parser('graph', help='Generate a graph of your local jobs')
    parser_graph.add_argument("--output", required=True, type=str,
                              help="Path to the output file")
    parser_graph.set_defaults(func=graph)

    # validate
    validate_graph = sub_parser.add_parser('validate', help='Validate infrabox.json')
    validate_graph.set_defaults(func=validate)

    # list
    list_job = sub_parser.add_parser('list', help='List all available jobs')
    list_job.set_defaults(func=list_jobs)

    # run
    parser_run = sub_parser.add_parser('run', help='Run your jobs locally')
    parser_run.add_argument("job_name", type=str,
                            help="Job name to execute")
    parser_run.add_argument("--clean", action='store_true', required=False,
                            help="Runs 'docker-compose rm' before building")
    parser_run.add_argument("-e", dest='environment', default=[], required=False,
                            action='append', type=str,
                            help="Add environment variable to jobs")
    parser_run.add_argument("-t", dest='tag', required=False, type=str,
                            help="Docker image tag")
    parser_run.add_argument("--local-cache", required=False, type=str, default="/tmp/infrabox/local-cache",
                            help="Path to the local cache")

    parser_run.set_defaults(clean=False)
    parser_run.set_defaults(func=run)

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
        else:
            if not os.path.exists(args.ca_bundle):
                logger.error("INFRABOX_CA_BUNDLE: %s not found" % args.ca_bundle)
                sys.exit(1)

    # Find infrabox.json
    p = os.getcwd()

    while p:
        tb = os.path.join(p, 'infrabox.json')
        if not os.path.exists(tb):
            p = p[0:p.rfind('/')]
        else:
            args.project_root = p
            args.infrabox_json = tb
            args.project_name = os.path.basename(p)
            break

    if 'project_root' not in args and 'is_init' not in args:
        logger.error("infrabox.json not found in current or any parent directory")
        sys.exit(1)

    # Run command
    args.func(args)
