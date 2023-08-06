from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING

from .exceptions import NoReasonRegisteredError

if TYPE_CHECKING:
    from .models import UserCheck


__all__ = 'CheckDefinition', 'CheckRegistry',


@dataclass
class CheckDefinition:
    reason: str
    states: Enum
    inspector: Callable[['UserCheck'], bool]
    initial_state: str
    verbose_name: Optional[str] = None
    default_message: Optional[str] = ''

    def get_verbose_name(self):
        return self.verbose_name or self.reason

    def get_state_display(self, state):
        if hasattr(self.states, '_value2label_map_'):
            return self.states._value2label_map_[state]

        return self.states._value2member_map_[state]._name_

    @property
    def choices(self):
        if hasattr(self.states, 'choices'):
            return self.states.choices

        return self.states._value2member_map_.items()


class CheckRegistry(dict):
    def register(self, definition: CheckDefinition) -> CheckDefinition:
        assert isinstance(definition, CheckDefinition), (
            'Must be a `CheckDefinition` type.'
        )

        reason = definition.reason

        assert reason not in self, (
            f'Reason "{reason}" had already been registered.'
        )

        self[reason] = definition

        return definition

    def unregister(self, definition: CheckDefinition) -> CheckDefinition:
        assert definition.reason in self, 'Register checker first.'
        assert self[definition.reason] == definition, (
            'You are trying to unregister different checker with the '
            'same reason. This is prohibited.'
        )

        return self.pop(definition.reason)

    @property
    def choices(self):
        return [
            (x.reason, x.verbose_name or x.reason)
            for x in self.values()
        ]


    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError as e:
            raise NoReasonRegisteredError(str(e))
