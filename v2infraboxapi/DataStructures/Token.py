from v2infraboxapi.Utils import Arrayable


class Token(Arrayable):
    """
    Class used to describe a token.
    Attributes:
        id: the token's id
        description: the token's description
        scope_push: whether this token allows to push
        scope_pull: whether this token allows to pull
    """

    def __init__(self, token_id, description, scope_push, scope_pull):
        """
        :type token_id: str
        :param token_id: the token's id
        :type description: str
        :param description: the token's description
        :type scope_push: bool
        :param scope_push: whether this token allows to push
        :type scope_pull: bool
        :param scope_pull: whether this token allows to pull
        """
        self.id = token_id
        self.description = description
        self.scope_push = scope_push
        self.scope_push = scope_push
        self.scope_pull = scope_pull

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        value = super(Token, self).__getattribute__(attribute_name)

        if type(value) == bool:
            return str(value)
        return value if value else "None"

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Token
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Token and obtained through the REST API
        :rtype Token
        :return: a Token
        """
        return Token(token_id=rest_dict["id"],
                     description=rest_dict["description"],
                     scope_push=rest_dict["scope_push"],
                     scope_pull=rest_dict["scope_pull"])

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Token
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Tokens
        """
        return [Token.from_REST_API_dict(d) for d in rest_dicts]
