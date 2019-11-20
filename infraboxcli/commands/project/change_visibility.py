import click

import infraboxcli


@click.command(name="chg-visib")
@infraboxcli.add_project_id_option
@click.option("-pub", "--public", "public", is_flag=True,
              help="Whether the project should become public.")
def change_project_visibility(project_id, public):
    """
    Changes the project's visibility (to private by default).
    \f
    :type project_id: str
    :param project_id: the project's id
    :type public: bool
    :param public: whether the project should become public.
    """

    infraboxcli.CLI_SETTINGS.get_api().change_project_visibility(project_id, not public)
    infraboxcli.logger.info("Visibility changed successfully.")

    infraboxcli.CLI_SETTINGS.save()
