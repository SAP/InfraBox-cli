import os
import json
import signal
import shutil
import sys
import stat
from datetime import datetime
import traceback
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
    job_dir = os.path.join(args.project_root, '.infraboxwork', 'jobs', job_name)
    job_git_source = os.path.join(job_dir, 'git_source')
    infrabox = os.path.join(job_dir, 'infrabox')
    infrabox_cache = os.path.join(infrabox, 'cache')
    infrabox_output = os.path.join(infrabox, 'output')
    infrabox_inputs = os.path.join(infrabox, 'inputs')
    infrabox_testresult = os.path.join(infrabox, 'upload', 'testresult')
    infrabox_markup = os.path.join(infrabox, 'upload', 'markup')
    infrabox_badge = os.path.join(infrabox, 'upload', 'badge')
    infrabox_job_json = os.path.join(infrabox, 'job.json')
    infrabox_gosu = os.path.join(infrabox, 'gosu.sh')
    infrabox_context = os.path.join(args.project_root)

    if not os.path.exists(args.local_cache):
        makedirs(infrabox_cache)

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
        "upload/testresult": infrabox_testresult,
        "upload/markup": infrabox_markup,
        "upload/badge": infrabox_badge,
        "cache": infrabox_cache,
        "local-cache": args.local_cache,
        "context": infrabox_context,
        "job.json": infrabox_job_json,
        "gosu.sh": infrabox_gosu
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

    with open(infrabox_gosu, 'w') as out:
        out.write('''
#!/bin/sh
USER_ID=${INFRABOX_UID:-9001}
GROUP_ID=${INFRABOX_GID:-9001}

echo "Starting with UID:GID: $USER_ID:$GROUP_ID"
addgroup -g $GROUP_ID infrabox
adduser -D -u $USER_ID -G infrabox infrabox
#useradd --shell /bin/bash -u $USER_ID -o -c "" -m infrabox
export HOME=/home/infrabox

exec su-exec infrabox "$@"
''')
        st = os.stat(infrabox_gosu)
        os.chmod(infrabox_gosu, st.st_mode | stat.S_IEXEC)

    # Inputs
    repo_infrabox = os.path.join(args.project_root, '.infrabox')
    if os.path.exists(repo_infrabox):
        shutil.rmtree(repo_infrabox)

    for dep in job.get('depends_on', []):
        source_path = os.path.join(args.project_root, '.infraboxwork',
                                   'jobs', dep['job'], 'infrabox', 'output')
        dep = dep['job'].split("/")[-1]

        # Copy to .infrabox so we can use it in a COPY/ADD instruction
        destination_path = os.path.join(repo_infrabox, 'inputs', dep)

        if os.path.exists(source_path):
            shutil.copytree(source_path, destination_path, symlinks=True)

        # Mount to /infrabox/inputs
        job['directories']['inputs/%s' % dep] = source_path

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
    compose_file = os.path.join(job['base_path'], job['docker_compose_file'])
    compose_file_new = compose_file + ".infrabox"

    # rewrite compose file
    compose_file_content = docker_compose.create_from(compose_file)
    for service in compose_file_content['services']:
        create_infrabox_directories(args, job, service=service)

        volumes = []
        for name, path in job['directories'].items():
            volumes.append(str('%s:/infrabox/%s' % (path, name)))

        compose_file_content['services'][service]['volumes'] = volumes

    with open(compose_file_new, "w+") as out:
        yaml.dump(compose_file_content, out, default_flow_style=False)

    env = {"PATH": os.environ['PATH']}

    if 'environment' in job:
        for name, value in job['environment'].iteritems():
            if isinstance(value, dict):
                env[name] = get_secret(args, value['$ref'])
            else:
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

    if 'build_only' not in job:
        return

    if job['build_only']:
        return

    cmd = ['docker', 'run', '--name', container_name]

    for name, path in job['directories'].items():
        cmd += ['-v', '%s:/infrabox/%s' % (path, name)]

    cmd += ['-v', '/var/run/docker.sock:/var/run/docker.sock']
    cmd += ['-m', '%sm' % job['resources']['limits']['memory']]

    if 'environment' in job:
        for name, value in job['environment'].iteritems():
            if isinstance(value, dict):
                cmd += ['-e', '%s=%s' % (name, get_secret(args, value['$ref']))]
            else:
                cmd += ['-e', '%s=%s' % (name, value)]

    cmd += ['-e', 'INFRABOX_UID=%s' % os.geteuid()]
    cmd += ['-e', 'INFRABOX_GID=%s' % os.getegid()]

    cmd.append(image_name)

    logger.info("Run docker container")
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

def build_and_run(args, job):
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

    # Dynamic child jobs
    infrabox_json = os.path.join(job['directories']['output'], 'infrabox.json')

    jobs = []
    if os.path.exists(infrabox_json):
        logger.info("Loading generated jobs")

        data = load_infrabox_json(infrabox_json)
        jobs = get_job_list(data, args, base_path=args.project_root)

    end_date = datetime.now()

    track_as_parent(job, state, start_date, end_date)
    logger.info("Finished job %s" % job['name'])

    for j in jobs:
        if not j.get('depends_on', None):
            j['depends_on'] = [{"on": ["finished"], "job": job['name']}]

        build_and_run(args, j)

def run(args):
    # validate infrabox.json
    data = load_infrabox_json(args.infrabox_json)
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
