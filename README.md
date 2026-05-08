# SWADL — Selenium Webdriver Accelerated Development Library

SWADL is a test automation framework built on the AutomationBlox best-practices model.
It hides the complexity of browser and desktop UI interaction behind a clean, consistent
API that non-programmers can learn in a day and experienced engineers can maintain without pain.

Inspired by SilkTest and QTP: controls are objects with selectors baked in at instantiation,
not raw locators scattered through your tests. The framework handles all synchronization —
no more `time.sleep()`, no more stale element exceptions.


## The Three-Layer Model

```
Test Case  ── knows data and which flows to call. All assertions live here.
    │
Flow       ── knows which page sections do the work and what to ask them to do.
    │          Tests never call page sections directly.
    │
Section    ── knows how to interact with the UI. Flows never inspect its internals.
```

This encapsulation means:
- A UI change only requires updating one section file.
- Flows are stable as long as the intent is the same.
- Tests read like specifications.


## Quick Example

```python
# test_login.py
class TestLogin(SWADLTest):
    def setUp(self):
        super().setUp()
        self.auth_flow = AuthFlow()

    def test_valid_login(self):
        self.test_data[USERNAME] = "alice"
        self.test_data[PASSWORD] = "correct-horse"

        self.auth_flow.login()

        self.assert_true(exper=self.test_data[LOGIN_SUCCEEDED])
```

```python
# flows/auth_flow.py
class AuthFlow(SWADLBaseFlow):
    def __init__(self, **kwargs):
        super().__init__(name="AuthFlow", **kwargs)
        self.login_page = LoginSection()
        self.home_page = HomeSection()

    def login(self):
        self.login_page.do_login()
        self.home_page.validate_loaded()
```

```python
# page_sections/login_section.py
class LoginSection(SWADLPageSection):
    def __init__(self, name="LoginSection", **kwargs):
        super().__init__(name=name, **kwargs)
        self.url = "https://example.com/login"

        self.username_field = SWADLControl(
            name="username_field",
            selector="#username",
            validation={VALIDATE_VISIBLE: True},
        )
        self.password_field = SWADLControl(
            name="password_field",
            selector="#password",
        )
        self.login_button = SWADLControl(
            name="login_button",
            selector="#submit",
        )
        self.validate_loaded_queue = [self.username_field]

    def do_login(self):
        self.load_page()
        self.username_field.set_value(value=self.test_data[USERNAME])
        self.password_field.set_value(value=self.test_data[PASSWORD])
        self.login_button.click()
```


## Installation

```bash
git clone https://github.com/akienm/swadl.git
cd swadl
pip install -e .          # installs swadl + selenium
pip install -e .[dev]     # also installs pytest, nose2, flake8
```

Set `SWADL_HOME` to the repo directory and add `$SWADL_HOME/bin` to your PATH.

### Running the demo

```bash
googledemo          # runs under nose2
googledemo p        # runs under pytest
```

### Running your own test

```bash
# from the directory containing your test file:
runatest nose2 --log=debug your_test_module_name
runatest pytest --log=debug your_test_file.py
```


## Writing Tests

### 1. Test case

Subclass `SWADLTest`. Tests only touch `test_data` and flow methods.

```python
from SWADL.engine.swadl_base_test import SWADLTest

class MyTest(SWADLTest):
    def setUp(self):
        super().setUp()          # required — initializes the framework
        self.my_flow = MyFlow()

    def tearDown(self):
        super().tearDown()       # required — reports accumulated failures

    def test_something(self):
        self.test_data[MY_KEY] = "some value"
        self.my_flow.do_something()
        self.assert_equal(x=self.test_data[RESULT_KEY], y="expected value")
```

### 2. Flow

Subclass `SWADLBaseFlow`. Flows orchestrate sections but never inspect their internals.

```python
from SWADL.engine.swadl_base_flow import SWADLBaseFlow

class MyFlow(SWADLBaseFlow):
    def __init__(self, **kwargs):
        super().__init__(name="MyFlow", **kwargs)
        self.my_section = MySection()

    def do_something(self):
        self.my_section.perform_action()
```

### 3. Section (page object)

Subclass `SWADLPageSection`. Declare controls as instance attributes. Set
`validate_loaded_queue` to the controls that prove the page is ready.

```python
from SWADL.engine.swadl_base_section import SWADLPageSection
from SWADL.engine.swadl_control import SWADLControl
from SWADL.engine.swadl_constants import VALIDATE_VISIBLE

class MySection(SWADLPageSection):
    def __init__(self, name="MySection", **kwargs):
        super().__init__(name=name, **kwargs)
        self.url = "https://example.com/page"

        self.my_button = SWADLControl(
            name="my_button",
            selector="#submit-btn",
            validation={VALIDATE_VISIBLE: True},
        )
        self.validate_loaded_queue = [self.my_button]

    def click_button(self):
        self.load_page()
        self.my_button.click()
```


## Controls

Controls wrap a UI element selector with automatic retry, caching, and reporting.

```python
SWADLControl(
    name="search_box",      # used in all log output — be descriptive
    selector="#APjFqb",     # CSS selector (Selenium) or key=value pairs (pywinauto)
    has_text="Submit",      # optional: match only elements containing this text
    is_text="Submit",       # optional: match only elements with exactly this text
    index=0,                # optional: take the nth match after text filtering
    validation={VALIDATE_VISIBLE: True},  # optional: used by engine-based validation
)
```

### Control methods

| Method | What it does |
|--------|-------------|
| `control.click()` | Click the element. Retries on stale element. |
| `control.set_value(value="text")` | Type into the element. |
| `control.submit()` | Submit the form containing the element. |
| `control.get_exist()` | Returns `True` if the element exists. |
| `control.get_visible()` | Returns `True` if the element is visible. |
| `control.get_enabled()` | Returns `True` if the element is enabled. |
| `control.get_value()` | Returns the element's text. |
| `control.validate(validation={...})` | Run engine-based validation checks. |

All methods accept `timeout=` (seconds to retry) and `end_time=` (absolute deadline).
Pass `end_time` through a chain of calls to share a single timeout budget.

### Selector substitution

Selectors support f-string style substitution from `test_data`:

```python
self.row = SWADLControl(name="row", selector="tr[data-id='{row_id}']")
# At runtime, {row_id} is filled from test_data["row_id"]
```


## Validations

Every validation comes in three flavors with identical signatures:

| Flavor | Default | On failure |
|--------|---------|-----------|
| `assert_*` | non-fatal | accumulates; raises at end of test |
| `require_*` | fatal | raises `SWADLTestError` immediately |
| `expect_*` | non-fatal | logs a warning; never raises |

Pass `fatal=True` to any of them to override the default.

```python
self.assert_equal(x=result, y="expected")
self.assert_true(exper=flag)
self.assert_in(member=item, container=collection)
self.require_true(exper=page_loaded, fatal=True)   # stops the test immediately
self.expect_equal(x=count, y=5)                    # warning only
```

Accumulated non-fatal failures are reported in `tearDown`.


## Engine-Based Testing

Rather than writing individual assertions for every control, you can declare what
each control should look like and have the engine verify them all:

```python
# In a section:
self.validate_loaded_queue = [self.username, self.password, self.submit_btn]

# Calling this verifies all three are visible:
self.validate_loaded()

# Or validate any list with any validation dict:
self.validate_controls(
    controls=[self.username, self.password],
    validation={VALIDATE_VISIBLE: True, VALIDATE_ENABLED: True},
)
```

Validation dict keys:

| Key | Value | Meaning |
|-----|-------|---------|
| `VALIDATE_EXIST` | `True`/`False` | element must / must not exist |
| `VALIDATE_VISIBLE` | `True`/`False` | element must / must not be visible |
| `VALIDATE_ENABLED` | `True`/`False` | element must / must not be enabled |
| `VALIDATE_UNIQUE` | `True`/`False` | selector must match exactly one element |
| `VALIDATE_TEXT` | `"string"` | element text must equal this |
| `VALIDATE_INPUT` | `True` | type the control's `key` value into the field |
| `VALIDATE_CLICK` | `True` | click the element as part of the validation pass |


## Interface Support

SWADL ships with adapters for five automation libraries. The right choice depends on what you're automating:

| Interface | Driver class | Best for | Platform | Selector type |
|-----------|-------------|----------|----------|---------------|
| **Selenium** | `SeleniumDriver` | Web apps (Chrome, Edge) | Cross-platform | CSS / XPath |
| **Playwright** | `PlaywrightDriver` | Modern SPAs, async-heavy web apps | Cross-platform | CSS / XPath / text |
| **pyautogui** | `PyautoguiDriver` | Any app, no accessibility tree required | Cross-platform | Image file (screenshot) |
| **dogtail** | `DogtailDriver` | Native Linux/GTK/KDE desktop apps | Linux only | `"role:name"` (AT-SPI2) |
| **pywinauto** | `PywinautoDriver` | Windows desktop apps (UIA / Win32) | Windows only | `"key=value"` criteria |

### When to use each

**Selenium** — the default. Use for any web app where you control the browser. Mature, well-documented, huge selector support.

**Playwright** — prefer over Selenium for modern SPAs with heavy client-side rendering. Built-in auto-waiting means fewer explicit sleeps. The `page.locator()` API finds elements without needing explicit waits.

**pyautogui** — the nuclear option. Finds elements by screenshot-matching rather than the DOM or accessibility tree. Use when:
- The app has no AT-SPI2 support (many Electron, Qt, and proprietary apps)
- You can't install browser automation
- Pixel-perfect UI testing is the goal
Limitation: `element.text` is not available (no accessibility tree); use OCR or read state another way.

**dogtail** — the Linux equivalent of pywinauto. Walks the AT-SPI2 accessibility tree, so selectors are semantic (`"push button:OK"`, `"text"`). Requires `at-spi2-core` service running (`export AT_SPI_BUS_ADDRESS` or `dbus-run-session`). Works well with GNOME, KDE, GTK apps.

**pywinauto** — Windows only. Walks the UIA/Win32 accessibility tree. Selector format: `"auto_id=btnOK,class_name=Button"` (comma-separated key=value pairs).

### Choosing between Playwright and Selenium

Both drive real browsers via Chrome DevTools Protocol. Playwright advantages:
- Auto-waits for elements to be actionable before interacting (fewer flaky tests)
- `locator.all()` for element lists without manual WebDriverWait
- Better TypeScript/IDE support for test authors
- Built-in screenshot diff support

Selenium advantages:
- Longer community history, more Stack Overflow answers
- Works with Firefox, Safari, and Edge out of the box
- Widely understood in QA teams

### Choosing between dogtail and pyautogui (Linux desktop)

Use **dogtail** when the app exposes AT-SPI2 (GNOME/GTK apps, most KDE apps). Selectors are semantic and stable across UI changes.

Use **pyautogui** when the app doesn't expose AT-SPI2 (many Electron apps, Qt apps without AT-SPI plugin, proprietary tools). It degrades gracefully but requires maintaining reference screenshot images.

### Adding a new interface

Subclass `SWADLDriver` and `SWADLElement` in `SWADL/engine/swadl_driver.py`:

```python
class MyElement(SWADLElement):
    def text(self): ...
    def click(self): ...
    def send_keys(self, *value, **kwargs): ...
    # ... implement remaining abstract methods

class MyDriver(SWADLDriver):
    def find_elements(self, selector): ...
    def quit(self): ...
    # ... implement remaining abstract methods
```

The interface is selected via the `SELENIUM_BROWSER` environment variable (default: `chrome`).


## Data Flow

All test state lives in `test_data` (`cfgdict[TEST_DATA]`), a shared dictionary
passed implicitly through the entire stack. This makes every piece of state
inspectable at any point and eliminates argument passing between layers.

```python
# In the test:
self.test_data[SEARCH_KEY] = "python"

# In the flow (reads and writes test_data):
self.search_page.do_search()   # reads SEARCH_KEY, writes SEARCH_RESULT_TITLES_LIST

# In the test (reads results):
self.assert_in(member="Python.org", container=self.test_data[SEARCH_RESULT_TITLES_LIST])
```


## Project Structure

```
your_project/
├── tests/          ← SWADLTest subclasses; data + flow calls + assertions only
├── flows/          ← SWADLBaseFlow subclasses; orchestrate sections
└── page_sections/  ← SWADLPageSection subclasses; UI interaction

swadl/
├── SWADL/engine/   ← framework source
├── Project/        ← demo tests (Google search)
├── learning/       ← in-progress example tests
└── bin/            ← helper scripts (googledemo, runatest)
```


## Requirements

- Python 3.9+
- Selenium 4+ (Chrome or Edge WebDriver on PATH)
- Selenium 4+ (Chrome or Edge WebDriver on PATH)
- Playwright (optional): `pip install playwright && playwright install chromium`
- pyautogui (optional, cross-platform): `pip install pyautogui`
- dogtail (optional, Linux AT-SPI2): `pip install dogtail` + `at-spi2-core` system service
- pywinauto (optional, Windows desktop): `pip install pywinauto`
