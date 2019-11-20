import click

import infraboxcli


@click.command("env")
@click.option("-s", "--save", "save_env_settings", is_flag=True,
              help="Whether we should save the env settings.")
def get_env_information(save_env_settings):
    """
    Lists the information about the environment. (which ids are stored)
    You can also save the grid style, remote url and and CA bundle with the --save option.
    \f
    :type save_env_settings: bool
    :param save_env_settings: Whether we should save the env settings
    """
    env = infraboxcli.CLI_SETTINGS

    # Storing settings changes
    if save_env_settings:
        env.save(save_env_settings=True)

    print(infraboxcli.tabulate([[env.get_from_env(None, "project_id", False),
                                 env.get_from_env(None, "build_id", False),
                                 env.get_from_env(None, "job_id", False)]],
                               headers=["Project Id", "Build Id", "Job Id"]))
    print("")
    print(infraboxcli.tabulate([[env.infrabox_url, env.ca_bundle]],
                               headers=["InfraBox URL", "CA Bundle"]))
