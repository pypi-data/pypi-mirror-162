from django.contrib.auth.backends import ModelBackend as Base

from .services import permissions_collector
from .utils import get_permission_model


Permission = get_permission_model()


class ModelBackend(Base):
    def _get_group_permissions(self, user_obj):
        group_permissions = permissions_collector.collect_all(
            user_obj.groups.all().values_list('pk', flat=True)
        )
        return Permission.objects.filter(pk__in=group_permissions)
