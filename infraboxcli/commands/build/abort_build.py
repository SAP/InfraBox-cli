import click

import infraboxcli


@click.command(name="abort")
@infraboxcli.add_project_id_option
@infraboxcli.add_build_id_option
def abort_build(project_id, build_id):
    """
    Aborts a build for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type build_id: str
    :param build_id: the build's id
    """
    infraboxcli.CLI_SETTINGS.get_api().abort_build(project_id, build_id)
    infraboxcli.logger.info("Build successfully aborted.")

    infraboxcli.CLI_SETTINGS.save()
