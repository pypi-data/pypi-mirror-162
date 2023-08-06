from django.contrib import admin
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from ..models import UserCheck
from .filters import create_all_reason_state_filter, create_is_reviewed_filter
from .mixins import AdminBaseMixin
from .forms import UserCheckAdminForm


__all__ = 'UserCheckAdmin',


@admin.register(UserCheck)
class UserCheckAdmin(AdminBaseMixin, admin.ModelAdmin):
    list_display = (
        'user', 'get_reason_display', 'get_state_display',
        'is_reviewed', 'is_passed',
    )
    list_display_links = 'user', 'get_reason_display',
    list_filter = (
        'is_passed',
        'user',
        create_all_reason_state_filter(),
        ('is_reviewed', create_is_reviewed_filter(state_parameter='state')),
    )
    list_select_related = 'user',
    autocomplete_fields = 'user',
    search_fields = 'reason', 'state', 'message', 'user__username', 'meta',
    form = UserCheckAdminForm

    date_hierarchy = 'updated_at'

    fields_on_create = 'user', 'reason', 'message',
    fieldsets = (
        (None, {
            'fields': (
                ('user', 'reason',),
                'message',
            )
        }),
    )
    fieldsets_on_update = (
        (None, {
            'fields': (
                ('user', 'reason',),
                ('state', 'is_reviewed', 'is_passed',),
                'message',
            )
        }),
        (pgettext_lazy('wcd_user_checks:admin', 'Dates'), {
            'classes': ('collapse',),
            'fields': (('created_at', 'updated_at'),),
        }),
        (pgettext_lazy('wcd_user_checks:admin', 'Metadata'), {
            'classes': ('collapse',),
            'fields': ('meta',),
        }),
    )

    def get_fields(self, request, obj=None):
        if obj is None and self.fields_on_create:
            return self.fields_on_create

        return super().get_fields(request, obj=obj)

    def get_fieldsets(self, request, obj = None):
        if obj is not None:
            return self.fieldsets_on_update

        return super().get_fieldsets(request, obj=obj)

    @admin.display(
        ordering='reason',
        description=UserCheck._meta.get_field('reason').verbose_name
    )
    def get_reason_display(self, obj):
        return obj.get_reason_display()

    @admin.display(
        ordering='state',
        description=UserCheck._meta.get_field('state').verbose_name
    )
    def get_state_display(self, obj):
        return obj.get_state_display()
