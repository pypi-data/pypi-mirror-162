from django.dispatch import Signal


__all__ = 'state_changed',


# Arguments: "user_id", "items", "previous_state"
state_changed: Signal = Signal()
