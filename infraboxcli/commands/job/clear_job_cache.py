import click

import infraboxcli


@click.command(name="clear")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
def clear_job_cache(project_id, job_id):
    """
    Clears a job's cache for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    """

    infraboxcli.CLI_SETTINGS.get_api().clear_job_cache(project_id, job_id)
    infraboxcli.logger.info("Job cache cleared successfully.")

    infraboxcli.CLI_SETTINGS.save()
