from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = ('DRFConfig',)


class DRFConfig(AppConfig):
    # TODO: Create drf permissions at least
    name = 'wcd_user_checks.contrib.drf'
    label = 'wcd_user_checks_drf'
    verbose_name = pgettext_lazy('wcd_user_checks:drf', 'User checks: DRF')
