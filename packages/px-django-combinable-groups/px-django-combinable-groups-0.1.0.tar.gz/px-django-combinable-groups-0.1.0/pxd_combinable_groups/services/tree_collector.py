from pxd_tree.adjacency_list.services.tree_collector import (
    TreeCollector, FieldsConfig
)

from ..models import GroupToGroupConnection


DEFAULT_FIELDS_CONFIG = FieldsConfig(
    id='source_id', parent='grouper', parent_id='grouper_id'
)


class GrouperTreeCollector(TreeCollector):
    pass


grouper_tree_collector = GrouperTreeCollector(
    fields=DEFAULT_FIELDS_CONFIG,
    queryset=GroupToGroupConnection.objects.all(),
)
get_ancestors = grouper_tree_collector.get_ancestors
get_descendants = grouper_tree_collector.get_descendants
