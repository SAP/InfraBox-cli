import fnmatch
import json
import os
import tempfile
import zipfile

import click
import yaml

import infraboxcli
import infraboxcli.local_project_dependencies.console as console
from infraboxcli.local_project_dependencies.FilesValidation import validate_json
from infraboxcli.log import logger


@click.command()
@click.option("-s", "--show-console", "show_console", is_flag=True,
              help="Show the console output of the jobs.")
def push(show_console):
    """
    Pushes a local project to InfraBox.
    \f
    :type show_console: bool
    :param show_console: whether we should show the console output of the jobs
    """
    config = infraboxcli.local_project_dependencies.LocalProjectConfig.load()

    if not config.infrabox_url:
        logger.error('The remote url must be set. (See the \"local config\" command)')

    with open(config.infrabox_file, 'r') as f:
        try:
            data = json.load(f)
        except ValueError:
            f.seek(0)
            data = yaml.load(f)
        validate_json(data)

    zip_file = zipdir(config.project_root)
    result = upload_zip(config, zip_file)

    logger.info(result['url'])

    if show_console:
        console.show_console(config.project_id, result['build']['id'])


def ignore_file(ignore_list, path):
    for i in ignore_list:
        if fnmatch.fnmatch(path, i):
            return True

    return False


def add_files(project_root, ignore_list, path, ziph):
    c = os.listdir(path)

    for f in c:
        p = os.path.join(path, f)
        rp = os.path.relpath(p, project_root)

        if os.path.isfile(p) and not ignore_file(ignore_list, rp):
            ziph.write(p, rp)
            continue

        if os.path.isdir(p) and not ignore_file(ignore_list, rp):
            add_files(project_root, ignore_list, p, ziph)
            continue


def zipdir(project_root):
    logger.info('compressing %s' % project_root)

    dockerignore = os.path.join(project_root, '.dockerignore')

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
    with zipfile.ZipFile(ft, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as ziph:
        add_files(project_root, ignore_list, project_root, ziph)

    ft.seek(0, os.SEEK_END)
    size = ft.tell()
    logger.info('Finished, file size is %s kb' % (size / 1024))
    ft.seek(0)
    return ft


def upload_zip(config, f):
    """
    Uploads the zip file to the remote.
    :type config: infraboxcli.local_project_dependencies.LocalProjectConfig
    :param config: the project's config.
    :param f: the file to upload
    """
    logger.info('Uploading ...')

    return config.get_api().upload_project(config.project_id, f)["data"]
