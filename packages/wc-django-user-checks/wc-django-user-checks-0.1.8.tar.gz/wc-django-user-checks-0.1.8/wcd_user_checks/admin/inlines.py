from django.contrib import admin

from ..models import UserCheck
from .forms import UserCheckAdminForm
from .mixins import AdminInlineBaseMixin


__all__ = 'UserCheckInlineAdmin',


class UserCheckInlineAdmin(AdminInlineBaseMixin, admin.TabularInline):
    form = UserCheckAdminForm
    model = UserCheck
    extra = 0
    show_change_link = True
    readonly_fields = (
        'reason', 'message', 'is_passed', # 'meta', 'user', 'created_at', 'updated_at',
    )
    fields = (
        'reason', 'state', 'message', 'is_reviewed', 'is_passed',
    )

    def has_add_permission(self, request, obj):
        return False
