from v2infraboxapi.Utils import Arrayable


class Secret(Arrayable):
    """
    Class used to describe a project's secret.
    Attributes:
        id: the secret's id
        name: the secret's name
    """

    def __init__(self, secret_id, name):
        """
        :type secret_id: str
        :param secret_id: the secret's id
        :type name: str
        :param name: the secret's name
        """
        self.id = secret_id
        self.name = name

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        value = super(Secret, self).__getattribute__(attribute_name)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Secret
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Secret and obtained through the REST API
        :rtype Secret
        :return: a Secret
        """
        return Secret(secret_id=rest_dict["id"],
                      name=rest_dict["name"])

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Secret
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Secrets
        """
        return [Secret.from_REST_API_dict(d) for d in rest_dicts]
