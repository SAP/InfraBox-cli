import click

import infraboxcli


@click.command(name="stats")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
@click.option("-o", "--output-file", "output_file", type=click.File('w'),
              help="The path to the destination file.")
def get_job_stats(project_id, job_id, output_file):
    """
    Downloads a JOB_ID's stats and prints it (date;cpu;memory format).
    Use the --output-file option to save the stats.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    :type output_file: file
    :param output_file: the the file where the log will be saved.
    """

    stats = infraboxcli.CLI_SETTINGS.get_api().get_job_stats(project_id, job_id).get(job_id, [])
    result = "date;cpu;memory\n"

    sorted_stats = sorted(stats, key=lambda d: int(d["date"]))
    for stat in sorted_stats:
        result += ";".join([str(int(stat["date"]) - int(sorted_stats[0]["date"])),
                            str(stat["cpu"]),
                            str(stat["mem"])]) \
                  + "\n"

    if output_file:
        output_file.write(result)
    else:
        print(result)

    infraboxcli.CLI_SETTINGS.save()
