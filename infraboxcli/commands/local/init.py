import json
import os

import click

from infraboxcli.local_project_dependencies import LocalProjectConfig
from infraboxcli.log import logger


@click.command()
def init():
    """
    Creates a simple project.
    """
    p = os.getcwd()
    logger.info("Initializing %s" % p)

    infrabox_json = os.path.join(p, 'infrabox.json')
    if os.path.exists(infrabox_json):
        logger.error("%s already exists" % infrabox_json)

    dockerfile = os.path.join(p, 'infrabox', 'test', 'Dockerfile')
    infrabox_test = os.path.join(p, 'infrabox', 'test')
    if os.path.exists(dockerfile):
        logger.error("%s already exists" % dockerfile)

    logger.info("Creating infrabox.json")

    with open(infrabox_json, 'w+') as f:
        json.dump({
            "version": 1,
            "jobs": [{
                "name": "test",
                "type": "docker",
                "build_only": False,
                "resources": {"limits": {"memory": 1024, "cpu": 1}},
                "docker_file": "infrabox/test/Dockerfile"
            }
            ]
        }, f, sort_keys=True, indent=4)

    logger.info("Creating infrabox/test/Dockerfile")
    os.makedirs(infrabox_test)

    with open(dockerfile, 'w+') as f:
        f.write("""
    FROM alpine

    RUN adduser -S testuser
    USER testuser

    CMD echo "hello world"
            """)

    gitignore = os.path.join(p, '.gitignore')
    if os.path.exists(gitignore):
        with open(gitignore, 'a') as f:
            f.write("\n.infrabox/")
            f.write("\n.infraboxsecrets.json")

    dockerignore = os.path.join(p, '.dockerignore')
    with open(dockerignore, 'a') as f:
        f.write("\n.infrabox/")
        f.write("\n.infraboxsecrets.json")

    # Creating a local project config
    LocalProjectConfig.load()

    logger.info("Successfully initialized project")
