import os

import click

import infraboxcli
from infraboxcli.local_project_dependencies.job_list import load_infrabox_file, get_job_list
from infraboxcli.local_project_dependencies.workflow import WorkflowCache
from infraboxcli.log import logger


@click.command()
def graph():
    """
    Generate a graph of your local jobs.
    """
    config = infraboxcli.local_project_dependencies.LocalProjectConfig.load()

    project_root = os.path.abspath(config.project_root)
    infrabox_file_path = config.infrabox_file
    if not os.path.isfile(infrabox_file_path):
        logger.error('%s does not exist' % infrabox_file_path)

    data = load_infrabox_file(infrabox_file_path)
    jobs = get_job_list(data, infrabox_context=project_root)

    cache = WorkflowCache(project_root, infrabox_file_path)
    cache.add_jobs(jobs)
    cache.print_graph()
