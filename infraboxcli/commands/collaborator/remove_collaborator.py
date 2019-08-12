import click

import infraboxcli


@click.command(name="remove")
@infraboxcli.add_project_id_option
@click.option("-u", "--user-id", "user_id", required=True,
              help="The collaborator's user id.")
def delete_collaborator(project_id, user_id):
    """
    Removes the collaborator USER_ID for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type user_id: str
    :param user_id: the collaborator's id
    """

    infraboxcli.CLI_SETTINGS.get_api().delete_secret(project_id, user_id)
    infraboxcli.logger.info("Collaborator removed successfully.")

    infraboxcli.CLI_SETTINGS.save()
