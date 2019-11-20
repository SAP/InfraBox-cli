import click

import infraboxcli


@click.command(name="delete")
@infraboxcli.add_project_id_option
@click.option("-s", "--secret-id", "secret_id", required=True,
              help="The secret's id.")
def delete_secret(project_id, secret_id):
    """
    Deletes the secret SECRET_ID for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type secret_id: str
    :param secret_id: the secret's id
    """

    infraboxcli.CLI_SETTINGS.get_api().delete_secret(project_id, secret_id)
    infraboxcli.logger.info("Secret deleted successfully.")

    infraboxcli.CLI_SETTINGS.save()
