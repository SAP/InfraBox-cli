import os
import sys

from infraboxcli.log import logger
from infraboxcli.job_list import load_infrabox_file, get_job_list
from infraboxcli.workflow import WorkflowCache
from infraboxcli.env import check_project_root


def graph(args):
    check_project_root(args)
    args.project_root = os.path.abspath(args.project_root)
    infrabox_file_path = args.infrabox_file_path
    if not os.path.isfile(infrabox_file_path):
        logger.error('%s does not exist' % infrabox_file_path)
        sys.exit(1)

    data = load_infrabox_file(args.infrabox_file_path)
    jobs = get_job_list(data, args, infrabox_context=args.project_root)

    cache = WorkflowCache(args)
    cache.add_jobs(jobs)
    cache.print_graph()
