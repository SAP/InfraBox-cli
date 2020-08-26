import sys
import os
import json
import yaml

from pyinfrabox.infrabox import validate_json
from infraboxcli.env import check_project_root
from infraboxcli.log import logger

def validate_infrabox_file(args):
    args.project_root = os.path.abspath(args.project_root)
    infrabox_file_path = args.infrabox_file_path
    if not os.path.isfile(infrabox_file_path):
        logger.error('%s does not exist' % infrabox_file_path)
        sys.exit(1)

    with open(infrabox_file_path, 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            f.seek(0)
            if (sys.version_info.major == 2) or (yaml.__version__ < "5.1"):
                data = yaml.load(f)
            else:
                data = yaml.load(f, Loader=yaml.FullLoader)
        validate_json(data)

def validate(args):
    check_project_root(args)
    validate_infrabox_file(args)
    logger.info("No issues found in infrabox file %s" % args.infrabox_file_path)
