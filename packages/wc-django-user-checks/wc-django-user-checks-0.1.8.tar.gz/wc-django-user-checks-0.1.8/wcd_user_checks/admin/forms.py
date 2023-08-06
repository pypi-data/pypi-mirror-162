from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import UserCheck
from ..discovery import get_registry


__all__ = 'UserCheckAdminForm',


class UserCheckAdminForm(forms.ModelForm):
    class Meta:
        model = UserCheck
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        registry = get_registry()

        if 'reason' in self.fields:
            self.fields['reason'].widget = forms.Select(
                choices = registry.choices
            )

        if 'state' in self.fields:
            reason = self.instance and self.instance.reason

            if reason and reason in registry:
                self.fields['state'].widget = forms.Select(
                    choices = registry[reason].choices
                )
