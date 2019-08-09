from datetime import datetime, timedelta

from v2infraboxapi.Utils import Arrayable
from .RunnableStatus import RunnableStatus


class Testrun(Arrayable):
    """
    Class used to describe a job's testrun.
    Attributes:
        status: the testrun's status (RunnableStatus)
        name: the testrun's name
        suite: the testrun's suite
        duration: the testrun's duration (string in milliseconds)
        timestamp: the testrun's timestamp "%Y/%m/%d %H:%M:%S"
        stack: the testrun's stack
        message: the testrun's message
    """

    def __init__(self, status, name, suite, duration, timestamp, stack, message):
        """
        :type status: RunnableStatus
        :param status: the testrun's status
        :type name: str
        :param name: the testrun's name
        :type suite: str
        :param suite: the testrun's suite
        :type duration: str
        :param duration: the testrun's duration
        :type timestamp: str
        :param timestamp: the testrun's timestamp
        :type stack: str
        :param stack: the testrun's stack
        :type message: str
        :param message: the testrun's message
        """
        self.status = status
        self.name = name
        self.suite = suite
        self.duration = duration
        self.timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        self.stack = stack
        self.message = message

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        if attribute_name == "duration":
            return str(timedelta(seconds=int(self.duration) / 1000))
        elif attribute_name == "status":
            return RunnableStatus.to_short_string(self.status)
        elif attribute_name == "timestamp":
            return self.timestamp.strftime("%d/%m/%Y %H:%M:%S")

        value = super(Testrun, self).__getattribute__(attribute_name)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Testrun
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Testrun and obtained through the REST API
        :rtype Testrun
        :return: a Testrun
        """
        return Testrun(status=RunnableStatus.from_string(rest_dict["state"]),
                       name=rest_dict["name"],
                       suite=rest_dict["suite"],
                       duration=rest_dict["duration"],
                       timestamp=rest_dict["timestamp"],
                       stack=rest_dict["stack"],
                       message=rest_dict["message"]
                       )

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Testrun
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Testruns
        """
        return [Testrun.from_REST_API_dict(d) for d in rest_dicts]
