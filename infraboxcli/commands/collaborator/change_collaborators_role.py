import click

import infraboxcli
from v2infraboxapi import CollaboratorRole


@click.command(name="chg-role")
@infraboxcli.add_project_id_option
@click.option("-u", "--user-id", "user_id", required=True,
              help="The collaborator's user id.")
@click.option("-a", "--administrator", "administrator", cls=infraboxcli.MutuallyExclusiveOption, is_flag=True,
              help="Whether the collaborator's role should become \"Administrator\".",
              mutually_exclusive=["developer"])
def change_collaborators_role(project_id, user_id, administrator):
    """
    Changes the ROLE (to Developer by default) of a USER_ID for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type user_id: str
    :param user_id: the collaborator's id
    :type administrator: bool
    :param administrator: whether the collaborator's role should become \"Administrator\"."
    """

    if administrator:
        role = CollaboratorRole.ADMIN
    else:
        role = CollaboratorRole.DEV

    infraboxcli.CLI_SETTINGS.get_api().put_collaborator(project_id, user_id, CollaboratorRole.to_string(role))
    infraboxcli.logger.info("Role changed successfully.")

    infraboxcli.CLI_SETTINGS.save()
