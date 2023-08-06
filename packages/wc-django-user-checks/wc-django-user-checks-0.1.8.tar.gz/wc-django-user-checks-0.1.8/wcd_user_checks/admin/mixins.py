from ..cases import send_checks_changed
from ..discovery import get_registry
from ..utils import fix_check
from ..dtos import UserIdType, UserCheckStates, UserCheckDTO, UserCheckStateDTO


__all__ = 'AdminBaseMixin', 'AdminInlineBaseMixin',


class AdminBaseMixin:
    readonly_fields = (
        'user', 'reason', 'meta', 'is_passed', 'created_at', 'updated_at',
    )
    readonly_fields_on_create = ()

    def get_readonly_fields(self, request, obj = None):
        if obj is None:
            return self.readonly_fields_on_create

        return super().get_readonly_fields(request, obj=obj)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            previous_state = obj.__class__.objects.filter(pk=obj.pk)
            olds = UserCheckStateDTO.from_checks([
                UserCheckDTO.from_model(check) for check in previous_state
            ])

        obj = fix_check(get_registry(), obj)
        super().save_model(request, obj, form, change)
        send_checks_changed([obj], previous_states=olds)


class AdminInlineFormsetBaseMixin:

    def save_new(self, form, commit=True):
        fix_check(get_registry(), form.instance)
        return super().save_new(form, commit=commit)

    def save_existing(self, form, instance, commit=True):
        instance = fix_check(get_registry(), instance)
        return super().save_existing(form, instance, commit=commit)

    def save(self):
        olds = UserCheckStateDTO.from_checks([
            UserCheckDTO.from_model(check) for check in self.queryset
        ])
        saved = super().save()
        send_checks_changed(saved, previous_states=olds)

        return saved


class AdminInlineBaseMixin(AdminBaseMixin):
    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        return type(FormSet.__name__, (AdminInlineFormsetBaseMixin, FormSet,), {})
