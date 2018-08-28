import sys
import os
import json

from pyinfrabox.infrabox import validate_json
from infraboxcli.env import check_project_root
from infraboxcli.log import logger

def validate_infrabox_json(args):
    args.project_root = os.path.abspath(args.project_root)
    infrabox_json_path = os.path.join(args.project_root, 'infrabox.json')
    if not os.path.isfile(infrabox_json_path):
        logger.error('%s does not exist' % infrabox_json_path)
        sys.exit(1)

    with open(infrabox_json_path, 'r') as f:
        data = json.load(f)
        validate_json(data)

def validate(args):
    check_project_root(args)
    validate_infrabox_json(args)
    logger.info("No issues found infrabox.json")
