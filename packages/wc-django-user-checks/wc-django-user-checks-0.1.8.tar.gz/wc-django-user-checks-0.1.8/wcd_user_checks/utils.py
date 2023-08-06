from typing import Dict, List, Optional, Sequence, Tuple, Union
from .registry import CheckDefinition, CheckRegistry
from .dtos import UserIdType, UserCheckDTO
from .models import UserCheck


__all__ = 'fix_check', 'get_check_complex_id', 'get_checks_map',

CheckComplexId = Tuple[UserIdType, str]
ChecksMapperType = Union[UserCheck, UserCheckDTO]
EMPTY = ('', None)


def fix_check(
    registry: CheckRegistry,
    data: ChecksMapperType,
    state: Optional[str] = None,
    message: Optional[str] = None,
    meta: Optional[dict] = None,
) -> ChecksMapperType:
    definition: CheckDefinition = registry[data.reason]
    data.state = definition.states(
        definition.initial_state
        if state in EMPTY and data.state in EMPTY
        else
        state
        if state not in EMPTY
        else
        data.state
    )
    data.message = (
        definition.default_message
        if message in EMPTY and data.message in EMPTY
        else
        message
        if message not in EMPTY
        else
        data.message
    ) or ''
    data.meta = (data.meta if meta is None else meta) or {}
    data.is_passed = definition.inspector(data)

    data.state

    return data


def get_check_complex_id(x: ChecksMapperType) -> CheckComplexId:
    return (x.user_id, x.reason)


def get_checks_map(
    items: Sequence[ChecksMapperType]
) -> Dict[CheckComplexId, ChecksMapperType]:
    return {get_check_complex_id(x): x for x in items}
