from v2infraboxapi.Utils import Arrayable
from .ProjectType import ProjectType


class Project(Arrayable):
    """
    Class used to describe a project.
    Attributes:
        id: the project's id
        name: the project's name (length min = 3 + regex r"^[0-9a-zA-Z_\\-/]+$")
        type: a ProjectType
        private: whether the project is private
        userrole: the user's role or None
    """

    def __init__(self, project_id, name, project_type, private, userrole):
        """
        :type project_id: str
        :param project_id: the project's id
        :type name: str
        :param name: the project's name
        :type project_type: ProjectType
        :param project_type: a ProjectType instance
        :type private: bool
        :param private: whether the project is private
        :type userrole: str
        :param userrole: the user's role or None
        """
        self.id = project_id
        self.name = name
        self.type = project_type
        self.private = private
        self.userrole = userrole

    def _process_attribute(self, attribute_name):
        """
        Protected method used to process an attribute if needed (should be overwritten).
        :type attribute_name: str
        :param attribute_name: the name of one attribute.
        :rtype str
        :return: a string representing the specified attribute.
        """
        if attribute_name == "type":
            return ProjectType.to_string(self.type)
        elif attribute_name == "userrole":
            return self.userrole if self.userrole is not None else "None"
        elif attribute_name == "private":
            return "private" if self.private else "public"
        else:
            # No processing to be done
            return super(Project, self).__getattribute__(attribute_name)

    @staticmethod
    def from_REST_API_dict(rest_dict):
        """
        Static methods used to easily convert a dict to a Project
        :type rest_dict: dict
        :param rest_dict: a dictionary representing a Project and obtained through the REST API
        :rtype Project
        :return: a Project
        """
        return Project(project_id=rest_dict["id"],
                       name=rest_dict["name"],
                       project_type=ProjectType.from_string(rest_dict["type"]),
                       private=not rest_dict["public"],
                       userrole=rest_dict["userrole"])

    @staticmethod
    def from_REST_API_dicts(rest_dicts):
        """
        Static methods used to easily convert a list of dicts to a list of Project
        :type rest_dicts: list
        :param rest_dicts: a list of dicts (See from_REST_API_dict)
        :rtype list
        :return: a list of Projects
        """
        return [Project.from_REST_API_dict(d) for d in rest_dicts]
