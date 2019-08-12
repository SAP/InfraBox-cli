import click

import infraboxcli


@click.command(name="list")
def list_users_projects():
    """
    Lists the user's projects.
    """

    projects = infraboxcli.CLI_SETTINGS.get_api().get_projects()
    printable_projects = [project.to_string_array("name", "id", "type", "private", "userrole") for project in projects]

    # Id history update
    for project in projects:
        infraboxcli.CLI_SETTINGS.id_history["project_id"].add(project.id)
        infraboxcli.CLI_SETTINGS.known_project_names[project.name] = project.id

    print(infraboxcli.tabulate(printable_projects, headers=["Name", "Id", "Type", "Visibility", "User role"]))

    infraboxcli.CLI_SETTINGS.save()
