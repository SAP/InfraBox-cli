import click

import infraboxcli
from infraboxcli.local_project_dependencies import LocalProjectConfig


@click.command(name="config")
@click.option("-p", "--project-id", "project_id", default=None,
              autocompletion=lambda ctx, args, incomplete: infraboxcli.CLI_SETTINGS.completion_from_history(
                  incomplete, "project_id"), help="The project's id.")
@click.option("-u", "--inrabox-url", "infrabox_url", default=None,
              help="The url for the project's remote.")
def config_local_project(infrabox_url, project_id):
    """
    Configures the local project.
    In this command, the project id will NOT be fetched from the id env if missing.
    \f
    :type infrabox_url: str
    :param infrabox_url: the project's remote url
    :type project_id: str
    :param project_id: the project's id
    """

    config = LocalProjectConfig.load()
    if infrabox_url is not None:
        config.infrabox_url = infrabox_url
    if project_id is not None:
        config.project_id = project_id

    # Storing the project id in the env/history
    infraboxcli.CLI_SETTINGS.get_from_env(project_id, "project_id")

    config.check_tokens()

    print(infraboxcli.tabulate([[config.project_id, config.infrabox_url]],
                               headers=["Project Id", "Remote URL"]))

    config.save()
