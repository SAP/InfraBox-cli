from .CollaboratorRole import CollaboratorRole
from .User import User


class Collaborator(User):
    """
    Class used to describe a collaborator.
    Attributes:
        role: the user's role in the project
        See User's doc
    """

    def __init__(self, user_id, username, name, github_id, email, role):
        """
        :type user_id: str
        :param user_id: the user's id
        :type username: str
        :param username: the user's username
        :type name: str
        :param name: the user's name
        :type github_id: str
        :param github_id: the user's github id
        :type email: str
        :param email: the user's email
        :type role: CollaboratorRole
        :param role: the user's role in the project
        """
        super(Collaborator, self).__init__(user_id, username, name, github_id, email)
        self.role = role

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        if attribute_name == "role":
            return CollaboratorRole.to_string(self.role)
        else:
            # No processing to be done
            return super(Collaborator, self).__getattribute__(attribute_name)

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Collaborator
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Collaborator and obtained through the REST API
        :rtype Project
        :return: a Collaborator
        """
        return Collaborator(user_id=rest_dict["id"],
                            username=rest_dict["username"],
                            name=rest_dict["name"],
                            github_id="",
                            email=rest_dict["email"],
                            role=CollaboratorRole.from_string(rest_dict["role"]))

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Collaborator
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Collaborators
        """
        return [Collaborator.from_REST_API_dict(d) for d in rest_dicts]
