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

## List Jobs
If you have a more complex project it may be helpful to list all available jobs in it. For this you may use:

    infrabox list

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

	usage: infrabox run [-h] [--no-rm] [-t TAG] [--local-cache LOCAL_CACHE]
						[job_name]

	positional arguments:
	  job_name              Job name to execute

	optional arguments:
	  -h, --help            show this help message and exit
	  --no-rm               Does not run 'docker-compose rm' before building
	  -t TAG                Docker image tag
	  --local-cache LOCAL_CACHE
							Path to the local cache

To run all jobs defined in your _infrabox.json_ file simply do:

    infrabox run


In case you have multiple jobs defined an want to run only one of them you can do:

    infrabox run <job-name>

## Push a Job
To be able to use infrabox push you have to create a project in the InfraBox Dashboard and create an auth token for it.

Auth Token and InfraBox API Host must be set as environment variables.

    export INFRABOX_CLI_TOKEN=<YOUR_ACCESS_TOKEN>
    export INFRABOX_URL=<INFRABOX_URL>

To push your local project simply do:

    infrabox push

This will compress your local project and upload it to InfraBox. Now you can open the InfraBox Dashboard and navigate to your project. You should see the jobs running on InfraBox.

You can also watch the console output of your pushed jobs locally. Just use the _--show-console_ option.

    infrabox push --show-console

## Pull a Job
In case you would like to run a job which has been already executed on InfraBox you can use _infrabox pull_. It will download the docker container and all its inputs so you can the same container locally and investigate any issue.

    infrabox pull --job-id <JOB_ID>

You can find the exact command for each job on the job detail page of InfraBox under _Run local_

## Secrets
If you reference secrets in your job definition (i.e. as environment variable) then you can add a _.infraboxsecrets.json_ file to your project right next to the _.infrabox.json_ file. This file should then contain all your secrets referenced in your job definition as a simple object:

    {
        "SECRET_NAME1": "my secret value",
        "Another secret": "another value"
    }

## How to get support
If you need help please post your questions to [Stack Overflow](https://stackoverflow.com/questions/tagged/infrabox).
In case you found a bug please open a [Github Issue](https://github.com/InfraBox/infrabox/issues).
Follow us on Twitter: [@Infra_Box](https://twitter.com/Infra_Box) or have look at our Slack channel [infrabox.slack.com](https://infrabox.slack.com/).

## License
Copyright (c) 2018 SAP SE or an SAP affiliate company. All rights reserved.
This file is licensed under the Apache Software License, v. 2 except as noted otherwise in the [LICENSE file](LICENSE).
