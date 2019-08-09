from enum import Enum

from ..Utils import InfraBoxAPIException


class CollaboratorRole(Enum):
    DEV = "Developer"
    ADMIN = "Administrator"
    OWNER = "Owner"

    @staticmethod
    def from_string(string):
        """
        Converts a string to a CollaboratorRole instance.
        Raises an exception if the string is invalid.
        :type string: str
        :param string: a string describing a status
        :rtype Status
        :return: a CollaboratorRole instance
        """
        conv_dict = {"Developer": CollaboratorRole.DEV,
                     "Administrator": CollaboratorRole.ADMIN,
                     "Owner": CollaboratorRole.OWNER}
        if string in conv_dict:
            return conv_dict[string]
        raise InfraBoxAPIException("String not recognized: " + string)

    @staticmethod
    def to_string(role):
        """
        Converts a collaborator's role back to a string.
        Raises an exception if the role is invalid.
        :param role: an int or a CollaboratorRole instance
        :rtype str
        :return: a string describing the role
        """
        conv_dict = {CollaboratorRole.DEV: "Developer",
                     CollaboratorRole.ADMIN: "Administrator",
                     CollaboratorRole.OWNER: "Owner"}
        if role in conv_dict:
            return conv_dict[role]
        raise InfraBoxAPIException("Collaborator role not recognized: " + role)

    def __hash__(self):
        return hash(self.value)
