# Django combinable groups

Adds hierarchy to django permission groups.

## Installation

```sh
pip install px-django-combinable-groups
```

Depends on: `px-django-tree`.

In `settings.py`:

```python
INSTALLED_APPS += [
  # ...
  'django.contrib.auth',
  # ...
  # Dependent on:
  'pxd_tree.adjacency_list',
  # Should be added after auth package, or the one that defines `Group` model.
  'pxd_combinable_groups',
]

PXD_COMBINABLE_GROUPS = {
  # Use local cache in permissions resolver for key->id, id->key conversion.
  'USE_LOCAL_CACHE': True,
  # Use django's cache in permissions resolver for key->id, id->key conversion.
  'USE_DJANGO_CACHE': True,

  # Django cache key.
  'CACHE_KEY': 'default',
  # Cache timeout.
  'CACHE_TIMEOUT': 7 * 24 * 60 * 60,

  # Group model.
  'GROUP_MODEL': 'django.contrib.auth.models.Group',
  # Permission model.
  'PERMISSION_MODEL': 'django.contrib.auth.models.Permission',
}
```

## Usage

Package adds additional model, to construct auth groups oriented graph. So for each group you may define dependencies to additionally collect permissions from.

There are two services available for groups tree management:

- `pxd_combinable_groups.services.permissions_collector` - Permissions management methods.
- `pxd_combinable_groups.services.tree_collector` - Groups tree manager.

```python
from pxd_combinable_groups.services import permissions_collector


# Mapping

# Permissions collector mostly works with permission identifiers, not
# key-strings.
# To make your life easier there are two methods that converts one to another:
keys = ('auth.view_group', 'auth.change_group')
ids = permissions_collector.keys_to_ids(keys)
# > [1, 2]
permissions_collector.ids_to_keys(ids)
# > ['auth.view_group', 'auth.change_group']

# Methods preserve order so you may do things like that:
key_to_id_map = dict(zip(keys, permissions_collector.keys_to_ids(keys)))
# > {'auth.view_group': 1, 'auth.change_group': 2}


# Group management

# In case you need to know what permissions is in the certain groups you may
# use those methods:

# To get all permissions from any amount of groups:
permission_ids = permissions_collector.collect_all([
  group_id_1, group_id_2, group_id_3, group_id_4, # ... and so on.
])
# > [1,2,3,4,5,6,7,8,9]

# When you need to get permissions for each of groups separately:
groups = permissions_collector.collect([group_id_1, group_id_2])
# Result will be a list of `(group_id, permission_ids[])` for each passed group.
# Method `collect` preserves groups order.
# > [
#   (group_id_1, {1,2,3,4,5}),
#   (group_id_2, {2,3,4,5,6}),
# ]

# In case when you need to get permission for sets of groups:
sets = permissions_collector.collect_sets([
  (group_id_1, group_id_2),
  (group_id_3, group_id_4),
  (group_id_2, group_id_5),
])
# For each group identifier lists there will be a set of permission ids.
# Result will preserve initial sets order.
# > [
#   {1,2,3,4,5,6},
#   {3,4,5,6},
#   {1,2,5,6,7,8},
# ]


# User permissions resolver

# There is also a permissions resolvers for users.

# If you need to get permissions for multiple users at once:
permissions = permissions_collector.for_users([user_id_1, user_id_2])
# For each user identifier you'll receive a set of permission identifiers in
# a preserved order.
# > [
#   {2,3,7,9,23},
#   {2,3,7,9,23},
# ]

# And for one user.
# This method also will store cached response in user object, so for second
# call and further - there wouldn't be any db queries.
permissions = permissions_collector.for_user(user_object)
# > {2,3,7,9,23}
```

All those methods are pretty efficient in terms of database querying, so it will be better to prepare incoming permission/group/user ids/keys and then collect all of them once, than run them `n` times for each case.


```python
from pxd_combinable_groups.services import tree_collector


# This is a simple tree resolver for combinable groups.
# Technically it's not a tree, but an oriented graph, but you know,
# naming issues...

# Only two methods: `get_ancestors` and `get_descendants`.
# All those methods are done in one db call. They'r not very efficient but
# we're assuming there wouldn't be a lot of groups.
# Method is circular-graph proved. So any circular dependencies will result
# in graph gathering no matter what method will be called.

# Getting descendants is simple for any amount of groups you'll need:
descendants = tree_collector.get_descendants([group_id_1, group_id_2])
# Result will preserve order:
# > [
#   (group_id_1, [nested_group_id_1, nested_group_id_2, ...],
#   (group_id_2, [nested_group_id_4, nested_group_id_5, ...],
# ]

# Getting ancestors is same as for descendants:
descendants = tree_collector.get_descendants([group_id_1, group_id_2])
# Result will preserve order too.
# For tree-like structures where there is only one parent ancestors will be
# in straight [parent, parent's_parent, parent's_parent's_parent, ...] order.
# > [
#   (group_id_1, [ancestor_group_id_1, ancestor_group_id_2, ...],
#   (group_id_2, [ancestor_group_id_4, ancestor_group_id_5, ...],
# ]
```

## Admin

In administrative panel you may configure your groups with an additional grouper_to_source inliner in `Group` model editing interface.
