import click

import infraboxcli


@click.command(name="list-local")
def list_local_tokens():
    """
    Lists all the token stored locally.
    """

    project_ids = infraboxcli.CLI_TOKEN_MANAGER.list_tokens()

    print(infraboxcli.tabulate([[project_id, project_ids[project_id]["push"], project_ids[project_id]["pull"]]
                                for project_id in project_ids],
                               headers=["Project id", "Allows to push", "Allows to pull"]))
