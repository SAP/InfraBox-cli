import os

import click

import infraboxcli
from v2infraboxapi import ServerErrorException


@click.command(name="archive")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
@click.option("-f", "--filename", "filename", default="all_archives.tar.gz",
              help="The name of the file you wish to download.")
@click.option("-t", "--target", "target", default=None, type=click.File("wb"),
              help="The target (path and filename) where the file will be saved.")
def download_archive(project_id, job_id, filename, target):
    """
    Downloads the FILENAME in the job's archive tp the TARGET.
    By default, will download "all_archives.tar.gz" to the current directory.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    :type filename: str
    :param filename: the file to download
    :param target: the target (path and filename) where the file will be saved
    """

    try:
        content = infraboxcli.CLI_SETTINGS.get_api().download_job_archive(project_id, job_id, filename)

        if not target:
            with open(os.path.split(filename)[1], "wb") as f:
                f.write(content)
        else:
            target.write(content)

        infraboxcli.logger.info("File downloaded successfully.")

    except ServerErrorException as e:
        if e.status_code == 404:
            infraboxcli.logger.warn("No archive with such a filename (%s) found." % filename)
        else:
            raise e

    infraboxcli.CLI_SETTINGS.save()
