import click

import infraboxcli
from v2infraboxapi import Build


@click.command(name="from-id")
@infraboxcli.add_project_id_option
@infraboxcli.add_build_id_option
@click.option("-f", "--full", "full", type=click.BOOL, flag_value=True,
              help="Whether we should compute the builds' status and duration.")
def build_from_id(project_id, build_id, full):
    """
    Gets a build from its id.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type build_id: str
    :param build_id: the build's id
    :type full: bool
    :param full: whether we should display the full information (jobs related)
    """

    settings = infraboxcli.CLI_SETTINGS
    build = settings.get_build_from_cache(build_id, None)

    if not build:
        api = settings.get_api()
        build = Build(project_id, build_id)
        build.get_build_base_information(api)
        if full:
            build.get_jobs(api, True)

    # Selecting the right information to display
    attrs = ["build_number", "id", "restart_counter"] + (["duration", "status"] if full else [])
    headers = ["Build number", "Id", "Restart counter"] + (["Duration", "Status"] if full else [])

    print(infraboxcli.tabulate([build.to_string_array(*attrs)], headers=headers))

    infraboxcli.CLI_SETTINGS.save()
