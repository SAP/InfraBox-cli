import sys
import os
import zipfile
import fnmatch
import tempfile
import requests

from infraboxcli.console import show_console
from infraboxcli.validate import validate_infrabox_json
from infraboxcli.log import logger
import infraboxcli.env

def ignore_file(ignore_list, path):
    for i in ignore_list:
        if fnmatch.fnmatch(path, i):
            return True

    return False

def add_files(args, ignore_list, path, ziph):
    c = os.listdir(path)

    for f in c:
        p = os.path.join(path, f)
        rp = os.path.relpath(p, args.project_root)

        if os.path.isfile(p) and not ignore_file(ignore_list, rp):
            ziph.write(p, rp)
            continue

        if os.path.isdir(p) and not ignore_file(ignore_list, rp):
            add_files(args, ignore_list, p, ziph)
            continue

def zipdir(args):
    logger.info('compressing %s' % args.project_root)

    dockerignore = os.path.join(args.project_root, '.dockerignore')

    ignore_list = []
    if os.path.exists(dockerignore):
        logger.info('Using .dockerignore')

        with open(dockerignore) as di:
            ignore = di.read().splitlines()

            for i in ignore:
                i = i.strip()
                if not i.startswith("#"):
                    ignore_list.append(i)

    ft = tempfile.TemporaryFile()
    ziph = zipfile.ZipFile(ft, 'w', zipfile.ZIP_DEFLATED)

    add_files(args, ignore_list, args.project_root, ziph)

    ziph.close()
    ft.seek(0, os.SEEK_END)
    size = ft.tell()
    logger.info('finished, file size is %s kb' % (size / 1024))
    ft.seek(0)
    return ft

def upload_zip(args, f):
    logger.info('Uploading ...')
    url = '%s/v1/project/%s/upload' % (args.host, args.project_id)
    files = {'project.zip': f}
    headers = {'Authorization': args.token}
    r = requests.post(url, files=files, headers=headers, timeout=120, verify=args.ca_bundle)

    try:
        d = r.json()
    except:
        print(r.text)
        raise

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
