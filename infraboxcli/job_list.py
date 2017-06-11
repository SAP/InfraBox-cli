import os
import json
import sys
import subprocess
import signal
import shutil
import uuid

from builtins import range
from pyinfrabox.infrabox import validate_json
from infraboxcli.execute import execute

def load_infrabox_json(path):
    with open(path) as f:
        data = json.load(f)
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


def get_job_list(data, args, parents=[], base_path=None):
    jobs = []
    parent_name = get_parent_name(parents)

    for job in data['jobs']:
        job['id'] = str(uuid.uuid4())
        job['avg_duration'] = 0
        job['parents'] = parents
        job['base_path'] = base_path

        if parent_name != '':
            job['name'] = parent_name + "/" + job['name']

            deps = job.get('depends_on', [])
            for x in range(0, len(deps)):
                deps[x] = parent_name + "/" + deps[x]

        job_name = job['name']

        if job['type'] != "workflow" and job['type'] != 'git':
            jobs.append(job)
            continue

        new_parents = parents[:]
        new_parents.append(job_name)

        if job['type'] == "git":
            repo_path = os.path.join('/tmp', job_name)
            execute(['rm', '-rf', repo_path])
            execute(['git', 'clone', '--depth=50', job['clone_url'], repo_path])
            execute(['git', 'checkout', job['commit']], cwd=repo_path)

            data = load_infrabox_json(os.path.join(repo_path, 'infrabox.json'))
            sub = get_job_list(data, args, new_parents, base_path=repo_path)
        else:
            p = os.path.join(base_path, job['infrabox_file'])
            bp = os.path.dirname(p)
            data = load_infrabox_json(p)
            sub = get_job_list(data, args, new_parents, base_path=bp)

        # every sub job which does not have a parent
        # should be a child of the current job
        job_with_children = {}
        for s in sub:
            deps = s.get('depends_on', [])
            if len(deps) == 0:
                s['depends_on'] = job.get('depends_on', [])

            for d in deps:
                job_with_children[d] = True

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
                final_job['depends_on'].append(sub_name)

        jobs.append(final_job)

    return jobs
