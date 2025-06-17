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

        if args.infrabox_file:
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
                        if 'name' in p:
                            jobs += self.get_jobs(p['name'], children)
                        if 'job' in p:
                            jobs += self.get_jobs(p['job'], children)

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
        jobs = sorted(self.jobs, key=lambda k: k['name'])
        for j in jobs:
            print(j['name'])

    def print_graph(self):
        index = {}
        def place(index, name, job):
            if name.startswith('/'):
                name = name[1:]

            if name == "":
                index[""] = job
                return

            prefix = name.split('/')[0]
            if prefix not in index:
                index[prefix] = {}
            place(index[prefix], name[len(prefix):], job)

        for job in self.jobs:
            place(index, job['name'], job)

        print('digraph "Jobs" {')

        def print_cluster(name, cluster, indent='  '):
            if 'name' in cluster:
                # then this is a job and not a cluster
                print('{indent}"{name}" [label="{label}" shape=box]'.format(
                    name=cluster['name'],
                    label=cluster['name'].split('/')[-1],
                    indent=indent))
            elif len(cluster) == 1:
                if (sys.version_info.major == 2):
                    for inner_name, inner_cluster in cluster.iteritems():
                        print_cluster(inner_name, inner_cluster, indent)
                elif (sys.version_info.major == 3):
                    for inner_name, inner_cluster in cluster.items():
                        print_cluster(inner_name, inner_cluster, indent)
                else:
                    raise Exception('Unsupport python version')
            else:
                print('{indent}subgraph "cluster_{name}" {{'.format(name=name, indent=indent))

                if (sys.version_info.major == 2):
                    for inner_name, inner_cluster in cluster.iteritems():
                        print_cluster(inner_name, inner_cluster, indent + '  ')
                elif (sys.version_info.major == 3):
                    for inner_name, inner_cluster in cluster.items():
                        print_cluster(inner_name, inner_cluster, indent + '  ')
                else:
                    raise Exception('Unsupport python version')

                print('{indent}}}'.format(indent=indent))

        if (sys.version_info.major == 2):
            for name, cluster in index.iteritems():
                print_cluster(name, cluster)
        elif (sys.version_info.major == 3):
            for name, cluster in index.items():
                print_cluster(name, cluster)
        else:
            raise Exception('Unsupport python version')

        for j in self.jobs:
            name = j['name']

            for dep in j.get('depends_on', []):
                if isinstance(dep, str):
                    print('  "{a}" -> "{b}"'.format(a=dep, b=name))
                else:
                    print('  "{a}" -> "{b}" [label="{on}"]'.format(
                        a=dep['job'],
                        b=name,
                        on=", ".join(dep['on'])))

        print('}')
