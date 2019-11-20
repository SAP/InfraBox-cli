import click

import infraboxcli


@click.command(name="list")
@infraboxcli.add_project_id_option
def list_projects_collaborators(project_id):
    """
    Lists the project's collaborators for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    collabs = [collab.to_string_array("id", "username", "name", "email", "role")
               for collab in infraboxcli.CLI_SETTINGS.get_api().get_collaborators(project_id)]
    print(infraboxcli.tabulate(collabs, headers=["Id", "Username", "Name", "Email", "Role"]))

    infraboxcli.CLI_SETTINGS.save()
