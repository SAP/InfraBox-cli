from v2infraboxapi.Utils import Arrayable


class SSHKey(Arrayable):
    """
    Class used to describe a project's SSH key.
    Attributes:
        id: the key's id
        name: the key's name
        secret_name: the name of the secret, this key is linked to
    """

    def __init__(self, key_id, name, secret_name):
        """
        :type key_id: str
        :param key_id: the key's id
        :type name: str
        :param name: the key's name
        :type secret_name: str
        :param secret_name: the name of the secret, this key is linked to
        """
        self.id = key_id
        self.name = name
        self.secret_name = secret_name

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        value = super(SSHKey, self).__getattribute__(attribute_name)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a SSHKey
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a SSHKey and obtained through the REST API
        :rtype Project
        :return: a SSHKey
        """
        return SSHKey(key_id=rest_dict["id"],
                      name=rest_dict["name"],
                      secret_name=rest_dict["secret"])

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of SSHKey
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of SSHKeys
        """
        return [SSHKey.from_REST_API_dict(d) for d in rest_dicts]
