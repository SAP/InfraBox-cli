from enum import Enum

from ..Utils import InfraBoxAPIException


class ProjectType(Enum):
    GERRIT = "gerrit"
    GITHUB = "github"
    UPLOAD = "upload"

    @staticmethod
    def from_string(string):
        """
        Converts a string to a ProjectType instance.
        Raises an exception if the string is invalid.
        :type string: str
        :param string: a string describing a project type
        :rtype ProjectType
        :return: a Status instance
        """
        conv_dict = {"gerrit": ProjectType.GERRIT,
                     "github": ProjectType.GITHUB,
                     "upload": ProjectType.UPLOAD}
        if string in conv_dict:
            return conv_dict[string]
        raise InfraBoxAPIException("String not recognized: " + string)

    @staticmethod
    def to_string(project_type):
        """
        Converts a project type back to a string.
        Raises an exception if the project type is invalid.
        :param project_type: an int or a ProjectType instance
        :rtype str
        :return: a string describing the project type
        """
        conv_dict = {ProjectType.GERRIT: "gerrit",
                     ProjectType.GITHUB: "github",
                     ProjectType.UPLOAD: "upload"}
        if project_type in conv_dict:
            return conv_dict[project_type]
        raise InfraBoxAPIException("Project type not recognized: " + project_type)

    def __hash__(self):
        return hash(self.value)
