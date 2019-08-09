import click

import infraboxcli


@click.command(name="testruns")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
def get_job_testruns(project_id, job_id):
    """
    Lists the job's testruns for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    """

    runs = [secret.to_string_array("name", "suite", "duration", "status", "timestamp")
            for secret in infraboxcli.CLI_SETTINGS.get_api().get_testruns(project_id, job_id)]
    print(infraboxcli.tabulate(runs, headers=["Name", "Suite", "Duration", "Result", "Timestamp"]))

    infraboxcli.CLI_SETTINGS.save()
