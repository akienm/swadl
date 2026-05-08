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


# ── pyautogui adapter ─────────────────────────────────────────────────────────
# Coordinate/image-based automation. Works on apps with no accessibility tree.
# Selector for find_elements: image filename (str) or (x, y, w, h) region tuple.
# Requires: pip install pyautogui


class PyautoguiElement(SWADLElement):
    """Wraps a screen region located via image matching."""

    def __init__(self, region):
        self._region = region  # (left, top, width, height) named tuple

    def __eq__(self, other):
        if isinstance(other, PyautoguiElement):
            return self._region == other._region
        return NotImplemented

    def __hash__(self):
        return hash(self._region)

    @property
    def text(self):
        raise NotImplementedError("pyautogui does not provide text extraction; use OCR")

    def is_displayed(self):
        return self._region is not None

    def is_enabled(self):
        return True  # no accessibility state available

    def click(self):
        import pyautogui

        cx = self._region.left + self._region.width // 2
        cy = self._region.top + self._region.height // 2
        pyautogui.click(cx, cy)

    def send_keys(self, *value, **kwargs):
        import pyautogui

        self.click()
        pyautogui.typewrite("".join(str(v) for v in value), interval=0.02)

    def submit(self):
        import pyautogui

        pyautogui.press("enter")


class PyautoguiDriver(SWADLDriver):
    """Screen-level driver using pyautogui image matching."""

    def find_elements(self, selector):
        """Locate all occurrences of image file `selector` on screen.

        selector: path to a reference image file (PNG/BMP).
        Returns a list of PyautoguiElement for each match found.
        """
        import pyautogui

        if isinstance(selector, str):
            regions = list(pyautogui.locateAllOnScreen(selector, confidence=0.9))
            return [PyautoguiElement(r) for r in regions]
        raise ValueError(
            f"pyautogui selector must be an image file path, got {selector!r}"
        )

    def save_screenshot(self, filename):
        import pyautogui

        pyautogui.screenshot(filename)

    def get(self, url):
        raise NotImplementedError("pyautogui does not support URL navigation")

    def quit(self):
        pass  # no session to close

    def maximize_window(self):
        import pyautogui

        pyautogui.hotkey("winleft", "up")

    @property
    def actions(self):
        raise NotImplementedError("Action chains not supported for pyautogui")


# ── dogtail adapter (AT-SPI2) ─────────────────────────────────────────────────
# Accessibility-tree automation for native Linux/GTK/KDE apps.
# Selector format: "role:name" e.g. "push button:OK" or just "push button"
# Requires: pip install dogtail; at-spi2-core service must be running.


class DogtailElement(SWADLElement):
    """Wraps a dogtail Accessible node."""

    def __init__(self, node):
        self._node = node

    def __eq__(self, other):
        if isinstance(other, DogtailElement):
            return self._node == other._node
        return NotImplemented

    def __hash__(self):
        return id(self._node)

    @property
    def text(self):
        return getattr(self._node, "name", "") or getattr(self._node, "text", "")

    def is_displayed(self):
        return getattr(self._node, "showing", True)

    def is_enabled(self):
        return getattr(self._node, "sensitive", True)

    def click(self):
        self._node.click()

    def send_keys(self, *value, **kwargs):
        self._node.typeText("".join(str(v) for v in value))

    def submit(self):
        from dogtail.rawinput import pressKey

        pressKey("Return")


class DogtailDriver(SWADLDriver):
    """AT-SPI2 driver via dogtail. app_name must be the process name."""

    def __init__(self, app_name: str):
        import dogtail.tree

        self._app = dogtail.tree.root.application(app_name)

    def find_elements(self, selector: str):
        """Find nodes by selector.

        Selector format: "role:name" (e.g. "push button:OK") or just "role".
        Both parts are matched case-insensitively.
        """
        parts = selector.split(":", 1)
        role = parts[0].strip()
        name = parts[1].strip() if len(parts) > 1 else None
        if name:
            nodes = self._app.findChildren(
                lambda n: n.roleName.lower() == role.lower()
                and n.name.lower() == name.lower()
            )
        else:
            nodes = self._app.findChildren(lambda n: n.roleName.lower() == role.lower())
        return [DogtailElement(n) for n in (nodes or [])]

    def save_screenshot(self, filename):
        self._app.grab_focus()
        import subprocess

        subprocess.run(["scrot", filename], check=False)

    def get(self, url):
        raise NotImplementedError("dogtail does not support URL navigation")

    def quit(self):
        import dogtail.rawinput

        self._app.grab_focus()
        dogtail.rawinput.keyCombo("<Alt>F4")

    def maximize_window(self):
        import dogtail.rawinput

        self._app.grab_focus()
        dogtail.rawinput.keyCombo("<Super>Up")

    @property
    def actions(self):
        raise NotImplementedError("Action chains not supported for dogtail")


# ── Playwright adapter ────────────────────────────────────────────────────────
# Modern async-first browser automation. Better SPA support than Selenium.
# Use PlaywrightDriver with a sync_playwright page object.
# Requires: pip install playwright; playwright install chromium
#
# Usage:
#   from playwright.sync_api import sync_playwright
#   with sync_playwright() as p:
#       browser = p.chromium.launch()
#       page = browser.new_page()
#       driver = PlaywrightDriver(page, browser)
#       # pass driver to SWADLBaseAutomation(driver=driver)


class PlaywrightElement(SWADLElement):
    """Wraps a Playwright Locator."""

    def __init__(self, locator):
        self._locator = locator

    def __eq__(self, other):
        if isinstance(other, PlaywrightElement):
            return self._locator == other._locator
        return NotImplemented

    def __hash__(self):
        return id(self._locator)

    @property
    def text(self):
        return self._locator.inner_text()

    def is_displayed(self):
        return self._locator.is_visible()

    def is_enabled(self):
        return self._locator.is_enabled()

    def click(self):
        self._locator.click()

    def send_keys(self, *value, **kwargs):
        self._locator.fill("".join(str(v) for v in value))

    def submit(self):
        self._locator.press("Enter")


class PlaywrightDriver(SWADLDriver):
    """Playwright sync-API browser driver."""

    def __init__(self, page, browser=None):
        self._page = page
        self._browser = browser  # held for quit()

    def find_elements(self, selector):
        """Returns PlaywrightElement for each match of CSS/XPath selector."""
        locators = self._page.locator(selector).all()
        return [PlaywrightElement(loc) for loc in locators]

    def save_screenshot(self, filename):
        self._page.screenshot(path=filename)

    def get(self, url):
        self._page.goto(url)

    def quit(self):
        if self._browser:
            self._browser.close()

    def maximize_window(self):
        self._page.set_viewport_size({"width": 1920, "height": 1080})

    @property
    def actions(self):
        raise NotImplementedError(
            "Use Playwright's built-in chaining instead of action chains"
        )
