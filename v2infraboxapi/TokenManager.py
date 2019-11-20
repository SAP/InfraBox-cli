from enum import Enum


class TokenManager(object):
    """
    Interface used to handle tokens.
    Depending on the REST you make, you need different tokens, ex:
    the one you have from logging in, another you generated from a project, and so on...
    """

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
        # To explain why this exists:
        # There are 2 kinds of tokens: a user token (from your login) and project tokens (which allow to push/pull)
        # From what I tested:
        # With your user token, you can create projects / edit settings in projects you created
        # I do not know yet the rights you get from your user token when you are listed as Developer/Administrator
        # Then when a project is public, anyone (even with no token at all) gets to pull information for the project
        # If the project is private, even if you are the owner, if you DO NOT have a token to pull, you CANNOT
        # pull information about your own project
        # I guess that you cannot push either
        # So since we can only send one token per request, we need to send the right kind of token with the right
        # authorization, when we want to call the REST API

        raise NotImplementedError


class TokenKind(Enum):
    USER = "user"
    PULL = "pull"
    PUSH = "push"

