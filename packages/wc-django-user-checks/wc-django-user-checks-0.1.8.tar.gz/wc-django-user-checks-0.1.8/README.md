# WebCase User checks

Package to provide additional user check mechanics.

## Installation

```sh
pip install wc-django-user-checks
```

In `settings.py`:

```python
INSTALLED_APPS += [
  'wcd_uer_checks',
]

WCD_USER_CHECKS = {
  'REGISTRY' = 'wcd_user_checks.globals.registry', # default
  'DEFINITIONS' = None, # default
  'CACHE' = 'default', # default

  'DEFINITIONS' = [
    'wcd_user_checks.builtins.MANUAL_CHECK_DEFINITION', # Manual check reason
  ],
}
```

## Usage

For all your interactions use `client` module. It has everything that you would need.

### Simple check interaction

```python
# Importing client
from wcd_user_checks import client
# Getting check definition
from wcd_user_checks.builtins import MANUAL_CHECK_DEFINITION

# Setting a check reason to an initial value(invalid).
client.set_check(user_id, MANUAL_CHECK_DEFINITION.reason)
# Getting a user state
state = client.get_state(user_id)
# It will be invalid
# > state.is_passed == False

# Setting a valid state value
client.set_check(user_id, MANUAL_CHECK_DEFINITION.reason, state=builtins.ManualCheckState.VALID)
# Will force user check state to become valid
state = client.get_state(user_id)
# > state.is_passed == True
```

### Creating a custom checker

File: `apps/another/checker.py`
```python
from wcd_user_checks import client
from wcd_user_checks.registry import CheckDefinition

# This state might be django's `models.TextChoices` or any other Enum.
class AnotherState(str, Enum):
  VALID = 'valid'
  PROCESS = 'process'
  INVALID = 'invalid'

# This is your checker definition object
ANOTHER = CheckDefinition(
  # Reason to check. Must be unique for the project.
  reason='ANOTHER',
  # States enum, that your check workflow could be resolved.
  states=AnotherState,
  # Initial state. Better to be invalid,
  initial_state=AnotherState.INVALID,
  # Inspector - function that checks whether the check is passed or not.
  inspector=lambda x: x.state == AnotherState.VALID
)
```

You may register this manually:

```python
client.get_registry().register(ANOTHER)
```

Or by defining tha path to a definitions in `settings.py`:

```python
WCD_USER_CHECKS_DEFINITIONS = [
  'wcd_user_checks.builtins.MANUAL_CHECK_DEFINITION', # Build in

  'apps.another.checker.ANOTHER', # Yours
]
```

### Administrative panel

By default there will be a separate model to change user checks. But it might happen this to be not enough. An you'll need to add an inliner to a user model.

There is functionality for that:

`admin.py`
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as Base
from django.contrib.auth import get_user_model

# This inline here has a little bit more optimized user checks displaying.
from wcd_user_checks.admin import UserCheckInlineAdmin


UserModel = get_user_model()
admin.site.unregister(UserModel)


@admin.register(UserModel)
class UserAdmin(Base):
  inlines = Base.inlines + [UserCheckInlineAdmin]
```

## TODO

- [_] Middleware for user checks auto injection into `request`.
- [_] Context manager for checks for templates injection.
- [_] DRF permissions.
- [_] DRF views maybe.
- [_] Some simple view decorator to check user's ability to perform action.
