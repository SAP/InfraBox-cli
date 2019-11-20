import os
import shutil
import subprocess
import tarfile
import tempfile

import click

import infraboxcli
from infraboxcli.log import logger
from v2infraboxapi import TokenKind, ServerErrorException


@click.command(name="pull")
@infraboxcli.add_project_id_option
@infraboxcli.add_job_id_option
@click.option("-c", "--no-container", "no_container", is_flag=True,
              help="Only the inputs will be downloaded but not the actual container. Implies --no-run.")
@click.option("-r", "--no-run", "no_run", is_flag=True,
              help="The container will not be run.")
def pull_job(project_id, job_id, no_container, no_run):
    """
    Downloads the job's manifest for a PROJECT_ID and runs the container.
    Use --no-container to prevent the container's download.
    Use --no-run to avoid running the container (if downloaded)
    \f
    :type project_id: str
    :param project_id: the project's id
    :type job_id: str
    :param job_id: the job's id
    :type no_container: bool
    :param no_container: whether only the inputs will be downloaded but not the actual container.
        Implies no_run=True.
    :type no_run: bool
    :param no_run: whether the container should not be run.
    """

    api = infraboxcli.CLI_SETTINGS.get_api()
    # Getting the manifest
    manifest = api.get_job_manifest(project_id, job_id)

    # Create directories
    path = os.path.join(tempfile.gettempdir(), 'infrabox', manifest['id'])
    if os.path.exists(path):
        shutil.rmtree(path)

    download_path = os.path.join(path, 'downloads')
    os.makedirs(download_path)
    inputs_path = os.path.join(path, 'inputs')
    os.makedirs(inputs_path)
    cache_path = os.path.join(path, 'cache')
    os.makedirs(cache_path)
    output_path = os.path.join(path, 'output')
    os.makedirs(output_path)

    # Download inputs
    for d in manifest['dependencies']:
        p = os.path.join(inputs_path, d['name'])
        logger.info('Downloading output of %s to %s' % (d['name'], p))
        os.makedirs(p)
        package_path = os.path.join(download_path, '%s.%s' % (d['id'], d['output']['format']))

        try:
            tar_gz = api.get_job_output(project_id, d['id'])

            with open(package_path, 'wb') as f:
                for chunk in tar_gz.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        except ServerErrorException as e:
            if e.status_code == 404:
                logger.info('No output found')
                continue
            raise e

        # Unpack
        tar = tarfile.open(package_path)
        tar.extractall(p)

    # Download output
    logger.info('Downloading output of %s to %s' % (manifest['name'], output_path))

    try:
        tar_gz = api.get_job_output(project_id, job_id)
        package_path = os.path.join(download_path, '%s.%s' % (manifest['id'], manifest['output']['format']))

        with open(package_path, 'wb') as f:
            for chunk in tar_gz.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        if os.path.exists(package_path):
            tar = tarfile.open(package_path)
            tar.extractall(output_path)

    except ServerErrorException as e:
        if e.status_code == 404:
            logger.info('No output found')
            pass
        else:
            raise e

    # Remove download dir again
    shutil.rmtree(download_path)

    if no_container:
        return

    # Login
    logger.info("Login to registry")
    image = manifest['image'].replace("//", "/")
    subprocess.check_call(('docker', 'login', image, '-p',
                           infraboxcli.CLI_TOKEN_MANAGER.get_token(TokenKind.PULL, project_id)["token"],
                           '-u', 'infrabox'))

    # Pulling images
    logger.info("Pulling image")
    subprocess.check_call(('docker', 'pull', image))

    if no_run:
        return

    # Running it
    logger.info("Running container")

    cmd = ['docker', 'run', '-v', path + ':/infrabox', image]
    subprocess.check_call(cmd)

    infraboxcli.CLI_SETTINGS.save()
