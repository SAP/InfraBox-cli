# InfraBox CLI
With the InfraBox CLI you can run your InfraBox jobs on your local machine and configure your project.

## Install
To install infraboxcli you need to have these requirements already installed:

- git
- docker
- python & pip

Then simply run:

    pip install infraboxcli

You can validate your installation by running:

    infrabox version

## Migrating from version 0.8.3 to 2.0

The new version of the CLI does not use environment variables anymore.
To set up your project token, simply save it using the `token save` command as described in the next part.
To specify the InfraBox API Host, use the `--url` option. It is used on a per command basis, so you have to specify the
url for every command. You can save the url using the `env --save` command:

    infrabox --url <INFRABOX_URL> env --save

This also applies if you need to specify a CA bundle.
Most commands have also been moved:
*   `init`, `push`, `graph`, `validate`, `list` and `run` are now `infrabox local` sub-commands.
    For instance `infrabox init` has become `infrabox local init`.
*   The `pull` command can now be found under `job pull`.
*   `collaborators`, `secrets`, and `tokens` are no longer `project` sub-commands.
    For instance `infrabox project secrets list` has become `infrabox secret list`.
*   The `project status` command has been removed.

## Logging in and token management

To login to InfraBox simply do:

    infrabox login --email YOUR_EMAIL

You will then be prompted to enter your password. Neither your email nor your password will be saved, 
only the token we get from logging in is stored on the hard drive.

To see if your logged in or to log out simply do respectively:

    infrabox user
    infrabox logout

Auth tokens can be set with:

    infrabox token save --token TOKEN_VALUE

The project's id is automatically detected from the token's value.
Do not forget to use the `--push` and `--pull` options to specify which rights the token gives.
The CLI will then chose the right token to use for each request.

### The 2 most useful commands

*   The 1ist command is `build list`. It lists the last 100 builds of a project:

        infrabox build list --project-name MY_PROJECT

    If you also want to display the duration and status of the last 10 builds use the `--long` option.

*   The 2nd command is `job list`. It lists the jobs of a build:

        infrabox job list --project-name MY_PROJECT --build-id BUILD_ID
    
    You can also display the jobs as a tree using th option `--tree`, 
    but note that only one of each jobs dependencies will be displayed.
    
        infrabox job list --tree --project-name MY_PROJECT --build-id BUILD_ID

## Setting up a local project

*   To create a new local project, use the `local init` command. 
    If you already have an `infrabox` project jump to the next step.

*   To configure the local project, use the `local config` command. 
    Do not forget to use the `--project-id` option to specify the project's id.
    You can also specify the mote's url with the `--url` option.
    By default, the url will be the same as one used globally by the CLI.

*   Finally if you wish to configure a token for your project, proceed like described earlier.

## List Jobs
If you have a more complex project it may be helpful to list all available jobs in it. For this you may use:

    infrabox local list

It outputs the names of all available jobs. An example output may look like this:

    tutorial-1
    tutorial-1/step1
    tutorial-1/step2
    tutorial-1/step3
    tutorial-1/step4
    tutorial-1/step5
    tutorial-1/tutorial-1/step1/tests
    tutorial-1/tutorial-1/step2/tests
    tutorial-1/tutorial-1/step3/tests
    tutorial-1/tutorial-1/step4/tests
    tutorial-1/tutorial-1/step5/tests

## Run a Job
InfraBox CLI may be used to run you jobs on your local machine. It will also respect all the dependencies and run the jobs in the correct order. Available options are:

    usage: infrabox local run [-h] [--no-rm] [-t TAG] [--local-cache LOCAL_CACHE] [job_name]

    positional arguments:
      job_name              Job name to execute

    optional arguments:
      -h, --help            show this help message and exit
      --no-rm               Does not run 'docker-compose rm' before building
      -t TAG                Docker image tag
      --local-cache LOCAL_CACHE
                            Path to the local cache

To run all jobs defined in your _infrabox.json_ file simply do:

    infrabox local run


In case you have multiple jobs defined an want to run only one of them you can do:

    infrabox local run <job-name>

## Push a Job
To be able to use infrabox push you have to create a project in the InfraBox Dashboard and create an auth token for it.

To push your local project simply do:

    infrabox local push

This will compress your local project and upload it to InfraBox. Now you can open the InfraBox Dashboard and navigate to your project. You should see the jobs running on InfraBox.

You can also watch the console output of your pushed jobs locally. Just use the _--show-console_ option.

    infrabox local push --show-console

## Pull a Job
In case you would like to run a job which has been already executed on InfraBox you can use _infrabox pull_. It will download the docker container and all its inputs so you can the same container locally and investigate any issue.

    infrabox job pull --job-id <JOB_ID>

You can find the exact command for each job on the job detail page of InfraBox under _Run local_

## Secrets
If you reference secrets in your job definition (i.e. as environment variable) then you can add a _.infraboxsecrets.json_ file to your project right next to the _.infrabox.json_ file. This file should then contain all your secrets referenced in your job definition as a simple object:

    {
        "SECRET_NAME1": "my secret value",
        "Another secret": "another value"
    }

## Extra functionalities

*   Some auto-completion is available for bash and can be enabled with the following command:

        source infrabox-bash-autocompletion

    The auto-completion of course includes completing command names but also the input of project/build/job ids based on 
    ids the CLI has already encountered. To see which ids are stored use the `history` command and the `--clear` option to
    clear the history.

*   The build information you get with the `build list --long` command is cached and no new REST API call is required
    for the `job list` command for any of these builds. The cache is saved for 5 minutes, but the timer is refreshed
    after every `build list --long` call. Optionally you can use `job list --ignore-cache` to ignore the cache.

*   The project name resolution uses a cache to remember the id of projects it already looked up.

*   It is tedious to enter all these ids all the time. This is why the CLI will remember the id you use for a 
    project a build or a job. For instance, this is a valid command chain:
    
        infrabox build list -n hanalite
        infrabox job list -b BUILD_ID
    
    Notice how the project id or name does not need to be specified for the job list command.

*   Finally a client/daemon version of the CLI also exists. It is slightly faster, but it can only handle one command at
    a time. It only becomes useful if the environment you are working on is especially slow like for example a Linux 
    subsystem for Windows.

## How to get support
If you need help please post your questions to [Stack Overflow](https://stackoverflow.com/questions/tagged/infrabox).
In case you found a bug please open a [Github Issue](https://github.com/SAP/InfraBox-cli/issues).
Follow us on Twitter: [@Infra_Box](https://twitter.com/Infra_Box) or have look at our Slack channel [infrabox.slack.com](https://infrabox.slack.com/).

## License
Copyright (c) 2018 SAP SE or an SAP affiliate company. All rights reserved.
This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the [LICENSE file](LICENSE).
