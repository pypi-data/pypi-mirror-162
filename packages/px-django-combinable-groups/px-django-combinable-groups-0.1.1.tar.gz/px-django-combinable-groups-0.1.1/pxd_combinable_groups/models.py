from typing import Dict, List, Sequence
from django.utils.translation import pgettext_lazy
from django.db import models

from .utils import get_group_model


Group = get_group_model()


class GroupToGroupConnectionQuerySet(models.QuerySet):
    pass


class GroupToGroupConnection(models.Model):
    objects = GroupToGroupConnectionQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy(
            'pxd_combinable_groups', 'Group to group connection'
        )
        verbose_name_plural = pgettext_lazy(
            'pxd_combinable_groups', 'Group to group connection'
        )
        unique_together = (
            ('grouper', 'source'),
        )

    grouper = models.ForeignKey(
        Group, related_name='source_connections', on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('pxd_combinable_groups', 'Grouper group'),
    )
    source = models.ForeignKey(
        Group, related_name='grouper_connections', on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('pxd_combinable_groups', 'Source group'),
    )

    def __str__(self):
        return f'#{self.grouper_id} -> #{self.source_id}'
