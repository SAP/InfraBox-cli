import click

import infraboxcli
from v2infraboxapi import Build


@click.command(name="list")
@infraboxcli.add_project_id_option
@infraboxcli.add_build_id_option
@click.option("-r", "--restart-counter", "restart_counter", default=1, type=click.INT,
              help="The build's restart counter.")
@click.option("-t", "--tree", "tree", is_flag=True,
              help="Display the jobs as a tree instead of a list.")
@click.option("-i", "--ignore-cache", "ignore_cache", is_flag=True,
              help="Whether we should ignore any build stored in the cache.")
def list_jobs(project_id, build_id, restart_counter, tree, ignore_cache):
    """
    Lists a BUILD_ID's jobs. The PROJECT_ID must be specified. Optionally a RESTART_COUNTER can be added.
    Use --tree option to display the jobs' dependencies (only the 1st one gets captured).
    The --tree option will not print anything if the grid style is "json".
    Adds the build to the cache.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type build_id: str
    :param build_id: the build's id
    :type restart_counter: str
    :param restart_counter: the build's restart counter
    :type tree
    :param tree: display the jobs as a tree instead of a list.
    :type ignore_cache: bool
    :param ignore_cache: whether we should ignore any build stored in the cache.
    """

    # Looking for the build in the cache (expecting a full build)
    build = infraboxcli.CLI_SETTINGS.get_build_from_cache(build_id) if not ignore_cache else None

    if build is None:
        api = infraboxcli.CLI_SETTINGS.get_api()
        # Getting the data
        build = Build(project_id, build_id, restart_counter=restart_counter)
        build.get_build_base_information(api)
        build.get_jobs(api)

    # Id history update
    for job in build.jobs:
        infraboxcli.CLI_SETTINGS.id_history["job_id"].add(job.id)

    # Printing the common information
    commit = build.commit
    strings_array = [build.to_string_array("start_date", "duration") +
                     ([commit["id"], commit["author_name"], commit["branch"]] if commit else ["", "", ""])]

    print(infraboxcli.tabulate(strings_array, headers=["Start date", "Duration", "Commit id", "Author", "Branch"]))
    print("")

    # Display as a tree
    if tree:
        if not infraboxcli.CLI_SETTINGS.grid_style == "json":
            print(build.jobs)
    # Display as a list
    else:
        strings_array = [job.to_string_array("status", "name", "start_date", "duration", "id")
                         for job in build.jobs]
        print(infraboxcli.tabulate(strings_array, headers=["State", "Name", "Start date", "Duration", "Id"]))

    infraboxcli.CLI_SETTINGS.add_build_to_cache(build)
    infraboxcli.CLI_SETTINGS.save()
