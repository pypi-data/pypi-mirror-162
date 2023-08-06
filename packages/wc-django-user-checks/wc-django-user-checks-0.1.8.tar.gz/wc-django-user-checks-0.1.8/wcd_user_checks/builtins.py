from django.db import models
from django.utils.translation import pgettext_lazy

from .registry import CheckDefinition


__all__ = 'ManualCheckState', 'MANUAL_CHECK_DEFINITION',


class ManualCheckState(models.TextChoices):
    INVALID = 'invalid', pgettext_lazy('wcd_user_checks:manual', 'Invalid')
    VALID = 'valid', pgettext_lazy('wcd_user_checks:manual', 'Valid')


MANUAL_CHECK_DEFINITION = CheckDefinition(
    reason='MANUAL',
    states=ManualCheckState,
    initial_state=ManualCheckState.INVALID,
    inspector=lambda x: x.state == ManualCheckState.VALID,
    verbose_name=pgettext_lazy('wcd_user_checks:manual', 'Manual'),
    default_message=pgettext_lazy(
        'wcd_user_checks:manual', 'You have been blocked by administrator.'
    ),
)
