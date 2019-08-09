import colorama


class DefaultDict(dict):
    """
    A default dict, as found in the container library.
    """

    def __init__(self, default_constructor):
        """
        :param default_constructor: a callable object used to create a new element if a key is missing
        """
        self._default_constructor = default_constructor
        super(DefaultDict, self).__init__()

    def __missing__(self, key):
        self[key] = self._default_constructor()
        return self[key]


class Arrayable(object):
    """Interface used for classes which we want to convert to a list from a list of attributes."""

    def to_string_array(self, *args):
        """
        Returns a displayable array of strings.
        Some processing is done on a few attributes.
        :rtype list
        """
        ret = []
        for attr in args:
            assert isinstance(attr, str), "Not string: " + str(attr)
            ret.append(self._process_attribute(attr))
        return ret

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        return str(self.__getattribute__(attribute_name))


class InfraBoxAPIException(Exception):
    pass


colorama.init()
