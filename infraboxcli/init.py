import os
import json
import sys

from infraboxcli.log import logger

def init(_):
    p = os.getcwd()
    logger.info("Initializing %s" % p)

    infrabox_json = os.path.join(p, 'infrabox.json')
    if os.path.exists(infrabox_json):
        logger.error("%s already exists" % infrabox_json)
        sys.exit(1)

    dockerfile = os.path.join(p, 'infrabox', 'test', 'Dockerfile')
    infrabox_test = os.path.join(p, 'infrabox', 'test')
    if os.path.exists(dockerfile):
        logger.error("%s already exists" % dockerfile)
        sys.exit(1)


    logger.info("Creating infrabox.json")

    with open(infrabox_json, 'w+') as f:
        json.dump({
            "version": 1,
            "jobs": [{
                "name": "test",
                "type": "docker",
                "build_only": False,
                "machine_config": "vm-1-2048",
                "docker_file": "infrabox/test/Dockerfile"
            }]
        }, f)

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

    dockerignore = os.path.join(p, '.dockerignore')
    with open(dockerignore, 'a') as f:
        f.write("\n.infrabox/")

    logger.info("Successfully initialized project")
    logger.info("Use 'infrabox run' to execute your jobs")
