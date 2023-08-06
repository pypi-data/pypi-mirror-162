from django.utils.translation import gettext as _

from gqlauth.bases.exceptions import ErrorBase


class GraphQLAuthError(ErrorBase):
    def __init__(self, message=None):
        if message is None:
            message = " ".join([_("Authorization error:"), self.default_message])

        super().__init__(message)


class UserAlreadyVerified(GraphQLAuthError):
    default_message = _("User already verified.")


class InvalidCredentials(GraphQLAuthError):
    default_message = _("Invalid credentials.")


class UserNotVerified(GraphQLAuthError):
    default_message = _("User is not verified.")


class EmailAlreadyInUse(GraphQLAuthError):
    default_message = _("This email is already in use.")


class TokenScopeError(GraphQLAuthError):
    default_message = _("This token if for something else.")


class PasswordAlreadySetError(GraphQLAuthError):
    default_message = _("Password already set for account.")


class WrongUsage(GraphQLAuthError):
    """
    internal exception
    """

    default_message = _("Wrong usage, check your code!.")


class PermissionDenied(GraphQLAuthError):
    default_message = _("User is not allowed for this content")
