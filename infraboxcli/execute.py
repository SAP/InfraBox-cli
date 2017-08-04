import os
import subprocess

def execute(command, cwd=None, env=None, ignore_error=False, ignore_output=False):
    if env is None:
        env = os.environ

    process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, env=env, universal_newlines=True)

    # Poll process for new output until finished
    while True:
        line = process.stdout.readline()
        if not line:
            break

        if ignore_output:
            continue

        print(line.rstrip())

    process.wait()

    if ignore_error:
        return

    exitCode = process.returncode
    if exitCode != 0:
        raise Exception(exitCode)
