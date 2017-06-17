import logging
import time
import sys

from socketIO_client import SocketIO
from colorama import Fore

from infraboxcli.log import logger

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.ERROR)

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

    job_name = jobs[job_id]['name']
    color = jobs[job_id]['color']

    lines = output.splitlines()
    f = '{:%s}' % job_name_len
    for l in lines:
        print('%s%s:%s %s' % (color, f.format(job_name), Fore.RESET, l))

def show_console(build_id, args):
    logger.info("Starting console output for build %s" % build_id)
    with SocketIO(args.host) as s:
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
                            sys.exit(1)

                # wait until we received the real jobs
                if len(jobs) < 2:
                    return

                rc = 0
                active = False
                for job_id in jobs:
                    state = jobs[job_id]['state']
                    if  state == 'failure' or state == 'error':
                        rc = 1
                    elif state == 'scheduled' or state == 'queued' or state == 'running':
                        active = True

                if not active:
                    for job_id in jobs:
                        state = jobs[job_id]['state']
                        name = jobs[job_id]['name']

                        if state == 'finished':
                            logger.info("Job %s finished successfully" % state)
                        else:
                            logger.error("Job %s failed with '%s'" % (name, state))

                    sys.exit(rc)

        s.on('notify:job', on_job_update)
        s.on('notify:console', on_console_update)
        s.emit('auth:token', args.token)

        time.sleep(3)
        s.emit('listen:build', build_id)
        s.wait()
