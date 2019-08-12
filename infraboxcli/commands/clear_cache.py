import click

import infraboxcli


@click.command(name="clear-cache")
@click.option("-f", "--full", "full", is_flag=True,
              help="Whether we should clear everything (settings, project tokens...).")
def clear_cache(full):
    """
    Manually clears the cache.
    \f
    :type full: bool
    :param full: whether we should clear all the settings
    """

    settings = infraboxcli.CLI_SETTINGS
    settings.clear_cache(force=True)
    if full:
        settings.clear_history(["project_id", "build_id", "job_id"])
        settings.clear_known_project_names()
        settings.id_env = {"project_id": None, "build_id": None, "job_id": None}

    settings.save()

    print("Successfully cleared the cache." + (" (fully)" if full else ""))
