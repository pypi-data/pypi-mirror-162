from functools import lru_cache
from typing import Any, Callable, Type
from django.utils.module_loading import import_string
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model

from .conf import settings


EMPTY = object()


@lru_cache
def cached_import_string(path: str):
    return import_string(path)


def get_group_model() -> Type[Group]:
    return cached_import_string(settings.GROUP_MODEL)


def get_permission_model() -> Type[Permission]:
    return cached_import_string(settings.PERMISSION_MODEL)


def get_group_to_permission_model():
    return get_group_model().permissions.through


def get_group_to_user_model():
    return get_user_model().groups.through


def get_permission_to_user_model():
    return get_user_model().user_permissions.through


def resolve_on_cached_object(obj, key: str, resolver: Callable) -> Any:
    value = getattr(obj, key, EMPTY)

    if value is not EMPTY:
        return value

    value = resolver(obj, key)
    setattr(obj, key, value)

    return value
