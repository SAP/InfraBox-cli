import click

import infraboxcli


@click.command(name="list-archives")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
def list_jobs_archives(project_id, job_id):
    """
    Lists the job's archives (files available in the archive).
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    """

    answers = infraboxcli.CLI_SETTINGS.get_api().get_job_archive(project_id, job_id)
    print(infraboxcli.tabulate([[d["filename"]] for d in answers], headers=["Filename"]))

    infraboxcli.CLI_SETTINGS.save()
