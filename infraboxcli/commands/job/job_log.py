import click

import infraboxcli
from v2infraboxapi import Job


@click.command(name="log")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
@click.option("-o", "--output-file", "output_file", type=click.File('w'),
              help="The path to the destination file.")
def get_job_log(project_id, job_id, output_file):
    """
    Downloads a JOB_ID's console log and prints it.
    Use the --output-file option to save the log.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    :type output_file: file
    :param output_file: the the file where the log will be saved.
    """

    log = Job.get_console_log(infraboxcli.CLI_SETTINGS.get_api(), project_id, job_id)
    if output_file:
        output_file.write(log)
    elif log != '""':
        print(log)
    else:
        infraboxcli.logger.log("Job's log is empty.")

    infraboxcli.CLI_SETTINGS.save()
