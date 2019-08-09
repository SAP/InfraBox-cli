import logging
import sys

from colorama import Fore

import infraboxcli
from ..log import logger

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.WARNING)

colors = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]

job_name_len = 0
jobs = {}


def on_console_update(*args):
    u = args[0]
    job_id = u['job_id']
    output = u['data']

    if not output:
        return

    job_name = jobs[job_id]['name']
    color = jobs[job_id]['color']

    lines = output.splitlines()
    f = '{:%s}' % job_name_len
    for l in lines:
        print('%s%s:%s %s' % (color, f.format(job_name), Fore.RESET, l))


def on_disconnect(*_args):
    logger.info('Disconnected')


def show_console(project_id, build_id):
    logger.info("Starting console output for build " + build_id)

    with infraboxcli.CLI_SETTINGS.get_api().create_socket(project_id) as s:
        def on_job_update(*args):
            u = args[0]['data']
            job = u['job']
            job_id = job['id']

            if job_id not in jobs:
                s.emit('listen:console', job_id)
                color = colors[len(jobs) % len(colors)]
                job['color'] = color
                jobs[job_id] = job
                global job_name_len
                job_name_len = max(job_name_len, len(job['name']))
            else:
                jobs[job_id]['state'] = job['state']

                # no jobs yet
                if not jobs:
                    return

                # check if create job failed
                if len(jobs) == 1:
                    for job_id in jobs:
                        state = jobs[job_id]['state']
                        name = jobs[job_id]['name']
                        if state == 'failure' or state == 'error' or state == 'killed':
                            logger.error("Job %s failed with '%s'" % (name, state))

                # wait until we received the real jobs
                if len(jobs) < 2:
                    return

                active = False
                for job_id in jobs:
                    state = jobs[job_id]['state']
                    if state in ('scheduled', 'queued', 'running'):
                        active = True

                if active:
                    return

                for job_id in jobs:
                    state = jobs[job_id]['state']
                    name = jobs[job_id]['name']

                    if state == 'finished':
                        logger.info("Job %s finished successfully" % name)
                    else:
                        logger.error("Job %s failed with '%s'" % (name, state))

        s.on('disconnect', on_disconnect)
        s.on('notify:job', on_job_update)
        s.on('notify:console', on_console_update)

        s.emit('listen:build', build_id)
        s.wait()
