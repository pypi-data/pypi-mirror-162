from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('CombinableGroupsConfig',)


class CombinableGroupsConfig(AppConfig):
    name = 'pxd_combinable_groups'
    verbose_name = pgettext_lazy('pxd_combinable_groups', 'Combinable groups')
