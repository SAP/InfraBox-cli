import os
import json
import signal
import shutil
import sys
import copy
import stat
from datetime import datetime
import traceback
import yaml

from infraboxcli.execute import execute
from infraboxcli.job_list import get_job_list, load_infrabox_json
from infraboxcli.log import logger
from infraboxcli.workflow import WorkflowCache
from pyinfrabox import docker_compose

parent_jobs = []

def makedirs(path):
    os.makedirs(path)
    os.chmod(path, 0o777)

def makedirs_if_not_exists(path):
    if not os.path.exists(path):
        makedirs(path)

def recreate_sym_link(source, link_name):
    if os.name == 'nt':
        if os.path.exists(link_name):
            shutil.rmtree(link_name)
        shutil.copytree(source, link_name)
    else:
        if os.path.exists(link_name):
            os.remove(link_name)
        os.symlink(source, link_name)

def get_build_context(job, args):
    job_build_context = job.get('build_context', None)
    job_infrabox_context = job['infrabox_context']

    # Default build context is the infrabox context
    build_context = job_infrabox_context

    if job_build_context:
        # job specified build context is alway relative to the infrabox context
        build_context = os.path.join(job_infrabox_context, job_build_context)

    build_context = os.path.join(args.project_root, build_context)
    return os.path.normpath(build_context)


def create_infrabox_directories(args, job, service=None, services=None, compose_file=None):
    #pylint: disable=too-many-locals
    job_name = job['name'].replace('/', '_')

    if service:
        job_name += "/" + service

    # Create dirs
    work_dir = os.path.join(args.project_root, '.infrabox', 'work')
    job_dir = os.path.join(work_dir, 'jobs', job_name)
    infrabox = os.path.join(job_dir, 'infrabox')
    infrabox_work = os.path.join(job_dir, 'work')
    infrabox_cache = os.path.join(infrabox, 'cache')
    infrabox_output = os.path.join(infrabox, 'output')
    infrabox_inputs = os.path.join(infrabox, 'inputs')
    infrabox_upload = os.path.join(infrabox, 'upload')
    infrabox_testresult = os.path.join(infrabox_upload, 'testresult')
    infrabox_coverage = os.path.join(infrabox_upload, 'coverage')
    infrabox_markup = os.path.join(infrabox_upload, 'markup')
    infrabox_badge = os.path.join(infrabox_upload, 'badge')
    infrabox_job_json = os.path.join(infrabox, 'job.json')
    infrabox_gosu = os.path.join(infrabox, 'gosu.sh')
    infrabox_local_cache = args.local_cache

    # If any directories used as volumes in docker do not exist prior to the docker run call,
    # docker will create them as root!
    makedirs_if_not_exists(infrabox_cache)
    makedirs_if_not_exists(infrabox_local_cache)

    logger.info('Recreating directories')

    recreate_dirs = [
        infrabox_work,
        infrabox_output,
        infrabox_inputs,
        infrabox_testresult,
        infrabox_coverage,
        infrabox_markup,
        infrabox_badge
    ]

    for d in recreate_dirs:
        if os.path.exists(d):
            shutil.rmtree(d)

        makedirs(d)

    job['directories'] = {
        "output": infrabox_output,
        "upload/testresult": infrabox_testresult,
        "upload/coverage": infrabox_coverage,
        "upload/markup": infrabox_markup,
        "upload/badge": infrabox_badge,
        "cache": infrabox_cache,
        "local-cache": args.local_cache,
        "job.json:ro": infrabox_job_json,
        "gosu.sh:ro": infrabox_gosu
    }

    if service:
        service_build = services[service].get('build', None)

        if service_build:
            service_build_context = service_build.get('context', None)

            if service_build_context:
                context = os.path.join(os.path.dirname(compose_file), service_build_context)
                job['directories']['context'] = context
    else:
        job['directories']['context'] = get_build_context(job, args)

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


    if os.path.exists(os.path.join(args.project_root, '.infrabox', 'inputs')):
        shutil.rmtree(os.path.join(args.project_root, '.infrabox', 'inputs'))

    for dep in job.get('depends_on', []):
        source_path = os.path.join(args.project_root, '.infrabox', 'work',
                                   'jobs', dep['job'].replace('/', '_'), 'infrabox', 'output')

        if not os.path.exists(source_path):
            continue

        dep = dep['job'].split("/")[-1]
        destination_path = os.path.join(args.project_root, '.infrabox', 'inputs', dep)

        shutil.copytree(source_path, destination_path, symlinks=True)

        job['directories']['inputs/%s' % dep] = source_path

    # Create symlinks
    recreate_sym_link(infrabox_output, os.path.join(args.project_root, '.infrabox', 'output'))
    recreate_sym_link(infrabox_upload, os.path.join(args.project_root, '.infrabox', 'upload'))
    recreate_sym_link(infrabox_cache, os.path.join(args.project_root, '.infrabox', 'cache'))

def get_secret(args, name):
    secrets_file = os.path.join(args.project_root, '.infraboxsecrets.json')
    if not os.path.exists(secrets_file):
        logger.error("No secrets file found")
        sys.exit(1)

    with open(secrets_file) as f:
        secrets = json.load(f)

        if name not in secrets:
            logger.error("%s not found in .infraboxsecrets.json" % name)
            sys.exit(1)

        return secrets[name]

def build_and_run_docker_compose(args, job):
    create_infrabox_directories(args, job)

    compose_file = os.path.join(job['infrabox_context'], job['docker_compose_file'])
    compose_file = os.path.normpath(compose_file)
    compose_file_new = compose_file + ".infrabox"

    # rewrite compose file
    compose_file_content = docker_compose.create_from(compose_file)
    for service in compose_file_content['services']:
        create_infrabox_directories(args, job,
                                    service=service,
                                    services=compose_file_content['services'],
                                    compose_file=compose_file)

        volumes = []
        for v in compose_file_content['services'][service].get('volumes', []):
            v = v.replace('/infrabox/context', args.project_root)
            volumes.append(v)

        for name, path in job['directories'].items():
            volumes.append(str('%s:/infrabox/%s' % (path, name)))

        compose_file_content['services'][service]['volumes'] = volumes

    with open(compose_file_new, "w+") as out:
        yaml.dump(compose_file_content, out, default_flow_style=False)

    env = {
        'PATH': os.environ['PATH'],
        'INFRABOX_CLI': 'true'
    }

    if 'environment' in job:
        for name, value in job['environment'].items():
            if isinstance(value, dict):
                env[name] = get_secret(args, value['$secret'])
            else:
                env[name] = value

    if not args.no_rm:
        execute(['docker-compose', '-p', args.project_name,
                 '-f', compose_file_new, 'rm', '-f'], env=env, cwd=job['build_context'])

    execute(['docker-compose', '-p', args.project_name,
             '-f', compose_file_new, 'build'], env=env, cwd=job['build_context'])

    def signal_handler(_, __):
        logger.info("Stopping docker containers")
        execute(['docker-compose', '-f', compose_file_new, 'stop'], env=env, cwd=job['build_context'])
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

    container_name = 'ib_' + job['name'].replace("/", "-")

    # Build the image
    logger.info("Build docker image")

    if not args.no_rm:
        execute(['docker', 'rm', container_name],
                cwd=args.project_root,
                ignore_error=True,
                ignore_output=True)

    docker_file = os.path.normpath(os.path.join(get_build_context(job, args),
                                                job['docker_file']))

    cmd = ['docker', 'build', '-t', image_name, '.', '-f', docker_file]
    if 'build_arguments' in job:
        for name, value in job['build_arguments'].items():
            cmd += ['--build-arg', '%s=%s' %(name, value)]

    # memory limit
    cmd += ['-m', '%sm' % job['resources']['limits']['memory']]

    execute(cmd, cwd=get_build_context(job, args))

    if 'build_only' not in job:
        return

    if job['build_only']:
        return

    # Run the continer
    cmd = ['docker', 'run', '--name', container_name]
    caps = job.get('security_context', {}).get('capabilities', {}).get('add', [])
    if caps:
        cmd += ['--cap-add=' + ','.join(caps)]

    for name, path in job['directories'].items():
        cmd += ['-v', '%s:/infrabox/%s' % (path, name)]

    cmd += ['-v', '/var/run/docker.sock:/var/run/docker.sock']
    cmd += ['-m', '%sm' % job['resources']['limits']['memory']]

    if 'environment' in job:
        for name, value in job['environment'].items():
            if isinstance(value, dict):
                cmd += ['-e', '%s=%s' % (name, get_secret(args, value['$secret']))]
            else:
                cmd += ['-e', '%s=%s' % (name, value)]

    cmd += ['-e', 'INFRABOX_CLI=true']

    if os.name != 'nt':
        cmd += ['-e', 'INFRABOX_UID=%s' % os.geteuid()]
        cmd += ['-e', 'INFRABOX_GID=%s' % os.getegid()]

    # memory limit
    cmd += ['-m', '%sm' % job['resources']['limits']['memory']]

    # CPU limit
    cmd += ['--cpus', str(job['resources']['limits']['cpu'])]

    logger.info("Run docker container")
    cmd.append(image_name)
    execute(cmd, cwd=args.project_root)

    logger.info("Commiting Container")
    execute(['docker', 'commit', container_name, image_name], cwd=args.project_root)

def get_parent_job(name):
    for job in parent_jobs:
        if job['name'] == name:
            return job

def track_as_parent(job, state, start_date=datetime.now(), end_date=datetime.now()):
    parent_jobs.append({
        "name": job['name'],
        "state": state,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "depends_on": job.get('depends_on', [])
    })

def check_if_supported(job):
    res_k8s = job['resources'].get('kubernetes', None)

    if res_k8s:
        logger.warn('Using kubernetes resources is not supported')

def build_and_run(args, job, cache):
    check_if_supported(job)

    # check if depedency conditions are met
    for dep in job.get("depends_on", []):
        on = dep['on']
        parent = get_parent_job(dep['job'])

        if not parent:
            continue

        if parent['state'] not in on:
            logger.info('Skipping job %s' % job['name'])
            track_as_parent(job, 'skipped')
            return

    job_type = job['type']
    start_date = datetime.now()

    logger.info("Starting job %s" % job['name'])

    state = 'finished'

    try:
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
    except Exception as e:
        state = 'failure'
        traceback.print_exc(file=sys.stdout)
        logger.warn("Job failed: %s" % e)
        sys.exit(1)

    if not job.get('directories', None):
        return

    # Dynamic child jobs
    infrabox_json = os.path.join(job['directories']['output'], 'infrabox.json')

    jobs = []
    if os.path.exists(infrabox_json):
        logger.info("Loading generated jobs")

        data = load_infrabox_json(infrabox_json)
        jobs = get_job_list(data, args, infrabox_context=os.path.join(args.project_root, '.infrabox', 'output'))

    end_date = datetime.now()

    track_as_parent(job, state, start_date, end_date)
    logger.info("Finished job %s" % job['name'])

    for j in jobs:
        # Prefix name with parent
        j['name'] = job['name'] + '/' + j['name']

        # Add dependencies to all root jobs
        if not j.get('depends_on', None):
            j['depends_on'] = [{"on": ["finished"], "job": job['name']}]
        else:
            dependencies = copy.deepcopy(j['depends_on'])

            for d in dependencies:
                d['job'] = job['name'] + '/' + d['job']

            j['depends_on'] = dependencies

        cache.add_job(j)

    if args.children:
        for j in jobs:
            build_and_run(args, j, cache)

def run(args):
    # Init workflow cache
    cache = WorkflowCache(args)

    # validate infrabox.json
    data = load_infrabox_json(args.infrabox_json)
    jobs = get_job_list(data, args, infrabox_context=args.project_root)

    if not args.job_name:
        # We run all jobs, so clear all cached jobs
        cache.clear()

    # Cache all jobs
    cache.add_jobs(jobs)

    for j in cache.get_jobs(job_name=args.job_name, children=args.children):
        build_and_run(args, j, cache)
