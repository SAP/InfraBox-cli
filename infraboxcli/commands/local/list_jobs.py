import os

import click

import infraboxcli
from infraboxcli.local_project_dependencies.job_list import load_infrabox_file, get_job_list
from infraboxcli.local_project_dependencies.workflow import WorkflowCache
from infraboxcli.log import logger


@click.command(name="list")
def list_local_jobs():
    """
    Lists all available jobs.
    """

    config = infraboxcli.LocalProjectConfig.load()

    project_root = os.path.abspath(config.project_root)
    infrabox_file_path = config.infrabox_file
    if not os.path.isfile(infrabox_file_path):
        logger.error('%s does not exist' % infrabox_file_path)

    data = load_infrabox_file(infrabox_file_path)
    jobs = get_job_list(data, infrabox_context=project_root)

    # name_to_id = {job["name"]: job["id"] for job in jobs}
    # for i, job in enumerate(jobs):
    #     jobs[i] = Job(job["id"], None, job["name"], None, None, None, [name_to_id[dep["job"]]
    #                                                                    for dep in job.get("depends_on", [])])
    # print(JobTree(jobs))

    cache = WorkflowCache(project_root, infrabox_file_path)
    cache.add_jobs(jobs)
    cache.print_tree()
