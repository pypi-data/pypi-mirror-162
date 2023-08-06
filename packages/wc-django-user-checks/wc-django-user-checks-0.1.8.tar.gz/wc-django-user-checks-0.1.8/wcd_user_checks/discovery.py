from django.utils.module_loading import import_string

from .conf import settings
from .registry import CheckRegistry


__all__ = 'get_registry', 'autodiscover',


def get_registry() -> CheckRegistry:
    return import_string(settings.REGISTRY)


def autodiscover():
    r = get_registry()

    for runner in settings.DEFINITIONS or []:
        r.register(import_string(runner))
