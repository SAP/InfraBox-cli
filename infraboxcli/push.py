import sys
import os
import zipfile
import tempfile
import requests

from infraboxcli.console import show_console
from infraboxcli.validate import validate_infrabox_json
from infraboxcli.log import logger
import infraboxcli.env

def zipdir(args):
    logger.info('compressing %s' % args.project_root)
    ft = tempfile.TemporaryFile()
    ziph = zipfile.ZipFile(ft, 'w', zipfile.ZIP_DEFLATED)

    for root, _, files in os.walk(args.project_root):
        for f in files:
            ziph.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), args.project_root))

    ziph.close()
    ft.seek(0, os.SEEK_END)
    size = ft.tell()
    logger.info('finished, file size is %s kb' % (size / 1024))
    ft.seek(0)
    return ft

def upload_zip(args, f):
    logger.info('Uploading ...')
    url = '%s/api/v1/project/%s/upload' % (args.host, args.project_id)
    files = {'project.zip': f}
    headers = {'Authorization': args.token}
    r = requests.post(url, files=files, headers=headers, timeout=120)

    d = r.json()

    if r.status_code != 200:
        logger.error("Upload failed: %s" % d['message'])
        sys.exit(1)

    return d['data']

def push(args):
    infraboxcli.env.check_env_cli_token(args)
    infraboxcli.env.check_env_project_id(args)

    if not os.path.isdir(args.project_root):
        logger.error('%s does not exist or is not a directory' % args.project_root)
        sys.exit(1)

    validate_infrabox_json(args)

    if args.validate_only:
        return

    zip_file = zipdir(args)
    result = upload_zip(args, zip_file)

    if args.show_console:
        show_console(result['build']['id'], args)
