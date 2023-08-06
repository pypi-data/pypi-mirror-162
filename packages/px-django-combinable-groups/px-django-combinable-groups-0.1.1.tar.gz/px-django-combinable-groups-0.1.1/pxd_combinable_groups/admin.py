from django.contrib import admin

from .utils import get_group_model
from .models import GroupToGroupConnection


Group = get_group_model()



class ChildrenInline(admin.TabularInline):
    model = GroupToGroupConnection
    fk_name = 'grouper'
    extra = 0


class GroupAdmin(admin.ModelAdmin):
    inlines = [ChildrenInline]


if admin.site.is_registered(Group):
    Base = admin.site._registry[Group].__class__

    admin.site.unregister(Group)

    @admin.register(Group)
    class GroupAdmin(GroupAdmin, Base):
        inlines = list(Base.inlines) + GroupAdmin.inlines
