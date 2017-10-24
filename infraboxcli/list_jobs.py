import os
import sys

from infraboxcli.log import logger
from infraboxcli.job_list import load_infrabox_json, get_job_list
from infraboxcli.workflow import WorkflowCache

def list_jobs(args):
    args.project_root = os.path.abspath(args.project_root)
    infrabox_json_path = os.path.join(args.project_root, 'infrabox.json')
    if not os.path.isfile(infrabox_json_path):
        logger.error('%s does not exist' % infrabox_json_path)
        sys.exit(1)

    data = load_infrabox_json(args.infrabox_json)
    jobs = get_job_list(data, args, base_path=args.project_root)

    cache = WorkflowCache(args)
    cache.add_jobs(jobs)
    cache.print_tree()
