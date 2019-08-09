import os
from glob import glob

import infraboxcli
from v2infraboxapi import TokenManager, TokenKind
from .Utils import CLI_DATA_DIR, locked


class CLITokenManager(TokenManager):
    """
    Class used to store stuff about the current CLI session.
    Is also a TokenManager.
    """

    _PROJECT_TOKEN_FOLDER = os.path.join(CLI_DATA_DIR, ".tokens")
    _LOGIN_TOKEN_PATH = os.path.join(_PROJECT_TOKEN_FOLDER, "login.token")
    _LOCKFILE_PATH = os.path.join(CLI_DATA_DIR, "token_lockfile.pid")

    def __init__(self):
        if not os.path.isdir(self._PROJECT_TOKEN_FOLDER):
            os.makedirs(self._PROJECT_TOKEN_FOLDER)

        self._login_token = None
        if os.path.isfile(self._LOGIN_TOKEN_PATH):
            with open(self._LOGIN_TOKEN_PATH, "r") as f:
                self._login_token = {"token": "".join(line.strip() for line in f.readlines())}

    @locked(_LOCKFILE_PATH)
    def login(self, token):
        """
        Sets the login token and saves it.
        :type token: str
        :param token: the login token
        """

        self._login_token = {"token": token}
        with open(self._LOGIN_TOKEN_PATH, "w") as f:
            f.write(token)

    @locked(_LOCKFILE_PATH)
    def logout(self):
        """
        Deletes the login token. Returns whether we were logged in.
        """

        self._login_token = None
        if os.path.isfile(self._LOGIN_TOKEN_PATH):
            os.remove(self._LOGIN_TOKEN_PATH)
            return True
        return False

    @locked(_LOCKFILE_PATH)
    def get_token(self, token_kind, project_id=None):
        """
        Gets the right token for a project id, if none is provided please provide the login token.
        :type token_kind: TokenKind
        :param token_kind: the kind of token needed
        :type project_id: str
        :param project_id: the project's id we are interested in
        :rtype dict
        :return: {"token": <TOKEN>} if a token is found else None
        """

        if token_kind == TokenKind.USER or project_id is None or token_kind is None:
            return self._login_token

        path = self._project_id_to_token_path(project_id, token_kind == TokenKind.PULL)

        if os.path.isfile(path):
            with open(path, "r") as f:
                return {"token": "".join(line.strip() for line in f.readlines())}

        infraboxcli.logger.warn("No TOKEN found for project %s (scope %s)." % (project_id,
                                                                               "pull" if token_kind == TokenKind.PULL
                                                                               else "push"))

        return self._login_token

    @classmethod
    @locked(_LOCKFILE_PATH)
    def save_token(cls, project_id, token, pull, push):
        """
        Saves the token for a project id.
        :type project_id: str
        :param project_id: the project's id we are interested in
        :type token: str
        :param token: the token we want to save
        :type pull: bool
        :param pull: whether the token allows to pull
        :type push: bool
        :param push: whether the token allows to push
        """

        if not os.path.isdir(cls._PROJECT_TOKEN_FOLDER):
            os.makedirs(cls._PROJECT_TOKEN_FOLDER)

        if pull:
            with open(cls._project_id_to_token_path(project_id, True), "w") as f:
                f.write(token)
        if push:
            with open(cls._project_id_to_token_path(project_id, False), "w") as f:
                f.write(token)

    @classmethod
    @locked(_LOCKFILE_PATH)
    def delete_token(cls, project_id, pull, push):
        """
        Deletes a token.
        :type project_id: str
        :param project_id: the project's id we are interested in
        :type pull: bool
        :param pull: whether the token allows to pull
        :type push: bool
        :param push: whether the token allows to push
        :rtype int
        :return the number of tokens deleted
        """
        rep = 0

        if pull:
            path = cls._project_id_to_token_path(project_id, True)
            if os.path.isfile(path):
                os.remove(path)
                rep += 1

        if push:
            path = cls._project_id_to_token_path(project_id, False)
            if os.path.isfile(path):
                os.remove(path)
                rep += 1

        return rep

    @classmethod
    @locked(_LOCKFILE_PATH)
    def list_tokens(cls):
        """
        Lists tokens and returns them to the format: {project_id: {"push": bool, "pull": bool}}
        :rtype: dict
        """

        project_ids = dict()
        for path in glob(cls._PROJECT_TOKEN_FOLDER + os.sep + "*.token"):
            if path != cls._LOGIN_TOKEN_PATH:
                project_id, pull_or_push = os.path.split(path[:-6])[1].split('_')

                if project_id not in project_ids:
                    project_ids[project_id] = {"pull": False, "push": False}

                if pull_or_push == "push":
                    project_ids[project_id]["push"] = True
                elif pull_or_push == "pull":
                    project_ids[project_id]["pull"] = True

        return project_ids

    @classmethod
    def _project_id_to_token_path(cls, project_id, pull):
        """Returns the path to the project's token from its id."""
        return cls._PROJECT_TOKEN_FOLDER + os.sep + project_id + ("_pull" if pull else "_push") + ".token"


CLI_TOKEN_MANAGER = CLITokenManager()
