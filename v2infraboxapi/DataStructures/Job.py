import json
from datetime import datetime, timedelta

from v2infraboxapi.Utils import Arrayable
from .RunnableStatus import RunnableStatus


class Job(Arrayable):
    """
    Class used to describe a job.
    A static method is also provided to get a job's console log.
    Attributes:
        id: the job's id (should never be None if you want to use a JobTree)
        project_id: the project's id
        name: the job's name
        start_date: the date the job started (a datetime object or datetime.max if not yet running)
        end_date: the date the job ended (a datetime object or datetime.max if not yet running)
        status: a Status instance describing the job's state
        duration: a timedelta instance (timedelta(seconds=0) if the job has not started yet)
        dependencies: a list of dependencies as obtained through the REST API
        console_log: the job's console log as a string
    """

    def __init__(self, job_id, project_id, job_name, start_date, end_date, status, dependencies, console_log=None):
        """
        :type job_id: str
        :param job_id: the job's id
        :type project_id: str
        :param project_id: the project's id
        :type job_name: str
        :param job_name: the job's name
        :param start_date: the start date in the following format: "%Y-%m-%d %H:%M:%S" or None
        :param end_date: the end date in the following format: "%Y-%m-%d %H:%M:%S" or None
        :type status: RunnableStatus
        :param status: the job's state
        :type dependencies: list
        :param dependencies: a list of dependencies as obtained through the REST API
        :type console_log: str
        :param console_log: the job's console log
        """

        def str_to_datetime(date):
            # The 10th char can be a ' ' or a 'T' and the date might end with extra digits
            return datetime.strptime(date[:10] + date[11:19], "%Y-%m-%d%H:%M:%S")

        self.id = job_id
        self.project_id = project_id
        self.name = job_name
        self.start_date = str_to_datetime(start_date) if start_date is not None else datetime.max
        self.end_date = str_to_datetime(end_date) if end_date is not None else datetime.max
        self.status = status
        self.dependencies = dependencies
        self.console_log = console_log

        self.duration = None
        self._compute_duration()

    def _compute_duration(self):
        """
        :rtype timedelta
        :return: the duration used by the job if it is still running or has finished/failed,
        timedelta(seconds=0) otherwise
        """
        if self.status in [RunnableStatus.SKIPPED, RunnableStatus.QUEUED, RunnableStatus.SCHEDULED,
                           RunnableStatus.KILLED] or self.start_date is None:
            # Was killed or never launched
            self.duration = timedelta(seconds=0)
        elif self.status == RunnableStatus.RUNNING:
            # Is running
            self.duration = datetime.now() - self.start_date
        else:
            # Has somehow finished
            self.duration = self.end_date - self.start_date

    @staticmethod
    def get_console_log(api, project_id, job_id, job=None):
        """
        Downloads and returns the job's console log.
        Also updates the console_log attribute of the Job instance if provided.
        This is a static method, because sometimes you just want to get log without having to get the rest of the data.
        :type api: InfraBoxAPI
        :param api: an InfraBoxAPI instance to fetch any missing data
        :type project_id: str
        :param project_id: the project's id
        :type job_id: str
        :param job_id: the job's id
        :type job: Job:
        :param job: a Job instance you wish to update
        :rtype str
        :return: the job's console log as a string
        """
        console_log = api.get_job_console_log(project_id, job_id)
        if job is not None:
            job.console_log = console_log
        return console_log

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
            return RunnableStatus.to_short_string(self.status)
        else:
            # No processing to be done
            return super(Job, self).__getattribute__(attribute_name)

    @staticmethod
    def from_REST_API_dict(rest_dict, project_id):
        """
        Static methods used to easily convert a dict to a Job
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a job and obtained through the REST API
        :type project_id: str
        :param project_id: the project's id
        :rtype Job
        :return: a job
        """
        return Job(job_id=rest_dict["id"],
                   project_id=project_id,
                   job_name=rest_dict["name"],
                   start_date=rest_dict["start_date"],
                   end_date=rest_dict["end_date"],
                   status=RunnableStatus.from_string(rest_dict["state"]),
                   dependencies=rest_dict["depends_on"])

    @staticmethod
    def from_REST_API_dicts(rest_dicts, project_id):
        """
        Static methods used to easily convert a list of dicts to a list of Jobs.
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :type project_id: str
        :param project_id: the project's id
        :rtype list
        :return: a list of Job
        """
        return [Job.from_REST_API_dict(d, project_id) for d in rest_dicts]

    def to_json(self, dump=False):
        ret = self.__dict__.copy()
        ret["status"] = RunnableStatus.to_string(self.status)
        ret["start_date"] = self.start_date.strftime("%Y-%m-%d%H:%M:%S") if self.start_date != datetime.max else None
        ret["end_date"] = self.end_date.strftime("%Y-%m-%d%H:%M:%S") if self.end_date != datetime.max else None
        del ret["duration"]
        return json.dumps(ret) if dump else ret

    @classmethod
    def from_json(cls, json_dict):
        return cls(job_id=json_dict["id"],
                   project_id=json_dict["project_id"],
                   job_name=json_dict["name"],
                   start_date=json_dict["start_date"],
                   end_date=json_dict["end_date"],
                   status=RunnableStatus.from_string(json_dict["status"]),
                   dependencies=json_dict["dependencies"],
                   console_log=json_dict["console_log"])
