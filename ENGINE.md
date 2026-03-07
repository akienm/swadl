# Engine-Based Testing in SWADL

## The Problem With Control-by-Control Testing

Traditional test automation looks like this:

```python
def test_login_page():
    assert login_page.username.is_visible()
    assert login_page.password.is_visible()
    assert login_page.submit.is_visible()
    assert not login_page.error_banner.is_visible()
```

This works, but it requires you to think about every control individually every time.
As pages grow, test setup becomes repetitive. Controls that *should* be checked often get
skipped because writing the assertions is tedious.

## The Engine Approach

In SWADL, each control can carry a description of its expected state as part of its
definition. A single engine call then validates the whole set:

```python
# In the section definition:
self.username = SWADLControl(
    name="username",
    selector="#username",
    validation={VALIDATE_VISIBLE: True, VALIDATE_ENABLED: True},
)
self.submit = SWADLControl(
    name="submit",
    selector="#submit",
    validation={VALIDATE_VISIBLE: True},
)
self.error_banner = SWADLControl(
    name="error_banner",
    selector="#error",
    validation={VALIDATE_VISIBLE: False},
)
self.validate_loaded_queue = [self.username, self.submit, self.error_banner]

# In a method or test:
self.validate_loaded()   # checks all three in one call
```

The engine iterates the control list, calls `control.validate()` on each one, and
accumulates failures rather than stopping at the first one. You get a full picture of
what passed and what failed in a single run.


## Validation Dicts

A validation dict maps validation keys to expected values:

```python
{VALIDATE_VISIBLE: True}                   # must be visible
{VALIDATE_EXIST: False}                    # must not exist
{VALIDATE_VISIBLE: True, VALIDATE_ENABLED: True}  # both
{VALIDATE_TEXT: "Welcome, Alice"}          # text must match
{VALIDATE_INPUT: True}                     # type the control's key value into the field
{VALIDATE_CLICK: True}                     # click as part of this validation pass
```

`None` as a value means "skip this check", so you can build a base dict and override
individual keys for different scenarios.


## validate_controls()

`SWADLPageSection.validate_controls()` accepts either:

**A list of controls** (each uses its own `.validation` attribute):
```python
self.validate_controls(controls=self.validate_loaded_queue)
```

**A list of controls with an override dict** (applies the same dict to every control):
```python
self.validate_controls(
    controls=[self.username, self.password, self.submit],
    validation={VALIDATE_VISIBLE: True},
)
```

**A list of (control, dict) tuples** (per-control override):
```python
self.validate_controls(controls=[
    (self.username, {VALIDATE_VISIBLE: True, VALIDATE_ENABLED: True}),
    (self.submit,   {VALIDATE_VISIBLE: True, VALIDATE_ENABLED: False}),
])
```

This lets you describe the same page in different states with different lists:

```python
def validate_before_login(self):
    self.validate_controls(self.controls_always_visible, {VALIDATE_VISIBLE: True})
    self.validate_controls(self.controls_only_after_login, {VALIDATE_VISIBLE: False})

def validate_after_login(self):
    self.validate_controls(self.controls_always_visible, {VALIDATE_VISIBLE: True})
    self.validate_controls(self.controls_only_after_login, {VALIDATE_VISIBLE: True})
```


## validate_loaded()

`validate_loaded()` is a specialised call to `validate_controls()` that checks every
control in `self.validate_loaded_queue` for visibility. It defaults to `fatal=True`
because if the page isn't loaded, continuing the test makes no sense.

```python
self.validate_loaded_queue = [self.header, self.nav, self.main_content]
self.validate_loaded()   # fatal by default — stops the test if any are missing
```

`load_page()` calls `validate_loaded()` automatically after navigation. You rarely
need to call it directly unless you are verifying state mid-flow.


## How It Works Internally

`SWADLControl.validate(validation={...})` iterates the validation dict in a defined
order and calls the corresponding method for each key:

| Key | Method called |
|-----|--------------|
| `VALIDATE_ENABLED` | `validate_enabled()` |
| `VALIDATE_EXIST` | `validate_exist()` |
| `VALIDATE_TEXT` | `validate_text()` |
| `VALIDATE_UNIQUE` | `validate_unique()` |
| `VALIDATE_VISIBLE` | `validate_visible()` |
| `VALIDATE_INPUT` | `validate_input()` |
| `VALIDATE_CLICK` | `validate_click()` |

Input and click are always last: input fills a field (which may change page state),
and click may navigate away entirely.

Each `validate_*` method:
1. Calls `_fetch_property()` to read the current state with retry logic.
2. Calls `_validate()` to log the result, save a screenshot on failure, accumulate
   non-fatal failures, and optionally raise on fatal failures.

The retry loop (`_retry_until_expected_met`) keeps calling the underlying property
query until the result matches `expected` or the timeout expires. This is why
controls never go stale — the selector is re-evaluated on each retry.


## Adding Validation to a Control

Set `validation` at instantiation time for controls that always have the same
expected state:

```python
self.submit_btn = SWADLControl(
    name="submit_btn",
    selector="#submit",
    validation={VALIDATE_VISIBLE: True, VALIDATE_ENABLED: True},
)
```

Or pass a validation dict at call time for context-dependent checks:

```python
# Before login: submit should exist but may be disabled
self.submit_btn.validate(validation={VALIDATE_EXIST: True, VALIDATE_ENABLED: False})

# After filling the form: submit should be enabled
self.submit_btn.validate(validation={VALIDATE_ENABLED: True})
```
