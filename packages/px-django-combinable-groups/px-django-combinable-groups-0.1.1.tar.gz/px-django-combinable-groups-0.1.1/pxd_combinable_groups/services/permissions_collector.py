from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, TypeVar
from functools import reduce

from django.db import models
from django.core.cache.backends.locmem import LocMemCache
from django.core.cache import caches

from ..utils import (
    get_group_to_permission_model, get_permission_model, get_permission_to_user_model,
    get_group_to_user_model, resolve_on_cached_object
)
from ..conf import settings

from . import tree_collector


# FIXME: LocMemCache is pickles and unpickles items all the time.
# Maybe write simpler cache backend that doesn't do it.
LOCAL_CACHE = LocMemCache(
    'pxd-combinable-groups-permissions',
    {'TIMEOUT': settings.CACHE_TIMEOUT, 'MAX_ENTRIES': 10**4}
)
CACHE_KEY_TO_ID_PREFIX = 'pxd-combinable-groups-permissions:key-to-id:'
CACHE_ID_TO_KEY_PREFIX = 'pxd-combinable-groups-permissions:id-to-key:'
Permission = get_permission_model()
GroupToUser = get_group_to_user_model()
PermissionToUser = get_permission_to_user_model()

I = TypeVar('I')
O = TypeVar('O')


def _resolve_descended(group_ids: Iterable[int]):
    group_ids = list(group_ids)
    groups = tree_collector.get_descendants(group_ids)
    all_ids = reduce(
        lambda acc, definition: acc | set(definition[1]),
        groups, set(group_ids),
    )

    return group_ids, groups, all_ids


def _map_pair(values):
    values_map = {}

    for grouper, value in values:
        values_map[grouper] = values_map.get(grouper, [])
        values_map[grouper].append(value)

    return values_map


def _mget(cache, keys: Iterable[str], prefix: Optional[str] = None):
    result = {}
    resolvable_keys = {
        (str(key) if prefix is None else prefix + str(key)): key
        for key in keys
    }

    if hasattr(cache, 'mget'):
        result = cache.mget(resolvable_keys.keys())
    elif hasattr(cache, 'get_many'):
        result = cache.get_many(resolvable_keys.keys())
    else:
        for key in resolvable_keys.keys():
            result[key] = cache.get(key)

    return {
        resolvable_keys[k]: value
        for k, value in result.items()
        if value is not None
    }


def _mset(cache, values: Dict[str, Any], prefix: Optional[str] = None):
    prefixed = values if prefix is None else {
        prefix+str(key): value for key, value in values.items()
    }

    if hasattr(cache, 'mset'):
        cache.mset(prefixed, timeout=settings.CACHE_TIMEOUT)
    elif hasattr(cache, 'set_many'):
        cache.set_many(prefixed, timeout=settings.CACHE_TIMEOUT)
    else:
        for key, value in prefixed.items():
            cache.set(key, value, timeout=settings.CACHE_TIMEOUT)


def _reverse_map(values: dict) -> dict:
    return {value: key for key, value in values.items()}


def _keys_to_ids_map(keys: Iterable[str]) -> Dict[str, int]:
    key_labels = [tuple(x.split('.')) for x in keys]
    q = models.Q()

    for label, codename in key_labels:
        q |= models.Q(content_type__app_label=label, codename=codename)

    ids_map: Dict[str, str] = {
        (label, codename): id
        for id, label, codename in (
            get_permission_model().objects.filter(q)
            .values_list('pk', 'content_type__app_label', 'codename')
            .order_by()
        )
    }

    return {'.'.join(key): ids_map.get(key) for key in key_labels}


def _ids_to_keys_map(ids: Iterable[int]) -> Dict[int, str]:
    return {
        id: f'{label}.{codename}'
        for id, label, codename in (
            get_permission_model().objects.filter(pk__in=ids)
            .values_list('pk', 'content_type__app_label', 'codename')
            .order_by()
        )
    }


def _cache_resolver(
    keys: Sequence[I],
    solver: Callable,
    prefix_general: str,
    prefix_reverse: str,
) -> List[Optional[O]]:
    result = {}
    diff = set(keys)

    if settings.USE_LOCAL_CACHE:
        result.update(_mget(LOCAL_CACHE, diff))
        diff -= result.keys()

    if settings.USE_DJANGO_CACHE and len(diff) > 0:
        result.update(
            _mget(caches[settings.CACHE_KEY], diff, prefix=prefix_general)
        )
        diff -= result.keys()

    if len(diff):
        found = solver(diff)
        result.update(found)

        # Updating cache
        if settings.USE_LOCAL_CACHE:
            _mset(LOCAL_CACHE, found)
            _mset(LOCAL_CACHE, _reverse_map(found))

        if settings.USE_DJANGO_CACHE:
            _mset(caches[settings.CACHE_KEY], found, prefix=prefix_general)
            _mset(caches[settings.CACHE_KEY], _reverse_map(found), prefix=prefix_reverse)

    return [result.get(k) for k in keys]


# FIXME: Overcomplicated implementation...
def keys_to_ids(keys: Sequence[str]) -> List[Optional[int]]:
    """Resolves permission keys to identifiers.

    Args:
        keys (Sequence[str]): Keys list.

    Returns:
        List[Optional[int]]: Identifiers list.
    """
    return _cache_resolver(
        keys, _keys_to_ids_map, CACHE_KEY_TO_ID_PREFIX, CACHE_ID_TO_KEY_PREFIX,
    )


# FIXME: Overcomplicated implementation...
def ids_to_keys(ids: Sequence[int]) -> List[Optional[str]]:
    """Resolves permission ids to keys.

    Args:
        ids (Sequence[int]): Identifiers list.

    Returns:
        List[Optional[str]]: Keys list.
    """
    return _cache_resolver(
        ids, _ids_to_keys_map, CACHE_ID_TO_KEY_PREFIX, CACHE_KEY_TO_ID_PREFIX,
    )


def collect_all(group_ids: Iterable[int]) -> List[int]:
    """Collects list of all permissions that those groups has.

    Args:
        group_ids (Iterable[int]): Group identifiers to collect permissions from.

    Returns:
        List[int]: Queryset of permission identifiers.
    """
    _, _, all_ids = _resolve_descended(group_ids)

    return (
        get_group_to_permission_model().objects
        .filter(group_id__in=all_ids)
        .values_list('permission_id')
    )


def collect(group_ids: Iterable[int]) -> List[Tuple[int, Set[int]]]:
    """For each group collects a list of it's permission identifiers.

    Args:
        group_ids (Iterable[int]): Group identifiers to collect permissions from.

    Returns:
        List[Tuple[int, Set[int]]]: List of (id, permissions_ids) entries.
    """
    group_ids, groups, all_ids = _resolve_descended(group_ids)
    permission_connections = (
        get_group_to_permission_model().objects
        .filter(group_id__in=all_ids)
        .values_list('group_id', 'permission_id')
    )

    inverted_group_map = {}

    for id, descendants in groups:
        for descendant in descendants:
            inverted_group_map[descendant] = inverted_group_map.get(descendant) or set()
            inverted_group_map[descendant].add(id)

    permissions_map = {}

    for group_id, permission_id in permission_connections:
        root_groups = inverted_group_map.get(group_id) or [group_id]

        for root_group in root_groups:
            permissions_map[root_group] = permissions_map.get(root_group) or set()
            permissions_map[root_group].add(permission_id)

    return [(id, permissions_map.get(id, [])) for id in group_ids]


def collect_sets(sets: Sequence[Sequence[int]]) -> List[Set[int]]:
    """Collects all permission ids for each of groups list in a `sets` sequence.

    Args:
        sets (Sequence[Sequence[int]]): Set of groups lists.

    Returns:
        List[Set[int]]: List of permission sets for each group list.
    """
    sets = list(sets)
    collected = dict(collect(group_id for seq in sets for group_id in seq))

    return [
        set(
            permission_id
            for group_id in seq
            for permission_id in collected.get(group_id, [])
        )
        for seq in sets
    ]


def for_users(user_ids: Sequence[int]) -> List[Set[int]]:
    """Collects all permission ids for each user in a sequence.

    Args:
        user_ids (Sequence[int]): User identifiers.

    Returns:
        List[Set[int]]: List of permission sets.
    """
    connections = (
        GroupToUser.objects.filter(user_id__in=user_ids)
        .values_list('user_id', 'group_id')
        .order_by('user_id')
    )
    connections_map = _map_pair(connections)

    permission_connections = (
        PermissionToUser.objects
        .filter(user_id__in=user_ids)
        .values_list('user_id', 'permission_id')
    )
    permission_connections_map = _map_pair(permission_connections)

    return [
        perms | set(permission_connections_map.get(user_ids[i], []))
        for i, perms in enumerate(collect_sets([
            connections_map.get(id, []) for id in user_ids
        ]))
    ]


def for_user(user: 'User') -> Set[int]:
    """Collects all permission ids for a given user.
    Caches result inside user object.

    Args:
        user (User): User object.

    Returns:
        Set[int]: Permissions set.
    """
    return resolve_on_cached_object(
        user, '_gathered_combinable_permissions',
        lambda *a: for_users([user.id])[0],
    )
