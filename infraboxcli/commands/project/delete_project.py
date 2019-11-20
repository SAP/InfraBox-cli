import click

import infraboxcli


@click.command(name="delete")
@infraboxcli.add_project_id_option
def delete_project(project_id):
    """
    Deletes the project with PROJECT_ID.
    Also removes tokens for this project from the hard drive.
    \f
    :type project_id: str
    :param project_id: the project's id
    """

    settings = infraboxcli.CLI_SETTINGS
    settings.get_api().delete_project(project_id)
    infraboxcli.logger.info("Project deleted successfully.")

    infraboxcli.CLI_TOKEN_MANAGER.delete_token(project_id, True, True)

    # BUG fix: we also need to delete the relevant information in the cache
    for name in settings.known_project_names:
        if settings.known_project_names[name] == project_id:
            settings.known_project_names.pop(name)
            break

    for build_id in settings.cached_builds:
        if settings.cached_builds[build_id].project_id == project_id:
            settings.cached_builds.pop(build_id)

    settings.save()
