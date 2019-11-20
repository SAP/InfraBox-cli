import click

import infraboxcli


@click.command(name="clear")
@infraboxcli.add_project_id_option
@infraboxcli.add_build_id_option
def clear_job_cache(project_id, build_id):
    """
    Clears a build's cache for a PROJECT_ID.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type build_id: str
    :param build_id: the build's id
    """
    
    infraboxcli.CLI_SETTINGS.get_api().clear_build_cache(project_id, build_id)
    infraboxcli.logger.info("Build cache successfully cleared.")

    infraboxcli.CLI_SETTINGS.save()
