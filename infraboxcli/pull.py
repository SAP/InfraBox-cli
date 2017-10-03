import os
import sys
import tempfile
import tarfile
import shutil
import subprocess

import requests

import infraboxcli.env
from infraboxcli.log import logger

def download_file(url, filename, args):
    headers = {'auth-token': args.token}
    r = requests.get(url, headers=headers, stream=True, timeout=5, verify=args.ca_bundle)

    if r.status_code == 404:
        # no file exists
        return

    if r.status_code != 200:
        logger.error("Failed to download output of job")
        sys.exit(1)

    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def pull(args):
    infraboxcli.env.check_env_cli_token(args)
    infraboxcli.env.check_env_project_id(args)

    headers = {'auth-token': args.token}
    url = '%s/v1/project/%s/job/%s/manifest' % (args.api_url, args.project_id, args.job_id)
    r = requests.get(url, headers=headers, timeout=5, verify=args.ca_bundle)

    if r.status_code != 200:
        logger.error("Failed to download job manifest")
        logger.error("Validate your job id and make sure you used 'keep=true' in your job definition")
        sys.exit(1)

    manifest = r.json()

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

    # download inputs
    for d in manifest['dependencies']:
        p = os.path.join(inputs_path, d['name'])
        logger.info('Downloading output of %s to %s' % (d['name'], p))
        os.makedirs(p)
        package_path = os.path.join(download_path, '%s.%s' % (d['id'], d['output']['format']))
        download_file(d['output']['url'], package_path, args)

        if not os.path.exists(package_path):
            continue

        # unpack
        tar = tarfile.open(package_path)
        tar.extractall(p)

    # download output
    logger.info('Downloading output of %s to %s' % (manifest['name'], output_path))

    package_path = os.path.join(download_path, '%s.%s' % (manifest['id'], manifest['output']['format']))
    download_file(manifest['output']['url'], package_path, args)

    if os.path.exists(package_path):
        tar = tarfile.open(package_path)
        tar.extractall(output_path)

    # remove download dir again
    shutil.rmtree(download_path)

    if not args.pull_container:
        return

    # login
    logger.info("Login to registry")
    image = manifest['image'].replace("//", "/")
    subprocess.check_call(('docker', 'login', image, '-p', args.token, '-u', 'infrabox'))

    # pulling images
    logger.info("Pulling image")
    subprocess.check_call(('docker', 'pull', image))

    if not args.run_container:
        return

    # running it
    logger.info("Running container")

    cmd = ['docker', 'run', '-v', '%s:/infrabox' % path]

    for e in args.environment:
        cmd += ['-e', e]

    cmd.append(image)

    subprocess.check_call(cmd)
