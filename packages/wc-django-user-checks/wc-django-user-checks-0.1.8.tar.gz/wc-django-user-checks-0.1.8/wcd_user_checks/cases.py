from typing import Dict, List, Optional, Sequence
from itertools import groupby
from django.db import transaction
from .models import UserCheck
from .registry import CheckRegistry
from .signals import state_changed
from .dtos import UserIdType, UserCheckStates, UserCheckDTO, UserCheckStateDTO

from .utils import fix_check, get_checks_map


__all__ = 'get_user_check_states', 'set_checks', 'set_check', 'send_checks_changed',


EMPTY = object()


def get_user_check_states(
    ids: Sequence[UserIdType]
) -> Dict[UserIdType, UserCheckStateDTO]:
    checks = UserCheck.objects.filter(user_id__in=ids)

    return UserCheckStateDTO.from_checks([
        UserCheckDTO.from_model(check) for check in checks
    ])


def set_checks(
    registry: CheckRegistry,
    checks: Sequence[UserCheckDTO],
) -> Sequence[UserCheck]:
    checks = [fix_check(registry, check) for check in checks]
    user_ids = set()
    reasons = set()

    for item in checks:
        user_ids.add(item.user_id)
        reasons.add(item.reason)

    existing = UserCheck.objects.filter(user_id__in=user_ids, reason__in=reasons)
    olds = UserCheckStateDTO.from_checks([
        UserCheckDTO.from_model(check) for check in existing
    ])
    existing = get_checks_map(existing)
    updates: Sequence[UserCheck] = []
    creates: Sequence[UserCheck] = []

    for item in checks:
        id = (item.user_id, item.reason)

        if id in existing:
            updates.append(item.update_model(existing[id]))
        else:
            creates.append(item.update_model(UserCheck()))

    with transaction.atomic():
        created = UserCheck.objects.bulk_create(creates)
        UserCheck.objects.bulk_update(updates, fields=(
            'user_id', 'state', 'message', 'meta', 'is_reviewed', 'is_passed',
        ))

        result = (created or []) + (updates or [])

    send_checks_changed(result, previous_states=olds)

    return result


def set_check(
    registry: CheckRegistry,
    user_id: UserIdType,
    reason: str,

    state: Optional[str] = None,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
    is_reviewed: bool = False,
) -> UserCheck:
    return set_checks(registry, (UserCheckDTO(
        user_id=user_id,
        reason=reason,
        state=state,
        message=message,
        meta=meta,
        is_reviewed=is_reviewed
    ),))[0]


def get_user_id(item: UserCheck):
    return item.user_id


def send_checks_changed(
    checks: Sequence[UserCheck],
    # FIXME: Must not be this way.
    # Checks state should store a changes history for every change happened.
    # For me to get previous state at any time I need, not only when
    # it was passed to me.
    previous_states: Optional[UserCheckStates] = {}
):
    grouped = groupby(sorted(checks, key=get_user_id), key=get_user_id)

    for user_id, items in grouped:
        state_changed.send(
            UserCheck,
            user_id=user_id,
            items=list(items),
            previous_state=previous_states.get(user_id)
        )
