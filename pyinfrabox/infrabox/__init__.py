import re
from builtins import int, range

from pyinfrabox import ValidationError
from pyinfrabox.utils import *

def special_match(strg, search=re.compile(r'[^a-z0-9_-]').search):
    return not bool(search(strg))

def check_name(n, path):
    check_text(n, path)
    if not special_match(n):
        raise ValidationError(path, "'%s' not a valid value" % n)

def check_name_array(a, path):
    check_string_array(a, path)

    for i in range(0, len(a)):
        n = a[i]
        check_name(n, path + ('[%s]' % i))


def check_version(v, path):
    if not isinstance(v, int):
        raise ValidationError(path, "must be an int")

    if v != 1:
        raise ValidationError(path, "unsupported version")

def parse_environment(e, path):
    if not isinstance(e, dict):
        raise ValidationError(path, "must be an object")

    for key in e:
        value = e[key]
        p = path + "." + key

        if isinstance(value, dict):
            if "$ref" not in value:
                raise ValidationError(p, "must contain a $ref")

            check_text(value['$ref'], p + ".$ref")
        else:
            try:
                check_text(value, p)
            except:
                raise ValidationError(p, "must be a string or object")


def parse_git(d, path):
    check_allowed_properties(d, path, ("type", "name", "commit", "clone_url", "depends_on", "environment"))
    check_required_properties(d, path, ("type", "name", "commit", "clone_url"))
    check_name(d['name'], path + ".name")
    check_text(d['commit'], path + ".commit")
    check_text(d['clone_url'], path + ".clone_url")

    if 'depends_on' in d:
        check_name_array(d['depends_on'], path + ".depends_on")

    if 'environment' in d:
        parse_environment(d['environment'], path + ".environment")

def parse_workflow(d, path):
    check_allowed_properties(d, path, ("type", "name", "infrabox_file", "depends_on"))
    check_required_properties(d, path, ("type", "name", "infrabox_file"))
    check_name(d['name'], path + ".name")
    check_text(d['infrabox_file'], path + ".infrabox_file")

    if 'depends_on' in d:
        check_name_array(d['depends_on'], path + ".depends_on")

def parse_security(d, path):
    check_allowed_properties(d, path, ("scan_container",))
    check_required_properties(d, path, ("scan_container",))

    if not isinstance(d['scan_container'], bool):
        raise ValidationError(path + ".scan_container", "Must be boolean")

def parse_limits(d, path):
    check_allowed_properties(d, path, ("memory", "cpu"))
    check_required_properties(d, path, ("memory", "cpu"))

    check_number(d['cpu'], path + ".cpu")
    check_number(d['memory'], path + ".memory")

    if d['cpu'] <= 0:
        raise ValidationError(path + ".cpu", "must be greater than 0")

    if d['memory'] <= 255:
        raise ValidationError(path + ".memory", "must be greater than 255")

def parse_resources(d, path):
    check_allowed_properties(d, path, ("limits",))
    check_required_properties(d, path, ("limits",))

    parse_limits(d['limits'], path + ".limits")

def parse_docker(d, path):
    check_allowed_properties(d, path, ("type", "name", "docker_file", "depends_on", "resources", "build_only", "security", "commit_after_run", "keep", "environment"))
    check_required_properties(d, path, ("type", "name", "docker_file", "resources"))
    check_name(d['name'], path + ".name")
    check_text(d['docker_file'], path + ".docker_file")
    parse_resources(d['resources'], path + ".resources")

    if 'build_only' in d:
        check_boolean(d['build_only'], path + ".build_only")

    if 'keep' in d:
        check_boolean(d['keep'], path + ".keep")

    if 'depends_on' in d:
        check_name_array(d['depends_on'], path + ".depends_on")

    if 'security' in d:
        parse_security(d['security'], path + ".security")

    if 'commit_after_run' in d:
        if not isinstance(d['commit_after_run'], bool):
            raise ValidationError(path + ".commit_after_run", "Must be boolean")

    if 'environment' in d:
        parse_environment(d['environment'], path + ".environment")

def parse_docker_compose(d, path):
    check_allowed_properties(d, path, ("type", "name", "docker_compose_file", "depends_on", "environment", "resources"))
    check_required_properties(d, path, ("type", "name", "docker_compose_file", "resources"))
    check_name(d['name'], path + ".name")
    check_text(d['docker_compose_file'], path + ".docker_compose_file")
    parse_resources(d['resources'], path + ".resources")

    if 'depends_on' in d:
        check_name_array(d['depends_on'], path + ".depends_on")

    if 'environment' in d:
        parse_environment(d['environment'], path + ".environment")

def parse_wait(d, path):
    check_allowed_properties(d, path, ("type", "name", "depends_on"))
    check_required_properties(d, path, ("type", "name"))
    check_name(d['name'], path + ".name")

    if 'depends_on' in d:
        check_name_array(d['depends_on'], path + ".depends_on")

def parse_jobs(e, path):
    if not isinstance(e, list):
        raise ValidationError(path, "must be an array")

    if not e:
        raise ValidationError(path, "must not be empty")

    for i in range(0, len(e)):
        elem = e[i]
        p = "%s[%s]" % (path, i)

        if 'type' not in elem:
            raise ValidationError(p, "does not contain a 'type'")

        t = elem['type']

        if t == 'git':
            parse_git(elem, p)
        elif t == 'wait':
            parse_wait(elem, p)
        elif t == 'workflow':
            parse_workflow(elem, p)
        elif t == 'docker':
            parse_docker(elem, p)
        elif t == 'docker-compose':
            parse_docker_compose(elem, p)
        else:
            raise ValidationError(p, "type '%s' not supported" % t)

def parse_document(d):
    check_allowed_properties(d, "#", ("version", "jobs"))
    check_required_properties(d, "#", ("version", "jobs"))

    check_version(d['version'], "#version")
    parse_jobs(d['jobs'], "#jobs")

def validate_json(d):
    parse_document(d)

    jobs = {}
    for i in range(0, len(d['jobs'])):
        job = d['jobs'][i]
        job_name = job['name']

        path = "#jobs[%s]" % i

        if jobs.get(job_name, None):
            raise ValidationError(path + ".name", "Job name '%s' already exists" % job_name)

        if job_name == 'Create Jobs':
            raise ValidationError(path + ".name", "Job name may not be 'Create Jobs'")

        jobs[job_name] = job

        if 'depends_on' not in job:
            continue

        deps = {}
        for depends_on in job['depends_on']:
            if job_name == depends_on:
                raise ValidationError(path, "Job '%s' may not depend on itself" % depends_on)

            if depends_on not in jobs:
                raise ValidationError(path + ".depends_on", "Job '%s' not found" % depends_on)

            if depends_on in deps:
                raise ValidationError(path + ".depends_on", "'%s' duplicate dependencies" % depends_on)

            deps[depends_on] = True

    return True
