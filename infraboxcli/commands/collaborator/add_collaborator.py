import click

import infraboxcli
from v2infraboxapi import CollaboratorRole


@click.command(name="add")
@infraboxcli.add_project_id_option
@click.option("-u", "--username", "username", required=True,
              help="The collaborator's username.")
@click.option("-a", "--administrator", "administrator", is_flag=True,
              help="Whether the collaborator's role should become \"Administrator\".")
def add_collaborator(project_id, username, administrator):
    """
    Adds a USERNAME as a collaborator (with a developer role by default) for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type username: str
    :param username: the collaborator's username
    :type administrator: bool
    :param administrator: whether the collaborator's role should become \"Administrator\"."
    """

    if administrator:
        role = CollaboratorRole.ADMIN
    else:
        role = CollaboratorRole.DEV

    infraboxcli.CLI_SETTINGS.get_api().add_collaborator(project_id, username, CollaboratorRole.to_string(role))
    infraboxcli.logger.info("Collaborator added successfully.")

    infraboxcli.CLI_SETTINGS.save()
