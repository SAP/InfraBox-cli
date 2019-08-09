import json
from datetime import datetime, timedelta

from v2infraboxapi.Utils import Arrayable, InfraBoxAPIException
from .JobTree import JobTree
from .RunnableStatus import RunnableStatus


class Build(Arrayable):
    """
    Class used to describe a build.
    The get_build_base_information, get_jobs_information and compute_jobs_related_information methods are used
    to update some information through REST API calls.
    Attributes:
        project_id: the project's id
        id: the build's id
        build_number: the build number
        restart_counter: the restart counter (str)
        jobs: a JobTree containing all the jobs
        duration: the build's duration (a timedelta object or timedelta(-1) if still running)
            (also available through .get_duration())
        status: the build's status (as a Status instance) (also available through .get_status())
        commit: a dict describing the last commit (the same kind as the ones returned by the REST API)
        start_date: the build's start date (a datetime object or datetime.max if not yet running)
        is_cronjob: whether the build is a cron job
    """

    def __init__(self, project_id, build_id, build_number=None, restart_counter=None,
                 is_cronjob=None, jobs=None, commit=None):
        """
        :type project_id: str
        :param project_id: the id of the project this build is a part of
        :type build_id: str
        :param build_id: the build's id
        :type build_number: str
        :param build_number: the build's number
        :type restart_counter: str
        :param restart_counter: the build's restart counter
        :type is_cronjob: bool
        :param is_cronjob: whether this job is a cron job
        :param jobs: a list of Job instances or a JobTree or None
        :type commit: dict
        :param commit: a dict describing the commit (like the ones you get from the REST API)
        """
        # Setting up the attributes
        self.id = build_id
        self.project_id = project_id
        self.build_number = build_number
        self.restart_counter = restart_counter
        self.is_cronjob = is_cronjob

        if isinstance(jobs, list):
            # Converting the dicts to jobs if necessary
            self.jobs = JobTree(jobs)
        elif isinstance(jobs, JobTree):
            # Converting the dicts to jobs if necessary
            self.jobs = jobs
        else:
            self.jobs = None

        self.commit = commit

        self.duration = timedelta(-1)
        self.status = None
        self.start_date = datetime.max

    def get_build_base_information(self, api):
        """
        Updates the project_id, the build_id, the build_number and the restart_counter attributes.
        :type api: InfraBoxAPI
        :param api: an InfraBoxAPI instance to fetch any missing data
        """
        build = api.get_build(self.project_id, self.id)

        self.build_number = build.build_number
        self.restart_counter = build.restart_counter

    def get_jobs(self, api, compute_related_information=True):
        """
        Updates the jobs and the is_cronjob attributes.
        :type api: InfraBoxAPI
        :param api: an InfraBoxAPI instance to fetch any missing data
        :type compute_related_information: bool
        :param compute_related_information: whether we should compute the information related to the build's jobs
            (calls the compute_jobs_related_information method)
        """
        if self.build_number is None:
            raise InfraBoxAPIException(
                "ERROR: build number missing: project_id={}, build_id={}".format(self.project_id, self.id))

        jobs, commit, is_cronjob = api.get_jobs_for_build(self.project_id, self.build_number,
                                                          restart_counter=self.restart_counter)

        self.jobs = JobTree(jobs)
        self.commit = commit
        self.is_cronjob = is_cronjob

        if compute_related_information:
            self.compute_jobs_related_information()

    def compute_jobs_related_information(self):
        """
        Updates the duration and status attributes.
        """
        # Status
        self.status = min([job.status for job in self.jobs])

        # Duration computation
        start_dates = [job.start_date for job in self.jobs if job.start_date != datetime.max]
        end_dates = [job.end_date for job in self.jobs if job.end_date != datetime.max]

        if self.status in [RunnableStatus.SKIPPED, RunnableStatus.QUEUED, RunnableStatus.SCHEDULED] or \
                (self.status == RunnableStatus.KILLED and (not start_dates or not end_dates)):
            # Skipped, queued, scheduled or killed before the 1st task ended
            self.duration = timedelta(seconds=0)
            self.start_date = datetime.max

        elif self.status == RunnableStatus.RUNNING:
            # Running
            self.duration = timedelta(-1)
            self.start_date = min(start_dates)
        elif len(start_dates) == 0:
            # No jobs
            self.duration = timedelta(-1)
            self.start_date = datetime.max
        else:
            # Finished or killed (and at least a task finished)
            self.duration = max(end_dates) - min(start_dates)
            self.start_date = min(start_dates)

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        if attribute_name == "duration":
            # Duration: sometimes the timedelta uses 6 digits for the seconds if there is any duration
            if self.duration != timedelta(-1):
                return datetime.utcfromtimestamp(self.duration.total_seconds()).strftime("%H:%M:%S")
            else:
                return "Still running"
        elif attribute_name == "start_date":
            # Start date: there is not always any
            if self.start_date != datetime.max:
                return self.start_date.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return "Not yet started"
        elif attribute_name == "status":
            if self.status is not None:
                return RunnableStatus.to_short_string(self.status)
            else:
                return "Not computed yet"
        else:
            # No processing to be done
            return super(Build, self).__getattribute__(attribute_name)

    @staticmethod
    def list_last_builds(api, project_id, full=False):
        """
        The only purpose of this method is to avoid spamming the REST API.
        Returns the last 100 builds or the last 10 builds in you want the full information.
        :type api: InfraBoxAPI
        :param api: an InfraBoxAPI instance to fetch the data
        :type project_id: str
        :param project_id: the id of the project we are interested in
        :type full: bool
        :param full: whether we should also get the information about the build's jobs
        :rtype list
        :return: an array containing the last builds
        """

        return api.get_jobs_for_last_builds(project_id) if full else api.get_builds(project_id)

    def to_json(self, dump=False):
        ret = self.__dict__.copy()
        ret["jobs"] = self.jobs.to_json() if self.jobs else None
        ret["status"] = RunnableStatus.to_string(self.status)
        ret["start_date"] = self.start_date.strftime("%d/%m/%Y %H:%M:%S") if self.start_date != datetime.max else None
        ret["duration"] = self.duration.total_seconds()
        return json.dumps(ret) if dump else ret

    @classmethod
    def from_json(cls, json_dict):
        ret = cls(project_id=json_dict["project_id"],
                  build_id=json_dict["id"],
                  build_number=json_dict["build_number"],
                  restart_counter=json_dict["restart_counter"],
                  is_cronjob=json_dict.get("is_cronjob", False),  # Cronjob not available?
                  jobs=JobTree.from_json(json_dict["jobs"]) if json_dict["jobs"] else None,
                  commit=json_dict["commit"])
        ret.status = RunnableStatus.from_string(json_dict["status"])
        ret.duration = timedelta(seconds=json_dict["duration"])
        ret.start_date = datetime.strptime(json_dict["start_date"],
                                           "%d/%m/%Y %H:%M:%S") if json_dict["start_date"] is not None else datetime.max
        return ret
