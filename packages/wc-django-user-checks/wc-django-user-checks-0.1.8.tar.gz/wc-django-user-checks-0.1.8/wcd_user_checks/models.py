from django.db import models
from django.contrib.postgres.indexes import BTreeIndex
from django.utils.translation import pgettext_lazy, pgettext
from django.conf import settings

from .query import UserCheckQuerySet
from .discovery import get_registry


__all__ = 'user_check_indexes', 'UserCheck'


def user_check_indexes(name: str = '%(app_label)s_%(class)s'):
    return [
        # BTreeIndex(name=name + '_lookup_idx', fields=['reason', 'state']),
    ]


class UserCheck(models.Model):
    objects: models.Manager[UserCheckQuerySet] = UserCheckQuerySet.as_manager()

    class Meta:
        verbose_name = pgettext_lazy('wcd_user_checks', 'User check')
        verbose_name_plural = pgettext_lazy('wcd_user_checks', 'User checks')
        indexes = user_check_indexes()
        unique_together = (
            ('user_id', 'reason'),
        )

    id = models.BigAutoField(
        primary_key=True,
        verbose_name=pgettext_lazy('wcd_user_checks', 'ID'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=pgettext_lazy('wcd_user_checks', 'User'),
        related_name='checks_set',
        null=False, blank=False, on_delete=models.CASCADE,
    )
    reason = models.TextField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Reason'),
        null=False, blank=False,
    )
    state = models.TextField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'State'),
        null=False, blank=False,
    )
    message = models.TextField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Message'),
        null=False, blank=True,
    )
    meta = models.JSONField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Metadata'),
        null=False, blank=True, default=dict
    )

    is_reviewed = models.BooleanField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Is reviewed'),
        null=False, default=False
    )
    is_passed = models.BooleanField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Is passed'),
        null=False, default=False
    )

    created_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Created at'),
        null=False, blank=False, auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_user_checks', 'Updated at'),
        null=False, blank=False, auto_now=True
    )

    def __str__(self):
        return (
            pgettext('wcd_user_checks', '#{user_id}: {reason}[{state}].')
            .format(
                user_id=self.user_id,
                reason=self.get_reason_display(),
                state=self.get_state_display()
            )
        )

    def get_reason_display(self):
        if not self.reason:
            return self.reason

        return get_registry()[self.reason].get_verbose_name()

    def get_state_display(self):
        if not self.state or not self.reason:
            return self.state

        return get_registry()[self.reason].get_state_display(self.state)

    def clone_object(self):
        data = {
            field: getattr(self, field)
            for field in (
                'pk', 'user_id', 'reason', 'state', 'message', 'meta',
                'is_reviewed', 'is_passed', 'created_at', 'updated_at',
            )
        }
        return self.__class__(**data)
