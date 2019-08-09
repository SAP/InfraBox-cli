import click
from time import sleep
import infraboxcli
from v2infraboxapi import Build, RunnableStatus


@click.command(name="trigger")
@infraboxcli.add_project_id_option
@click.option("-b", "--branch-sha", "branch_or_sha", default=None, required=True,
              help="Branch name or commit's sha.")
@click.option("-v", "--validate", "validate", is_flag=True,
              help="Displays the command's parameters instead of executing the request.")
@click.option("-e", "--env", "env", multiple=True, default=[],
              help="An environment variable. (Format NAME=VALUE or NAME)")
@click.option("-w", "--wait", "wait", is_flag=True,
              help="Whether we should wait for the build to finish.")
def trigger_new_build(project_id, branch_or_sha, env, validate, wait):
    """
    Triggers a build for a PROJECT_ID.
    You can specify environment variables in the following format: NAME=VALUE or NAME.
    \f
    :type project_id: str
    :param project_id: the project's id
    :type branch_or_sha: str
    :param branch_or_sha: branch name or commit's sha
    :type env: list
    :param env: list of strings to format "NAME=VALUE"
    :type validate: bool
    :param validate: whether we should only display the parameters instead of executing the request
    :type wait: bool
    :param wait: whether we should wait for the build to finish
    """

    formatted_env = []
    for string in env:
        if '=' in string:
            name, value = string.split('=')
        else:
            name, value = string, ""
        formatted_env.append({"name": name, "value": value})

    # Validate only?
    if validate:
        print(infraboxcli.tabulate([[project_id, branch_or_sha]], headers=["Project Id", "Branch"]))
        print("")
        print(infraboxcli.tabulate([(d["name"], d["value"]) for d in formatted_env], headers=["Name", "Value"]))
        return

    # Triggering
    api = infraboxcli.CLI_SETTINGS.get_api()
    rep = api.trigger_new_build(project_id, branch_or_sha, formatted_env)
    infraboxcli.logger.info(rep["message"])

    data = rep["data"]["build"]
    build = Build(project_id=project_id,
                  build_id=data["id"],
                  build_number=data["build_number"],
                  restart_counter=data["restartCounter"])
    # Saving the build id to the env
    infraboxcli.CLI_SETTINGS.get_from_env(build.id, "build_id")
    infraboxcli.CLI_SETTINGS.save()

    if wait:
        while True:
            infraboxcli.logger.info("Waiting for the build to finish...")
            # Getting the jobs to get the build's status
            build.get_jobs(api, True)

            if build.status not in [RunnableStatus.RUNNING, RunnableStatus.QUEUED, RunnableStatus.SCHEDULED]:
                infraboxcli.logger.info("Build finished with status: " + RunnableStatus.to_short_string(build.status))
                break

            sleep(5)

