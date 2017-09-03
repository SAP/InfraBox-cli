import os
import json
import signal
import shutil
import sys
from datetime import datetime
import yaml

from infraboxcli.execute import execute
from infraboxcli.job_list import get_job_list, load_infrabox_json
from infraboxcli.log import logger
from pyinfrabox import docker_compose

parent_jobs = []

def makedirs(path):
    os.makedirs(path)
    os.chmod(path, 0o777)

def create_infrabox_directories(args, job, service=None):
    job_name = job['name']

    if service:
        job_name += "/" + service

    # Create dirs
    job_dir = os.path.join(args.project_root, '.infrabox', 'jobs', job_name)
    job_git_source = os.path.join(job_dir, 'git_source')
    infrabox = os.path.join(job_dir, 'infrabox')
    infrabox_cache = os.path.join(infrabox, 'cache')
    infrabox_output = os.path.join(infrabox, 'output')
    infrabox_inputs = os.path.join(infrabox, 'inputs')
    infrabox_testresult = os.path.join(infrabox, 'upload', 'testresult')
    infrabox_markup = os.path.join(infrabox, 'upload', 'markup')
    infrabox_badge = os.path.join(infrabox, 'upload', 'badge')
    infrabox_job_json = os.path.join(infrabox, 'job.json')

    if not os.path.exists(infrabox_cache):
        makedirs(infrabox_cache)

    if os.path.exists(infrabox_output):
        shutil.rmtree(infrabox_output)

    if os.path.exists(infrabox_inputs):
        shutil.rmtree(infrabox_inputs)

    if os.path.exists(infrabox_testresult):
        shutil.rmtree(infrabox_testresult)

    if os.path.exists(infrabox_markup):
        shutil.rmtree(infrabox_markup)

    if os.path.exists(infrabox_badge):
        shutil.rmtree(infrabox_badge)

    if os.path.exists(job_git_source):
        shutil.rmtree(job_git_source)

    makedirs(infrabox_output)
    makedirs(infrabox_inputs)
    makedirs(infrabox_testresult)
    makedirs(infrabox_markup)
    makedirs(infrabox_badge)

    job['directories'] = {
        "output": infrabox_output,
        "inputs": infrabox_inputs,
        "upload/testresult": infrabox_testresult,
        "upload/markup": infrabox_markup,
        "upload/badge": infrabox_badge,
        "cache": infrabox_cache,
        "local-cache": args.local_cache
    }

    # create job.json
    with open(infrabox_job_json, 'w') as out:
        o = {
            "parent_jobs": parent_jobs,
            "local": True,
            "job": {
                "name": job_name,
            },
            "project": {
                "name": args.project_name,
            }
        }

        json.dump(o, out)

    # copy inputs
    for dep in job.get('depends_on', []):
        source_path = os.path.join(args.project_root, '.infrabox',
                                   'jobs', dep, 'infrabox', 'output')

        dep = dep.split("/")[-1]
        destination_path = os.path.join(infrabox_inputs, dep)

        if os.path.exists(source_path):
            shutil.copytree(source_path, destination_path, symlinks=True)

def build_and_run_docker_compose(args, job):
    compose_file = os.path.join(job['base_path'], job['docker_compose_file'])
    compose_file_new = compose_file + ".infrabox"

    # rewrite compose file
    compose_file_content = docker_compose.create_from(compose_file)
    for service in compose_file_content['services']:
        create_infrabox_directories(args, job, service=service)

        volumes = []
        for name, path in job['directories'].items():
            volumes.append('%s:/infrabox/%s' % (path, name))

        compose_file_content['services'][service]['volumes'] = volumes

    with open(compose_file_new, "w+") as out:
        yaml.dump(compose_file_content, out, default_flow_style=False)

    env = {"PATH": os.environ['PATH']}

    for e in args.environment:
        s = e.split("=")
        env[s[0]] = s[1]

    if 'environment' in job:
        for name, value in job['environment'].iteritems():
            if isinstance(value, dict):
                continue

            env[name] = value

    if args.clean:
        execute(['docker-compose', '-p', args.project_name,
                 '-f', compose_file_new, 'rm', '-f'], env=env, cwd=job['base_path'])

    execute(['docker-compose', '-p', args.project_name,
             '-f', compose_file_new, 'build'], env=env, cwd=job['base_path'])

    def signal_handler(_, __):
        logger.info("Stopping docker containers")
        execute(['docker-compose', '-f', compose_file_new, 'stop'], env=env, cwd=job['base_path'])
        os.remove(compose_file_new)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    execute(['docker-compose', '-p', args.project_name,
             '-f', compose_file_new, 'up', '--abort-on-container-exit'], env=env)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    os.remove(compose_file_new)

def build_and_run_docker(args, job):
    create_infrabox_directories(args, job)

    if args.tag:
        image_name = args.tag
    else:
        image_name = args.project_name + '_' + job['name']
        image_name = image_name.replace("/", "-")
        image_name = image_name.lower()

    container_name = job['name'].replace("/", "-")

    # Build the image
    logger.info("Build docker image")
    execute(['docker', 'rm', container_name], cwd=args.project_root, ignore_error=True, ignore_output=True)

    cmd = ['docker', 'build', '-t', image_name, '.', '-f', job['docker_file']]
    if 'build_arguments' in job:
        for name, value in job['build_arguments'].iteritems():
            cmd += ['--build-arg', '%s=%s' %(name, value)]

    execute(cmd, cwd=job['base_path'])

    # Run it
    if 'build_only' in job and not job['build_only']:
        cmd = ['docker', 'run', '--name', container_name]

        for name, path in job['directories'].items():
            cmd += ['-v', '%s:/infrabox/%s' % (path, name)]

        cmd += ['-m', '%sm' % job['resources']['limits']['memory']]

        for e in args.environment:
            cmd += ['-e', e]

        if 'environment' in job:
            for name, value in job['environment'].iteritems():
                if isinstance(value, dict):
                    continue

                cmd += ['-e', '%s=%s' %(name, value)]

        cmd.append(image_name)

        logger.info("Run docker container")
        execute(cmd, cwd=args.project_root)

        if job.get('commit_after_run', False):
            logger.info("Commiting Container")
            execute(['docker', 'commit', container_name, image_name], cwd=args.project_root)

def build_and_run(args, job):
    job_type = job['type']
    start_date = datetime.now()

    logger.info("Starting job %s" % job['name'])

    if job_type == "docker-compose":
        build_and_run_docker_compose(args, job)
    elif job_type == "docker":
        build_and_run_docker(args, job)
    elif job_type == "wait":
        # do nothing
        pass
    else:
        logger.error("Unknown job type")
        sys.exit(1)
    end_date = datetime.now()

    # track as parent
    parent_jobs.append({
        "name": job['name'],
        "state": 'finished',
        "start_date": str(start_date),
        "end_date": str(end_date),
        "machine_config": job.get('machine_config', None),
        "depends_on": job.get('depends_on', [])
    })
    logger.info("Finished job %s" % job['name'])

def run(args):
    # validate infrabox.json
    data = load_infrabox_json(args.infrabox_json)

    # If generator is set we have to run it first
    if 'generator' in data:
        job = {
            "name": "Generator",
            "type": "docker",
            "docker_file": data['generator']['docker_file'],
            "build_only": False,
            "resources": {"limits": {"memory": 1024, "cpu": 1}},
            "base_path": None
        }

        build_and_run(args, job)
        infrabox_json = os.path.join(job['directories']['output'], 'infrabox.json')

        if not os.path.exists(infrabox_json):
            logger.error("Generator did not create an infrabox.json file")
            sys.exit(1)

        data = load_infrabox_json(infrabox_json)

    jobs = get_job_list(data, args, base_path=args.project_root)

    # check if job name exists
    job = None
    if args.job_name:
        for j in jobs:
            if j['name'] == args.job_name:
                job = j
                break

        if not job:
            logger.error("job %s not found in infrabox.json" % args.job_name)
            sys.exit(1)

    if job:
        build_and_run(args, job)
    else:
        for j in jobs:
            build_and_run(args, j)
