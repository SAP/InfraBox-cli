import click

import infraboxcli


@click.command(name="from-id")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
def job_from_id(project_id, job_id):
    """
    Gets a job from its id for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    """

    job = infraboxcli.CLI_SETTINGS.get_api().get_job(project_id, job_id)
    print(infraboxcli.tabulate([job.to_string_array("status", "name", "start_date", "duration", "id")],
                               headers=["State", "Name", "Start date", "Duration", "Id"]))

    infraboxcli.CLI_SETTINGS.save()
