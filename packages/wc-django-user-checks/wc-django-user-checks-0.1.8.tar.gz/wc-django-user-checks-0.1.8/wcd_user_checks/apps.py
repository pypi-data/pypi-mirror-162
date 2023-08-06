from django.apps import AppConfig
from django.utils.translation import pgettext_lazy

from .discovery import autodiscover


__all__ = ('UserChecksConfig',)


class UserChecksConfig(AppConfig):
    name = 'wcd_user_checks'
    verbose_name = pgettext_lazy('wcd_user_checks', 'User checks')

    def ready(self):
        autodiscover()
