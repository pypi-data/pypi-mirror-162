from typing import Dict, Optional, Sequence
from .models import UserCheck
from .discovery import get_registry
from .dtos import UserIdType, UserCheckDTO, UserCheckStateDTO

from . import cases


__all__ = 'get_registry', 'get_states', 'get_state', 'set_checks', 'set_check'


def get_states(ids: Sequence[UserIdType]) -> Dict[UserIdType, UserCheckStateDTO]:
    return cases.get_user_check_states(ids)


def get_state(id: UserIdType) -> UserCheckStateDTO:
    return get_states([id]).get(id)


def set_checks(checks: Sequence[UserCheckDTO]) -> Sequence[UserCheck]:
    return cases.set_checks(get_registry(), checks)


def set_check(
    user_id: UserIdType,
    reason: str,

    state: Optional[str] = None,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
    is_reviewed: bool = False,
) -> UserCheck:
    return cases.set_check(
        get_registry(),
        user_id=user_id,
        reason=reason,
        state=state,
        message=message,
        meta=meta,
        is_reviewed=is_reviewed,
    )
