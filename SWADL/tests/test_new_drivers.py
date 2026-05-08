"""Tests for pyautogui, dogtail, and Playwright driver adapters.

All tests use mocks — no real browser, display, or AT-SPI service required.
pyautogui requires tkinter + a display; it's injected as a fake module so tests
run headlessly without system packages. dogtail and playwright import cleanly.
"""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# pyautogui calls sys.exit at import if tkinter is missing — inject a fake.
_fake_pyautogui = ModuleType("pyautogui")
_fake_pyautogui.click = MagicMock()
_fake_pyautogui.typewrite = MagicMock()
_fake_pyautogui.press = MagicMock()
_fake_pyautogui.hotkey = MagicMock()
_fake_pyautogui.screenshot = MagicMock()
_fake_pyautogui.locateAllOnScreen = MagicMock(return_value=[])
sys.modules["pyautogui"] = _fake_pyautogui

from SWADL.engine.swadl_driver import (
    DogtailDriver,
    DogtailElement,
    PlaywrightDriver,
    PlaywrightElement,
    PyautoguiDriver,
    PyautoguiElement,
    SWADLDriver,
    SWADLElement,
)

# ── pyautogui ─────────────────────────────────────────────────────────────────


class TestPyautoguiElement:
    def _region(self):
        r = MagicMock()
        r.left = 10
        r.top = 20
        r.width = 100
        r.height = 50
        return r

    def test_is_displayed_true(self):
        el = PyautoguiElement(self._region())
        assert el.is_displayed() is True

    def test_is_enabled_true(self):
        el = PyautoguiElement(self._region())
        assert el.is_enabled() is True

    def test_text_raises(self):
        el = PyautoguiElement(self._region())
        with pytest.raises(NotImplementedError):
            _ = el.text

    def test_click_calls_pyautogui(self):
        r = self._region()
        el = PyautoguiElement(r)
        with patch("pyautogui.click") as mock_click:
            el.click()
        mock_click.assert_called_once_with(60, 45)  # left+w//2, top+h//2

    def test_send_keys_types(self):
        el = PyautoguiElement(self._region())
        with patch("pyautogui.click"), patch("pyautogui.typewrite") as mock_type:
            el.send_keys("hello")
        mock_type.assert_called_once_with("hello", interval=0.02)

    def test_submit_presses_enter(self):
        el = PyautoguiElement(self._region())
        with patch("pyautogui.press") as mock_press:
            el.submit()
        mock_press.assert_called_once_with("enter")


class TestPyautoguiDriver:
    def test_find_elements_returns_list(self):
        r = MagicMock()
        r.left, r.top, r.width, r.height = 0, 0, 10, 10
        with patch("pyautogui.locateAllOnScreen", return_value=[r]):
            driver = PyautoguiDriver()
            els = driver.find_elements("button.png")
        assert len(els) == 1
        assert isinstance(els[0], PyautoguiElement)

    def test_find_elements_bad_selector_raises(self):
        driver = PyautoguiDriver()
        with pytest.raises(ValueError):
            driver.find_elements(123)

    def test_save_screenshot(self):
        driver = PyautoguiDriver()
        with patch("pyautogui.screenshot") as mock_ss:
            driver.save_screenshot("out.png")
        mock_ss.assert_called_once_with("out.png")

    def test_get_raises(self):
        with pytest.raises(NotImplementedError):
            PyautoguiDriver().get("http://example.com")

    def test_quit_noop(self):
        PyautoguiDriver().quit()  # should not raise

    def test_actions_raises(self):
        with pytest.raises(NotImplementedError):
            _ = PyautoguiDriver().actions

    def test_is_swadl_driver_subclass(self):
        assert issubclass(PyautoguiDriver, SWADLDriver)


# ── dogtail ───────────────────────────────────────────────────────────────────


class TestDogtailElement:
    def _node(self, name="OK", role="push button", showing=True, sensitive=True):
        n = MagicMock()
        n.name = name
        n.roleName = role
        n.showing = showing
        n.sensitive = sensitive
        return n

    def test_text_returns_name(self):
        el = DogtailElement(self._node(name="Cancel"))
        assert el.text == "Cancel"

    def test_is_displayed(self):
        el = DogtailElement(self._node(showing=True))
        assert el.is_displayed() is True

    def test_is_enabled(self):
        el = DogtailElement(self._node(sensitive=True))
        assert el.is_enabled() is True

    def test_click_delegates(self):
        node = self._node()
        el = DogtailElement(node)
        el.click()
        node.click.assert_called_once()

    def test_send_keys_delegates(self):
        node = self._node()
        el = DogtailElement(node)
        el.send_keys("abc")
        node.typeText.assert_called_once_with("abc")

    def test_is_swadl_element_subclass(self):
        assert issubclass(DogtailElement, SWADLElement)


class TestDogtailDriver:
    def _mock_app(self):
        app = MagicMock()
        node = MagicMock()
        node.roleName = "push button"
        node.name = "OK"
        app.findChildren.return_value = [node]
        return app, node

    def test_find_elements_role_only(self):
        app, node = self._mock_app()
        with patch("dogtail.tree.root") as mock_root:
            mock_root.application.return_value = app
            driver = DogtailDriver("myapp")
            els = driver.find_elements("push button")
        assert len(els) == 1
        assert isinstance(els[0], DogtailElement)

    def test_find_elements_role_and_name(self):
        app, node = self._mock_app()
        with patch("dogtail.tree.root") as mock_root:
            mock_root.application.return_value = app
            driver = DogtailDriver("myapp")
            els = driver.find_elements("push button:OK")
        assert len(els) == 1

    def test_get_raises(self):
        app, _ = self._mock_app()
        with patch("dogtail.tree.root") as mock_root:
            mock_root.application.return_value = app
            driver = DogtailDriver("myapp")
        with pytest.raises(NotImplementedError):
            driver.get("http://example.com")

    def test_is_swadl_driver_subclass(self):
        assert issubclass(DogtailDriver, SWADLDriver)


# ── Playwright ────────────────────────────────────────────────────────────────


class TestPlaywrightElement:
    def _locator(self, text="Submit", visible=True, enabled=True):
        loc = MagicMock()
        loc.inner_text.return_value = text
        loc.is_visible.return_value = visible
        loc.is_enabled.return_value = enabled
        return loc

    def test_text(self):
        el = PlaywrightElement(self._locator(text="Login"))
        assert el.text == "Login"

    def test_is_displayed(self):
        assert PlaywrightElement(self._locator(visible=True)).is_displayed() is True
        assert PlaywrightElement(self._locator(visible=False)).is_displayed() is False

    def test_is_enabled(self):
        assert PlaywrightElement(self._locator(enabled=True)).is_enabled() is True

    def test_click(self):
        loc = self._locator()
        PlaywrightElement(loc).click()
        loc.click.assert_called_once()

    def test_send_keys(self):
        loc = self._locator()
        PlaywrightElement(loc).send_keys("pw")
        loc.fill.assert_called_once_with("pw")

    def test_submit(self):
        loc = self._locator()
        PlaywrightElement(loc).submit()
        loc.press.assert_called_once_with("Enter")

    def test_is_swadl_element_subclass(self):
        assert issubclass(PlaywrightElement, SWADLElement)


class TestPlaywrightDriver:
    def _page(self):
        page = MagicMock()
        page.locator.return_value.all.return_value = [MagicMock(), MagicMock()]
        return page

    def test_find_elements_returns_list(self):
        page = self._page()
        driver = PlaywrightDriver(page)
        els = driver.find_elements("button")
        assert len(els) == 2
        assert all(isinstance(e, PlaywrightElement) for e in els)

    def test_get_navigates(self):
        page = self._page()
        PlaywrightDriver(page).get("https://example.com")
        page.goto.assert_called_once_with("https://example.com")

    def test_save_screenshot(self):
        page = self._page()
        PlaywrightDriver(page).save_screenshot("shot.png")
        page.screenshot.assert_called_once_with(path="shot.png")

    def test_quit_closes_browser(self):
        page = self._page()
        browser = MagicMock()
        PlaywrightDriver(page, browser).quit()
        browser.close.assert_called_once()

    def test_quit_no_browser_noop(self):
        PlaywrightDriver(self._page(), None).quit()  # should not raise

    def test_maximize_sets_viewport(self):
        page = self._page()
        PlaywrightDriver(page).maximize_window()
        page.set_viewport_size.assert_called_once_with({"width": 1920, "height": 1080})

    def test_actions_raises(self):
        with pytest.raises(NotImplementedError):
            _ = PlaywrightDriver(self._page()).actions

    def test_is_swadl_driver_subclass(self):
        assert issubclass(PlaywrightDriver, SWADLDriver)
