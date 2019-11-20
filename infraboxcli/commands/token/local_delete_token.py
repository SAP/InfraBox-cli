import click

import infraboxcli


@click.command(name="delete-local")
@infraboxcli.add_project_id_option
@click.option("-h", "--push", "scope_push", is_flag=True,
              help="Whether the token allows to push.")
@click.option("-l", "--pull", "scope_pull", is_flag=True,
              help="Whether the token allows to pull.")
def local_delete_token(project_id, scope_push, scope_pull):
    """
    Deletes a token saved by the CLI.
    Please specify if this token allows to pull/push with their respective options.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type scope_push: bool
    :param scope_push: whether this token allows to push
    :type scope_pull: bool
    :param scope_pull: whether this token allows to pull
    """

    rep = infraboxcli.CLI_TOKEN_MANAGER.delete_token(project_id, push=scope_push, pull=scope_pull)

    infraboxcli.logger.info(str(rep) + " token files deleted successfully.")

    infraboxcli.CLI_SETTINGS.save()
