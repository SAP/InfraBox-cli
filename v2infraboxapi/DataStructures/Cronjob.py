from v2infraboxapi.Utils import Arrayable


class Cronjob(Arrayable):
    """
    Class used to describe a project's cronjob.
    Attributes:
        id: the cronjob's id
        name: the cronjob's name
        minute: 0 - 59 and valid cron expression ("*", ",", "-")
        hour: 0 - 23 and valid cron expression ("*", ",", "-")
        month: 1 - 12 and valid cron expression ("*", ",", "-")
        day_of_week: 0 - 6 and valid cron expression ("*", ",", "-")
        day_of_month: 1 - 31 and valid cron expression ("*", ",", "-")
        sha: git commit sha or branch name
        infrabox_file: the path to the infrabox file (infrabox.json)
    """

    def __init__(self, cronjob_id, name, minute, hour, month, day_of_week, day_of_month, sha, infrabox_file):
        """
        :type cronjob_id: str
        :param cronjob_id: the cronjob's id
        :type name: str
        :param name: the cronjob's name
        :type minute: str
        :param minute: the cronjob's minute
        :type hour: str
        :param hour: the cronjob's hour
        :type month: str
        :param month: the cronjob's month
        :type day_of_week: str
        :param day_of_week: the cronjob's day_of_week
        :type day_of_month: str
        :param day_of_month: the cronjob's day_of_month
        :type sha: str
        :param sha: the cronjob's sha
        :type infrabox_file: str
        :param infrabox_file: the cronjob's infrabox_file
        """
        self.id = cronjob_id
        self.name = name
        self.minute = minute
        self.hour = hour
        self.month = month
        self.day_of_week = day_of_week
        self.day_of_month = day_of_month
        self.sha = sha
        self.infrabox_file = infrabox_file

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        value = super(Cronjob, self).__getattribute__(attribute_name)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Cronjob
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Cronjob and obtained through the REST API
        :rtype Cronjob
        :return: a Cronjob
        """
        return Cronjob(cronjob_id=rest_dict["id"],
                       name=rest_dict["name"],
                       minute=rest_dict["minute"],
                       hour=rest_dict["hour"],
                       month=rest_dict["month"],
                       day_of_week=rest_dict["day_week"],
                       day_of_month=rest_dict["day_month"],
                       sha=rest_dict["sha"],
                       infrabox_file=rest_dict["infrabox_file"]
                       )

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Cronjob
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Cronjobs
        """
        return [Cronjob.from_REST_API_dict(d) for d in rest_dicts]
