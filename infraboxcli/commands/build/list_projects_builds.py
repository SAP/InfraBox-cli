import click

import infraboxcli
from v2infraboxapi import Build


@click.command(name="list")
@infraboxcli.add_project_id_option
@click.option("-l", "--long", "long_version", flag_value=True,
              help="Whether we should compute the builds' status and duration.")
def list_builds(project_id, long_version):
    """
    Lists the last 100 builds for a PROJECT_ID.
    Use the --long option to get the duration and status for the last 10 builds (slower).
    Also if the --long option is used, the builds will be saved in a cache for further use (ex: job list).
    \f
    :type project_id: str
    :param project_id: the project's id
    :type long_version: bool
    :param long_version: whether we should display the full information (jobs related)
    """

    # Getting the builds
    builds = Build.list_last_builds(infraboxcli.CLI_SETTINGS.get_api(), project_id, full=long_version)

    # Id history update
    for build in builds:
        infraboxcli.CLI_SETTINGS.id_history["build_id"].add(build.id)

    # Selecting the right information to display
    attrs = ["build_number", "id", "restart_counter"] + (["duration", "status"] if long_version else [])
    headers = ["Build number", "Id", "Restart counter"] + (["Duration", "Status"] if long_version else [])

    # Getting the attributes we want to display (also makes the required API calls)
    strings_array = []
    for build in builds:
        strings_array.append(build.to_string_array(*attrs))

    print(infraboxcli.tabulate(strings_array, headers=headers))

    if long_version:
        for build in builds:
            infraboxcli.CLI_SETTINGS.add_build_to_cache(build)

    infraboxcli.CLI_SETTINGS.save()
