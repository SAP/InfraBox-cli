from v2infraboxapi.Utils import Arrayable


class User(Arrayable):
    """
    Class used to describe a user.
    Attributes:
        id: the user's id
        username: the user's username
        name: the user's name
        github_id: the user's github id
        email: the user's email
    """

    def __init__(self, user_id, username, name, github_id, email):
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
        """
        self.id = user_id
        self.username = username
        self.name = name
        self.github_id = github_id
        self.email = email

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        value = super(User, self).__getattribute__(attribute_name)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a User
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a User and obtained through the REST API
        :rtype User
        :return: a User
        """
        return User(user_id=rest_dict["id"],
                    username=rest_dict["username"],
                    name=rest_dict["name"],
                    github_id=rest_dict["github_id"],
                    email=rest_dict["email"])
