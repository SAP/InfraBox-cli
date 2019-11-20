import requests
from socketIO_client import SocketIO

from .TokenManager import TokenKind
from .Utils import InfraBoxAPIException


class InfraBoxAPI(object):
    """
    All parameters are strings by default.
    If not, it will be specified in the doc string.
    """
    # https://rebilly.github.io/ReDoc/?url=https://infrabox.ninja/api/swagger.json
    API_POSTFIX = 'api/v1/{url}'

    def __init__(self, url, token_manager, ca_bundle=False):
        self._url = url
        self._token_manager = token_manager
        self._ca_bundle = ca_bundle

        # Disabling warning if no bundle has been given
        if not ca_bundle:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_api_url(self, api, **kwargs):
        return self._url + '/' + self.API_POSTFIX.format(url=api.format(**kwargs))

    @staticmethod
    def _check_status_code(response):
        if response.status_code != 200:
            raise ServerErrorException(response.json()["message"], response.status_code)

    def _check_url(self):
        if not self._url:
            raise ServerErrorException("Please specify the remote's URL.", 500)

    def _do_get(self, api, params=None, token_kind=None, as_type="json", **kwargs):

        token = self._token_manager.get_token(token_kind, kwargs.get("project_id"))
        response = requests.get(url=self.get_api_url(api, **kwargs),
                                params=params,
                                verify=self._ca_bundle,
                                cookies=token)
        self._check_status_code(response)

        if as_type == "json":
            return response.json()
        elif as_type == "content":
            return response.content
        elif as_type == "cookies":
            return response.cookies

    def _do_post(self, api, params=None, token_kind=None, json=None, files=None, as_type="json", **kwargs):
        token = self._token_manager.get_token(token_kind, kwargs.get("project_id"))
        response = requests.post(url=self.get_api_url(api, **kwargs),
                                 params=params,
                                 json=json,
                                 files=files,
                                 verify=self._ca_bundle,
                                 cookies=token)
        self._check_status_code(response)

        if as_type == "json":
            return response.json()
        elif as_type == "content":
            return response.content
        elif as_type == "cookies":
            return response.cookies

    def _do_delete(self, api, token_kind=None, **kwargs):
        token = self._token_manager.get_token(token_kind, kwargs.get("project_id"))
        response = requests.delete(url=self.get_api_url(api, **kwargs),
                                   verify=self._ca_bundle,
                                   cookies=token)
        self._check_status_code(response)
        return response.json()

    def _do_put(self, api, data=None, token_kind=None, **kwargs):
        token = self._token_manager.get_token(token_kind, kwargs.get("project_id"))
        response = requests.put(url=self.get_api_url(api, **kwargs), data=data,
                                verify=self._ca_bundle,
                                cookies=token)
        self._check_status_code(response)
        return response.json()

    # ------------------------------------------------------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------------------------------------------------------

    def login(self, email, password):
        return self._do_post('account/login', json={"email": email, "password": password},
                             as_type="cookies", token_kind=TokenKind.USER)

    def create_account(self, username, email, password1, password2):
        return self._do_post('account/register',
                             json={"username": username, "email": email,
                                   "password1": password1, "password2": password2},
                             as_type="cookies")

    # ------------------------------------------------------------------------------------------------------------------
    # Builds
    # ------------------------------------------------------------------------------------------------------------------

    def get_builds(self, project_id):
        from v2infraboxapi import Build
        build_dicts = self._do_get('projects/{project_id}/builds/', project_id=project_id, token_kind=TokenKind.PULL)

        builds = []
        for build_dict in build_dicts:
            build = Build(project_id,
                          build_dict["id"],
                          build_number=build_dict["build_number"],
                          restart_counter=build_dict["restart_counter"])
            builds.append(build)

        return builds

    def get_build(self, project_id, build_id):
        from v2infraboxapi import Build
        ans = self._do_get('projects/{project_id}/builds/{build_id}',
                           project_id=project_id, build_id=build_id, token_kind=TokenKind.PULL)

        # Checks that there was no server error
        if not ans:
            raise ServerErrorException(
                "ERROR: build not found: project_id={}, build_id={}".format(project_id, build_id), 500)

        return Build(project_id, build_id, ans[0]["build_number"], ans[0]["restart_counter"])

    def abort_build(self, project_id, build_id):
        return self._do_get('projects/{project_id}/builds/{build_id}/abort',
                            project_id=project_id, build_id=build_id, token_kind=TokenKind.USER)

    def clear_build_cache(self, project_id, build_id):
        return self._do_get('projects/{project_id}/builds/{build_id}/cache/clear',
                            project_id=project_id, build_id=build_id, token_kind=TokenKind.USER)

    def get_jobs_for_build(self, project_id, build_number, restart_counter="1"):
        """Returns (jobs, commit_dict, is_cronjob)"""
        from v2infraboxapi import Job
        answers = self._do_get('projects/{project_id}/builds/{build_number}/{restart_counter}',
                               project_id=project_id,
                               build_number=build_number,
                               restart_counter=restart_counter,
                               token_kind=TokenKind.USER)

        # Checks that there was no server error
        if "message" in answers:
            raise InfraBoxAPIException(
                "ERROR: Jobs not found: project_id={}, build_id={}".format(project_id, id))

        if not answers:
            raise InfraBoxAPIException(
                "ERROR: No jobs for: project_id={}, build_id={}".format(project_id, id))

        # FIXME key mismatch between REST calls
        for ans in answers:
            ans["job"]["depends_on"] = ans["job"]["dependencies"]

        return Job.from_REST_API_dicts([ans["job"] for ans in answers], project_id), answers[0]["commit"], \
               answers[0]["build"].get("is_cronjob", False)  # Cronjob not available?

    def restart_build(self, project_id, build_id):
        return self._do_get('projects/{project_id}/builds/{build_id}/restart',
                            project_id=project_id, build_id=build_id, token_kind=TokenKind.USER)

    def create_socket(self, project_id):
        """Creates a socket to stream the results for a build push."""
        try:
            return SocketIO(self.get_api_url('socket.io'),
                            cookies=self._token_manager.get_token(TokenKind.PUSH, project_id),
                            wait_for_connection=False,
                            verify=self._ca_bundle)
        except Exception as e:
            raise ServerErrorException(e.message, 401)

    # ------------------------------------------------------------------------------------------------------------------
    # Collaborators
    # ------------------------------------------------------------------------------------------------------------------

    def add_collaborator(self, project_id, username, role):
        return self._do_post('projects/{project_id}/collaborators/',
                             project_id=project_id, json={"role": role, "username": username},
                             token_kind=TokenKind.USER)

    def get_collaborators(self, project_id):
        from v2infraboxapi.DataStructures import Collaborator
        return Collaborator.from_REST_API_dicts(self._do_get('projects/{project_id}/collaborators/',
                                                             project_id=project_id, token_kind=TokenKind.USER))

    def get_collaborator_roles(self, project_id):
        """Returns all the possible roles for a collaborator."""
        from v2infraboxapi.DataStructures import CollaboratorRole
        return [CollaboratorRole.from_string(role) for role in
                self._do_get('projects/{project_id}/collaborators/roles',
                             project_id=project_id, token_kind=TokenKind.USER)]

    def put_collaborator(self, project_id, user_id, role):
        """Changes a collaborator's role."""
        return self._do_get('projects/{project_id}/collaborators/{user_id}',
                            project_id=project_id, user_id=user_id, data={"role": role}, token_kind=TokenKind.USER)

    def delete_collaborator(self, project_id, user_id):
        return self._do_delete('projects/{project_id}/collaborators/{user_id}',
                               project_id=project_id, user_id=user_id, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # Commits
    # ------------------------------------------------------------------------------------------------------------------

    # def get_builds_commit(self, project_id, commit_id):
    #     """Returns a project's commit."""
    #     return self._do_get('projects/{project_id}/commits/{commit_id}',
    #                         project_id=project_id, commit_id=commit_id, token_kind=TokenKind.PULL)

    # ------------------------------------------------------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------------------------------------------------------
    def get_jobs_for_last_builds(self, project_id, from_nb=None, to_nb=None):
        """Returns the jobs for the build numbers FROM_NB to TO_NB. By default, for the last 10 builds."""
        from v2infraboxapi import Build, Job
        url = 'projects/{project_id}/jobs/?' + \
              ('from={}' if from_nb is not None else '') + \
              ('&' if from_nb is not None and to_nb is not None else '') + \
              ('to={}'.format(to_nb) if to_nb is not None else '')
        info_dicts = self._do_get(url, project_id=project_id, token_kind=TokenKind.PULL)
        build_dicts = dict()

        for info_dict in info_dicts:
            # FIXME key mismatch between REST calls
            info_dict["job"]["depends_on"] = info_dict["job"]["dependencies"]

            build_id = info_dict["build"]["id"]
            if build_id not in build_dicts:
                build = info_dict["build"]
                build_dicts[build_id] = build
                build["project_id"] = project_id
                build["commit"] = info_dict["commit"]
                build["jobs"] = []

            build_dicts[build_id]["jobs"].append(Job.from_REST_API_dict(info_dict["job"], project_id))

        builds = []
        for build_dict in build_dicts.values():
            build = Build(project_id,
                          build_dict["id"],
                          build_number=build_dict["build_number"],
                          restart_counter=build_dict["restart_counter"],
                          is_cronjob=build_dict.get("is_cronjob", False),  # Cronjob not available?
                          jobs=build_dict["jobs"],
                          commit=build_dict["commit"])

            # Computing the status and the duration
            build.compute_jobs_related_information()
            builds.append(build)
        return sorted(builds, key=lambda b: int(b.build_number), reverse=True)

    def get_job_output(self, project_id, job_id):
        """
        Returns the the content of /infrabox/output of the job (as .tar.gz).
        The server gives you a 404 error if there is no output for this job.
        """
        return self._do_get('projects/{project_id}/jobs/{job_id}/output',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL, as_type="content")

    # Not listed in the swagger doc
    def get_job_manifest(self, project_id, job_id):
        """
        Returns the the job's data (like get_job), image, output and dependencies.
        Pls be careful if you want to get a job's output: same remark as for get_job_output.
        Why you may ask? Well if it ware that easy, why would we get paid?
        The server gives you back an URL to get the output for each dependency, but like any "get_job_output" call,
        THis might result in a 404 error and don't let the "The requested URL was not found on the server. If you
        entered the URL manually please check your spelling and try again" fool you.
        """
        return self._do_get('projects/{project_id}/jobs/{job_id}/manifest',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL)

    # Not listed in the swagger doc
    def abort_job(self, project_id, job_id):
        """Aborts the job."""
        return self._do_get('projects/{project_id}/jobs/{job_id}/abort',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.USER)

    # Not listed in the swagger doc
    def get_job_stats(self, project_id, job_id):
        """Returns the the job's stats"""
        return self._do_get('projects/{project_id}/jobs/{job_id}/stats',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL)

    def get_jobs(self, project_id, build_id):
        from v2infraboxapi.DataStructures import Job
        return Job.from_REST_API_dicts(self._do_get('projects/{project_id}/builds/{build_id}/jobs/',
                                                    project_id=project_id,
                                                    build_id=build_id,
                                                    token_kind=TokenKind.PULL),
                                       project_id)

    def get_job(self, project_id, job_id):
        from v2infraboxapi.DataStructures import Job
        return Job.from_REST_API_dict(self._do_get('projects/{project_id}/jobs/{job_id}',
                                                   project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL),
                                      project_id)

    def get_job_archive(self, project_id, job_id):
        """Gets a list of files in a job's archive."""
        return self._do_get('projects/{project_id}/jobs/{job_id}/archive',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL)

    def download_job_archive(self, project_id, job_id, filename):
        return self._do_get('projects/{project_id}/jobs/{job_id}/archive/download/?filename={filename}',
                            project_id=project_id, job_id=job_id, filename=filename,
                            token_kind=TokenKind.PULL, as_type="content")

    def get_job_badges(self, project_id, job_id):
        return self._do_get('projects/{project_id}/jobs/{job_id}/badges',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL, as_type="content")

    def clear_job_cache(self, project_id, job_id):
        return self._do_get('projects/{project_id}/jobs/{job_id}/cache/clear',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.USER)

    def get_job_console_log(self, project_id, job_id):
        return self._do_get('projects/{project_id}/jobs/{job_id}/console',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.PULL, as_type="content")

    def restart_job(self, project_id, job_id):
        return self._do_get('projects/{project_id}/jobs/{job_id}/restart',
                            project_id=project_id, job_id=job_id, token_kind=TokenKind.USER)

    def get_testruns(self, project_id, job_id):
        from v2infraboxapi.DataStructures import Testrun
        return Testrun.from_REST_API_dicts(self._do_get('projects/{project_id}/jobs/{job_id}/testruns',
                                                        project_id=project_id, job_id=job_id,
                                                        token_kind=TokenKind.PULL))

    # ------------------------------------------------------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------------------------------------------------------
    # Not listed in the swagger doc
    def get_projects(self):
        """Returns the user's projects."""
        from v2infraboxapi.DataStructures import Project
        return Project.from_REST_API_dicts(self._do_get('projects', token_kind=TokenKind.USER))

    # Not listed in the swagger doc
    def get_project_by_name(self, name):
        """Returns a project by name."""
        from v2infraboxapi.DataStructures import Project
        return Project.from_REST_API_dict(self._do_get('projects/name/{name}', name=name, token_kind=TokenKind.USER))

    def create_project(self, name, project_type, private, github_repo_name=""):
        """
        :type name: str
        :param name: >= 3 characters and regex: r"^[0-9a-zA-Z_\\-/]+$"
        :type project_type: str
        :param project_type: "upload" or "gerrit" or "github"
        :type private: bool
        :type github_repo_name: str
        :param github_repo_name: only useful if the project is of type "github"
        """
        return self._do_post('projects/',
                             json={"github_repo_name": github_repo_name, "type": project_type,
                                   "name": name, "private": private},
                             token_kind=TokenKind.USER)

    def delete_project(self, project_id):
        return self._do_delete('projects/{project_id}', project_id=project_id, token_kind=TokenKind.USER)

    def get_project(self, project_id):
        from v2infraboxapi.DataStructures import Project
        return Project.from_REST_API_dict(self._do_get('projects/{project_id}',
                                                       project_id=project_id, token_kind=TokenKind.USER))

    def get_project_badge(self, project_id):
        return self._do_get('projects/{project_id}/badge.svg',
                            project_id=project_id, token_kind=TokenKind.USER, as_type="content")

    def get_project_state_badge(self, project_id):
        return self._do_get('projects/{project_id}/state.svg',
                            project_id=project_id, token_kind=TokenKind.USER, as_type="content")

    def get_project_tests_badge(self, project_id):
        return self._do_get('projects/{project_id}/tests.svg',
                            project_id=project_id, token_kind=TokenKind.USER, as_type="content")

    def upload_project(self, project_id, project_files):
        return self._do_post('projects/{project_id}/upload/',
                             project_id=project_id, token_kind=TokenKind.PUSH, files={'project.zip': project_files})

    def trigger_new_build(self, project_id, branch_or_sha, env=None):
        """
        :type project_id: str
        :param branch_or_sha: branch name or commit's sha
        :param env: Array of object (EnvVar) [{"name": "string", "value": "string"}]
        """

        data = {'branch_or_sha': branch_or_sha}
        if env is not None:
            data['env'] = env
        return self._do_post('projects/{project_id}/trigger',
                             project_id=project_id, json=data, token_kind=TokenKind.PUSH)

    def change_project_visibility(self, project_id, private):
        """
        :type project_id: str
        :type private: bool
        """

        return self._do_post('projects/{project_id}/visibility/',
                             project_id=project_id, json={"private": private}, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # Secrets
    # ------------------------------------------------------------------------------------------------------------------

    def create_secret(self, project_id, name, value):
        """
        :type project_id: str
        :type name: str
        :param name: <= 255 characters
        :type value: str
        :param value: <= 255 characters
        """
        return self._do_post('projects/{project_id}/secrets/',
                             project_id=project_id, json={"name": name, "value": value}, token_kind=TokenKind.USER)

    def get_projects_secrets(self, project_id):
        from v2infraboxapi.DataStructures import Secret
        return Secret.from_REST_API_dicts(self._do_get('projects/{project_id}/secrets/',
                                                       project_id=project_id, token_kind=TokenKind.USER))

    def delete_secret(self, project_id, secret_id):
        return self._do_delete('projects/{project_id}/secrets/{secret_id}',
                               project_id=project_id, secret_id=secret_id, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # Tokens
    # ------------------------------------------------------------------------------------------------------------------

    def create_token(self, project_id, description, scope_push, scope_pull):
        """
        :type project_id: str
        :type description: str
        :type scope_push: bool
        :type scope_pull: bool
        """
        data = {"scope_push": scope_push, "scope_pull": scope_pull, "description": description}

        return self._do_post('projects/{project_id}/tokens/',
                             project_id=project_id, json=data, token_kind=TokenKind.USER)

    def get_projects_tokens(self, project_id):
        from v2infraboxapi.DataStructures import Token
        return Token.from_REST_API_dicts(self._do_get('projects/{project_id}/tokens/',
                                                      project_id=project_id, token_kind=TokenKind.USER))

    def delete_token(self, project_id, token_id):
        return self._do_delete('projects/{project_id}/tokens/{token_id}',
                               project_id=project_id, token_id=token_id, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # CronJobs
    # ------------------------------------------------------------------------------------------------------------------

    def create_cronjob(self, project_id, name, minute, hour, day_of_month, month, day_of_week, sha, infrabox_file):
        return self._do_post('projects/{project_id}/cronjobs',
                             project_id=project_id, token_kind=TokenKind.USER,
                             json={"name": name, "minute": minute, "hour": hour, "day_month": day_of_month,
                                   "month": month, "day_week": day_of_week, "sha": sha, "infrabox_file": infrabox_file})

    def get_projects_cronjobs(self, project_id):
        from v2infraboxapi.DataStructures import Cronjob
        return Cronjob.from_REST_API_dicts(self._do_get('projects/{project_id}/cronjobs',
                                                        project_id=project_id, token_kind=TokenKind.USER))

    def delete_cronjob(self, project_id, cronjob_id):
        return self._do_delete('projects/{project_id}/cronjobs',
                               project_id=project_id, cronjob_id=cronjob_id, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # SSHKeys
    # ------------------------------------------------------------------------------------------------------------------

    def create_sshkey(self, project_id, name, secret):
        """
        :type project_id: str
        :type name: str
        :param name: <= 255 characters
        :type secret: str
        :param secret: <= 255 characters
        """
        return self._do_post('projects/{project_id}/sshkeys',
                             project_id=project_id, json={"secret": secret, "name": name}, token_kind=TokenKind.USER)

    def get_projects_sshkeys(self, project_id):
        from v2infraboxapi.DataStructures import SSHKey
        return SSHKey.from_REST_API_dicts(self._do_get('projects/{project_id}/sshkeys',
                                                       project_id=project_id, token_kind=TokenKind.USER))

    def delete_sshkey(self, project_id, sshkey_id):
        return self._do_delete('projects/{project_id}/sshkeys/{sshkey_id}',
                               project_id=project_id, sshkey_id=sshkey_id, token_kind=TokenKind.USER)

    # ------------------------------------------------------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------------------------------------------------------

    def get_current_user_information(self):
        from v2infraboxapi.DataStructures import User
        return User.from_REST_API_dict(self._do_get('user', token_kind=TokenKind.USER))

    # ------------------------------------------------------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------------------------------------------------------

    # Not listed in the swagger doc
    def get_cluster_settings(self):
        return self._do_get('settings', token_kind=TokenKind.USER)


class ServerErrorException(InfraBoxAPIException):
    def __init__(self, message, status_code):
        self.status_code = status_code
        super(InfraBoxAPIException, self).__init__("Server Error: " + message)
