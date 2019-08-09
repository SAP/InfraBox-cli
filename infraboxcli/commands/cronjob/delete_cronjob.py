import click

import infraboxcli


@click.command(name="delete")
@infraboxcli.add_project_id_option
@click.option("-c", "--cronjob-id", "cronjob_id", required=True,
              help="The project's id.")
def delete_secret(project_id, cronjob_id):
    """
    Deletes the cronjob CRONJOB_ID for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type cronjob_id: str
    :param cronjob_id: the secret's id
    """

    infraboxcli.CLI_SETTINGS.get_api().delete_cronjob(project_id, cronjob_id)
    infraboxcli.logger.info("Cronjob deleted successfully.")

    infraboxcli.CLI_SETTINGS.save()
