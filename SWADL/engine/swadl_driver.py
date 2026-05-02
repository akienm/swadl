"""
File: swadl_driver.py
Purpose: Interface layer between SWADL and the underlying UI automation technology.

To add a new interface (e.g. Playwright):
  1. Subclass SWADLElement and SWADLDriver
  2. Implement all methods
  3. Register a creator in swadl_cfg.py
"""

from SWADL.engine.swadl_exceptions import SWADLStaleElementError

# ── Base classes (act as both protocol definition and documentation) ──────────


class SWADLElement:
    """Wraps a single UI element. One implementation per interface."""

    @property
    def text(self):
        raise NotImplementedError

    def is_displayed(self):
        raise NotImplementedError

    def is_enabled(self):
        raise NotImplementedError

    def click(self):
        raise NotImplementedError

    def send_keys(self, *value, **kwargs):
        raise NotImplementedError

    def submit(self):
        raise NotImplementedError


class SWADLDriver:
    """Wraps a UI automation session. One implementation per interface."""

    def find_elements(self, selector):
        # Returns list[SWADLElement] matching selector
        raise NotImplementedError

    def save_screenshot(self, filename):
        raise NotImplementedError

    def get(self, url):
        raise NotImplementedError

    def quit(self):
        raise NotImplementedError

    def maximize_window(self):
        # Maximize the active automation surface. Page sections call this
        # during load_page() to ensure consistent layout for selectors.
        # Stub-raise here; concrete adapters override.
        raise NotImplementedError

    @property
    def actions(self):
        # Returns an action-chain builder for gesture sequences (e.g. mouseover).
        # Not all interfaces support this.
        raise NotImplementedError


# ── Selenium adapter ──────────────────────────────────────────────────────────


class SeleniumElement(SWADLElement):

    def __init__(self, element):
        self._element = element

    def __eq__(self, other):
        if isinstance(other, SeleniumElement):
            return self._element == other._element
        return NotImplemented

    def __hash__(self):
        return hash(self._element)

    def _call(self, fn):
        # Runs fn(), translating StaleElementReferenceException to SWADLStaleElementError
        try:
            return fn()
        except Exception as e:
            from selenium.common.exceptions import StaleElementReferenceException

            if isinstance(e, StaleElementReferenceException):
                raise SWADLStaleElementError() from e
            raise

    @property
    def text(self):
        return self._call(lambda: self._element.text)

    def is_displayed(self):
        return self._call(lambda: self._element.is_displayed())

    def is_enabled(self):
        return self._call(lambda: self._element.is_enabled())

    def click(self):
        return self._call(lambda: self._element.click())

    def send_keys(self, *value, **kwargs):
        return self._call(lambda: self._element.send_keys(*value))

    def submit(self):
        return self._call(lambda: self._element.submit())


class SeleniumDriver(SWADLDriver):

    def __init__(self, webdriver):
        self._driver = webdriver

    def find_elements(self, selector):
        from selenium.webdriver.common.by import By

        return [
            SeleniumElement(e)
            for e in self._driver.find_elements(By.CSS_SELECTOR, selector)
        ]

    def save_screenshot(self, filename):
        self._driver.save_screenshot(filename)

    def get(self, url):
        self._driver.get(url)

    def quit(self):
        self._driver.quit()

    def maximize_window(self):
        self._driver.maximize_window()

    @property
    def actions(self):
        from selenium.webdriver.common.action_chains import ActionChains

        return ActionChains(self._driver)


# ── pywinauto adapter (stub) ──────────────────────────────────────────────────
# Selector format: comma-separated key=value pairs, e.g. "auto_id=btnOK,class_name=Button"
# Keys map to pywinauto child_window() criteria.


class PywinautoElement(SWADLElement):

    def __init__(self, element):
        self._element = element

    def __eq__(self, other):
        if isinstance(other, PywinautoElement):
            return self._element == other._element
        return NotImplemented

    def __hash__(self):
        return hash(self._element)

    @property
    def text(self):
        return self._element.window_text()

    def is_displayed(self):
        return self._element.is_visible()

    def is_enabled(self):
        return self._element.is_enabled()

    def click(self):
        self._element.click_input()

    def send_keys(self, *value, **kwargs):
        self._element.type_keys("".join(str(v) for v in value))

    def submit(self):
        self._element.type_keys("{ENTER}")


class PywinautoDriver(SWADLDriver):

    def __init__(self, app, top_window=None):
        self._app = app
        self._window = top_window or app.top_window()

    def find_elements(self, selector):
        criteria = {}
        for part in selector.split(","):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                criteria[k.strip()] = v.strip()
        controls = self._window.children(**criteria)
        return [PywinautoElement(c) for c in controls]

    def save_screenshot(self, filename):
        self._window.capture_as_image().save(filename)

    def get(self, url):
        raise NotImplementedError("pywinauto does not support URL navigation")

    def quit(self):
        self._app.kill()

    def maximize_window(self):
        # Stub until pywinauto path is activated end-to-end. Real impl would
        # call self._window.maximize() — verify against actual pywinauto API
        # when the activation ticket lands.
        raise NotImplementedError("maximize_window not yet wired for pywinauto")

    @property
    def actions(self):
        raise NotImplementedError("Action chains not supported for pywinauto")
