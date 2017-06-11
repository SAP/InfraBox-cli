import sys
import os
import json

from pyinfrabox.infrabox import validate_json
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
    if not os.path.isdir(args.project_root):
        logger.error('%s does not exist or is not a directory' % args.project_root)
        sys.exit(1)

    validate_infrabox_json(args)

    logger.info("No issues found infrabox.json")
