from colorama import Fore, Back, Style
from enum import Enum

from ..Utils import InfraBoxAPIException


class RunnableStatus(Enum):
    """
    Enum used to list the different states a build and its jobs can have.
    This class is also mostly used rank states and compute the status of a build
    based on the status of each of its jobs.
    """
    FINISHED = 100
    OK = 95
    SKIPPED = 90
    SCHEDULED = 85
    UNSTABLE = 75
    FAILURE = 50
    ERROR = 35
    KILLED = 25
    QUEUED = 15
    RUNNING = 0

    @staticmethod
    def from_string(string):
        """
        Converts a string to a RunnableStatus instance.
        Raises an exception if the string is invalid.
        :type string: str
        :param string: a string describing a status
        :rtype Status
        :return: a Status instance
        """
        conv_dict = {"finished": RunnableStatus.FINISHED,
                     "skipped": RunnableStatus.SKIPPED,
                     "ok": RunnableStatus.OK,
                     "scheduled": RunnableStatus.SCHEDULED,
                     "queued": RunnableStatus.QUEUED,
                     "unstable": RunnableStatus.UNSTABLE,
                     "error": RunnableStatus.ERROR,
                     "failure": RunnableStatus.FAILURE,
                     "killed": RunnableStatus.KILLED,
                     "running": RunnableStatus.RUNNING}
        if string in conv_dict:
            return conv_dict[string]
        raise InfraBoxAPIException("String not recognized: " + string)

    @staticmethod
    def to_string(status):
        """
        Converts a status back to a string.
        Raises an exception if the status is invalid.
        :param status: an int or a Status instance
        :rtype str
        :return: a string describing the status
        """
        conv_dict = {RunnableStatus.FINISHED: "finished",
                     RunnableStatus.SKIPPED: "skipped",
                     RunnableStatus.OK: "ok",
                     RunnableStatus.SCHEDULED: "scheduled",
                     RunnableStatus.QUEUED: "queued",
                     RunnableStatus.UNSTABLE: "unstable",
                     RunnableStatus.ERROR: "error",
                     RunnableStatus.FAILURE: "failure",
                     RunnableStatus.KILLED: "killed",
                     RunnableStatus.RUNNING: "running"}
        if status in conv_dict:
            return conv_dict[status]
        raise InfraBoxAPIException("Status not recognized: " + status)

    @staticmethod
    def to_short_string(status):
        """
        Converts a status back to a string.
        Raises an exception if the status is invalid.
        :param status: an int or a Status instance
        :rtype str
        :return: a string describing the status
        """
        conv_dict = {RunnableStatus.FINISHED: Fore.GREEN + "OK" + Style.RESET_ALL,
                     RunnableStatus.OK: Fore.GREEN + "OK" + Style.RESET_ALL,
                     RunnableStatus.SKIPPED: Fore.YELLOW + "SKIP" + Style.RESET_ALL,
                     RunnableStatus.SCHEDULED: Fore.YELLOW + "SCHEDULED" + Style.RESET_ALL,
                     RunnableStatus.QUEUED: Fore.YELLOW + "QUEUED" + Style.RESET_ALL,
                     RunnableStatus.UNSTABLE: Fore.LIGHTRED_EX + "UNSTABLE" + Style.RESET_ALL,
                     RunnableStatus.ERROR: Fore.RED + "ERR" + Style.RESET_ALL,
                     RunnableStatus.FAILURE: Fore.RED + "FAILED" + Style.RESET_ALL,
                     RunnableStatus.KILLED: Fore.RED + "KILL" + Style.RESET_ALL,
                     RunnableStatus.RUNNING: Back.WHITE + Fore.BLACK + "RUN" + Style.RESET_ALL}

        if status in conv_dict:
            return conv_dict[status]
        raise InfraBoxAPIException("Status not recognized: " + status)

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return hash(self.value)
