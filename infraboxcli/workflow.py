import os
import json
import sys

from infraboxcli.log import logger

class WorkflowCache(object):
    def __init__(self, args):
        self.jobs = []
        self.persist = True

        work_dir = os.path.join(args.project_root, '.infrabox', 'work')

        if not os.path.exists(work_dir):
            os.makedirs(work_dir)

        self.infrabox_full_workflow = os.path.join(work_dir, 'full_workflow.json')

        if os.path.exists(self.infrabox_full_workflow):
            with open(self.infrabox_full_workflow) as f:
                data = json.load(f)
                self.jobs = data['jobs']

        if args.infrabox_json_file:
            # a infrabox.json file was specified with -f
            # so we don't persist the cache to not overwrite
            # the full workflow graph
            self.persist = False
            self.jobs = []

    def clear(self):
        if os.path.exists(self.infrabox_full_workflow):
            os.remove(self.infrabox_full_workflow)

        self.jobs = []

    def get_jobs(self, job_name=None, children=False):
        if not job_name:
            return self.jobs

        jobs = []
        for j in self.jobs:
            if j['name'] == job_name:
                jobs.append(j)

                if children:
                    for p in j.get('depends_on', []):
                        jobs += self.get_jobs(p['name'], children)

        if not jobs:
            logger.error("job %s not found in infrabox.json" % job_name)
            sys.exit(1)

        return jobs

    def add_jobs(self, jobs):
        for j in jobs:
            self.add_job(j)

    def add_job(self, job):
        updated = False

        for i in range(0, len(self.jobs)):
            if self.jobs[i]['name'] == job['name']:
                updated = True
                self.jobs[i] = job
                break

        if not updated:
            self.jobs.append(job)

        self._write()

    def _write(self):
        if not self.persist:
            return

        with open(self.infrabox_full_workflow, 'w') as out:
            json.dump({'version': 1, 'jobs': self.jobs}, out, indent=4)

    def print_tree(self):
        for j in self.jobs:
            print (j['name'])
