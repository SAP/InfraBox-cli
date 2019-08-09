import click

import infraboxcli


@click.command(name="from")
@infraboxcli.add_project_id_option
def project_from_id_or_name(project_id):
    """
    Gets a project from its id or name.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    project = infraboxcli.CLI_SETTINGS.get_api().get_project(project_id)
    print(infraboxcli.tabulate([project.to_string_array("name", "id", "type", "private", "userrole")],
                               headers=["Name", "Id", "Type", "Visibility", "User role"]))

    # To save the env/hist
    infraboxcli.CLI_SETTINGS.save()
