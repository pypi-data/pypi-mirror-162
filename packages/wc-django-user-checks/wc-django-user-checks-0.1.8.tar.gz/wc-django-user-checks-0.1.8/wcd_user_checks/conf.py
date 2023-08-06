from dataclasses import dataclass, field
from typing import Optional, Sequence
from px_settings.contrib.django import settings as s


__all__ = 'Settings', 'settings',


@s('WCD_USER_CHECKS')
@dataclass
class Settings:
    REGISTRY: str = 'wcd_user_checks.globals.registry'
    DEFINITIONS: Optional[Sequence[str]] = field(default_factory=lambda: [
        'wcd_user_checks.builtins.MANUAL_CHECK_DEFINITION',
    ])
    CACHE: str = 'default'


settings = Settings()
