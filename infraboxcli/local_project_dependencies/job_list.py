import json
import os
import uuid

import yaml

from infraboxcli.local_project_dependencies.FilesValidation import validate_json
from .execute import execute
from ..log import logger

LOADED_FILES = {}


def load_infrabox_file(path):
    if path in LOADED_FILES:
        logger.error('Recursive included detected with %s' % path)

    LOADED_FILES[path] = path

    with open(path) as f:
        try:
            data = json.load(f)
        except ValueError:
            f.seek(0)
            data = yaml.load(f)
        validate_json(data)
        return data


def get_parent_name(parents):
    name = ""
    for i in range(0, len(parents)):
        p = parents[i]

        if i > 0:
            name += '/'

        name += p

    return name


def rewrite_job_dependencies(job):
    # rewrite depends_on from
    # "jobname" -> {"job": "jobname", "on": ["finished"]}
    # "*" => ["finished", "error", "failure"]
    if 'depends_on' in job:
        for x in range(0, len(job['depends_on'])):
            dep = job['depends_on'][x]
            if not isinstance(dep, dict):
                job['depends_on'][x] = {"job": dep, "on": ["finished"]}
            else:
                for o in dep['on']:
                    if o != "*":
                        continue

                    job['depends_on'][x] = {
                        "job": dep['job'],
                        "on": ["finished", "error", "failure", "skipped"]
                    }


def get_job_list(data, infrabox_context=None):
    jobs = []
    parents = []

    parent_name = get_parent_name(parents)

    for job in data['jobs']:
        job['id'] = str(uuid.uuid4())
        job['parents'] = parents
        job['infrabox_context'] = os.path.normpath(infrabox_context)

        if 'build_context' in job:
            job['build_context'] = os.path.normpath(os.path.join(infrabox_context, job['build_context']))
        else:
            job['build_context'] = os.path.normpath(infrabox_context)

        if parent_name != '':
            job['name'] = parent_name + "/" + job['name']

            deps = job.get('depends_on', [])
            for x in range(0, len(deps)):
                dep = deps[x]
                if isinstance(dep, dict):
                    dep = dep['job']

                deps[x] = parent_name + "/" + dep

        rewrite_job_dependencies(job)

        job_name = job['name']

        if job['type'] != "workflow" and job['type'] != 'git':
            jobs.append(job)
            continue

        new_parents = parents[:]
        new_parents.append(job_name)

        if job['type'] == "git":
            repo_path = os.path.join('/tmp', job_name)
            clone_branch = job.get('branch', None)
            execute(['rm', '-rf', repo_path])
            if clone_branch:
                execute(['git', 'clone', '--depth=50', '--branch', clone_branch, job['clone_url'], repo_path])
            else:
                execute(['git', 'clone', '--depth=50', job['clone_url'], repo_path])
            execute(['git', 'config', 'remote.origin.url', job['clone_url']], cwd=repo_path)
            execute(['git', 'config', 'remote.origin.fetch', '+refs/heads/*:refs/remotes/origin/*'], cwd=repo_path)
            execute(['git', 'fetch', 'origin', job['commit']], cwd=repo_path)

            execute(['git', 'checkout', job['commit']], cwd=repo_path)

            ib_path = os.path.join(repo_path, job.get('infrabox_file', 'infrabox.json'))
            if not os.path.exists(ib_path):
                ib_path = os.path.join(repo_path, job.get('infrabox_file', 'infrabox.yaml'))

            data = load_infrabox_file(ib_path)
            sub = get_job_list(data, infrabox_context=os.path.dirname(ib_path))

            # Set the build context to dirname of the infrabox.json
            # if not build context is specified
            for s in sub:
                if 'build_context' not in s:
                    s['build_context'] = os.path.normpath(os.path.dirname(ib_path))

        else:
            p = os.path.join(infrabox_context, job['infrabox_file'])
            p = os.path.normpath(p)
            data = load_infrabox_file(p)
            sub = get_job_list(data, infrabox_context=os.path.dirname(p))

        # every sub job which does not have a parent
        # should be a child of the current job
        job_with_children = {}
        for s in sub:
            deps = s.get('depends_on', [])
            if not deps:
                s['depends_on'] = job.get('depends_on', [])

            for d in deps:
                job_with_children[d['job']] = True

        jobs += sub

        # add a wait job to all sub jobs
        # which don't have a child, so we have
        # one 'final' job
        final_job = {
            "type": "wait",
            "name": job_name,
            "depends_on": [],
            "id": str(uuid.uuid4()),
            "parents": new_parents
        }

        for s in sub:
            sub_name = s['name']
            if sub_name not in job_with_children:
                final_job['depends_on'].append({"job": sub_name, "on": ["finished"]})

        jobs.append(final_job)

    return jobs
