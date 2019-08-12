import click

import infraboxcli


@click.command(name="restart")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
def restart_job(project_id, job_id):
    """
    Restarts a job for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    """

    infraboxcli.CLI_SETTINGS.get_api().restart_job(project_id, job_id)
    infraboxcli.logger.info("Job restarted successfully.")

    infraboxcli.CLI_SETTINGS.save()
