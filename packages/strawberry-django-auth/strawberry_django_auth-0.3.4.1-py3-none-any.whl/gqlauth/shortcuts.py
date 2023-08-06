from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from .models import UserStatus

UserModel = get_user_model()


def get_user_by_email(email: str):
    """
    get user by email or by secondary email
    raise ObjectDoesNotExist
    """
    try:
        user = UserModel._default_manager.get(**{UserModel.EMAIL_FIELD: email})
        return user
    except ObjectDoesNotExist:
        status = UserStatus._default_manager.get(secondary_email=email)
        return status.user


def get_user_to_login(**kwargs):
    """
    get user by kwargs or secondary email
    to perform login
    raise ObjectDoesNotExist
    """
    try:
        user = UserModel._default_manager.get(**kwargs)
        return user
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist
