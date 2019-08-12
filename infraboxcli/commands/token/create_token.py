import click

import infraboxcli


@click.command(name="create")
@infraboxcli.add_project_id_option
@click.option("-d", "--description", "description", required=True,
              help="The token's description.")
@click.option("-h", "--push", "scope_push", is_flag=True,
              help="Whether the token allows to push.")
@click.option("-l", "--pull", "scope_pull", is_flag=True,
              help="Whether the token allows to pull.")
@click.option("-s", "--save", "save_token", is_flag=True,
              help="Whether we should save the token for later usage by the CLI.")
def create_token(project_id, description, scope_push, scope_pull, save_token):
    """
    Creates a token (with a DESCRIPTION and whether it allows to push/pull) for a PROJECT_ID.
    Please specify if this token allows to pull/push with their respective options.
    If successful, prints the token.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type description: str
    :param description: the token's description
    :type scope_push: bool
    :param scope_push: whether this token allows to push
    :type scope_pull: bool
    :param scope_pull: whether this token allows to pull
    :type save_token: bool
    :param save_token: whether we should save the token for future usage by the CLI
    """

    answer = infraboxcli.CLI_SETTINGS.get_api().create_token(project_id, description, scope_push, scope_pull)
    token = answer["data"]["token"]
    print(token)

    if save_token:
        infraboxcli.CLI_TOKEN_MANAGER.save_token(project_id, token, pull=scope_pull, push=scope_push)

    infraboxcli.CLI_SETTINGS.save()
