import click

import infraboxcli


@click.command()
@click.option("-c", "--clear", "clear", is_flag=True,
              help="Whether we should clear the id history.")
def history(clear):
    """
    Displays the data stored in the id/name history. Use the --clear option to clear the history.
    \f
    :type clear: bool
    :param clear: whether we should clear the id history
    """
    settings = infraboxcli.CLI_SETTINGS

    # Clearing if necessary
    if clear:
        settings.clear_history(["project_id", "build_id", "job_id"])
        settings.clear_known_project_names()
        settings.save()
        infraboxcli.logger.info("Id history successfully cleared.")
        return

    # Listing
    id_lists = [sorted(settings.completion_from_history("", key)) for key in ["project_id", "build_id", "job_id"]] + \
               [sorted(settings.known_project_names.keys())]

    # Reformatting through zip_longest
    lengths = [len(l) for l in id_lists]
    printable_lists = []
    n = max(lengths)
    m = len(id_lists)
    for i in range(n):
        line = []
        for j in range(m):
            line.append(id_lists[j][i] if i < lengths[j] else None)
        printable_lists.append(line)

    print(infraboxcli.tabulate(printable_lists, headers=["Project Id", "Build Id", "Job Id", "Project Names"]))
