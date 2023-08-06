from dataclasses import dataclass
from itertools import groupby
from typing import Any, Dict, List, Optional

from .models import UserCheck


__all__ = 'UserIdType', 'UserCheckStates', 'UserCheckDTO', 'UserCheckStateDTO',


UserIdType = Any
UserCheckStates = Dict[UserIdType, 'UserCheckStateDTO']


@dataclass
class UserCheckDTO:
    user_id: UserIdType
    reason: str

    state: Optional[str] = None
    message: Optional[str] = None
    meta: Optional[dict] = None

    is_reviewed: bool = False
    is_passed: bool = False

    def update_model(self, item: UserCheck) -> UserCheck:
        item.user_id = self.user_id
        item.reason = self.reason
        item.state = self.state
        item.message = self.message
        item.meta = self.meta
        item.is_passed = self.is_passed
        item.is_reviewed = self.is_reviewed

        return item

    @classmethod
    def from_model(cls, item: UserCheck) -> 'UserCheckDTO':
        return cls(
            user_id=item.user_id,
            reason=item.reason,
            state=item.state,
            message=item.message,
            meta=item.meta,
            is_passed=item.is_passed,
            is_reviewed=item.is_reviewed,
        )


def user_id_key(check: UserCheckDTO):
    return check.user_id


@dataclass
class UserCheckStateDTO:
    user_id: UserIdType
    checks: Dict[str, UserCheckDTO]
    is_reviewed: bool = False
    is_passed: bool = False

    @classmethod
    def from_checks(cls, checks: List[UserCheckDTO]) -> UserCheckStates:
        grouped = groupby(sorted(checks, key=user_id_key), key=user_id_key)

        return {
            id: cls(
                user_id=id,
                checks={check.reason: check for check in items},
                is_reviewed=all(check.is_reviewed for check in items),
                is_passed=all(check.is_passed for check in items),
            )
            for id, items in ((x, list(y)) for x, y in grouped)
        }
