# ENGINE.md
Purpose: This is a description of what is meant by engine based testing, and how it's used.

## Problem Statement
In many programmatical testing environments, the tests interact with the controls they're required to interact with, and don't pay attention to the rest of the controls.

One can add code to check each thing, but most of us never think to, as it's a lot of extra work that is very interface specific.

But we can increase the coverage of the test with an engine to do the heavy lifting for us, and

## Object Wrappers For Controls
In this approach, rather than the "control" just being a selector, the control has an object wrapper around it. That object wrapper encapsulates the selector, but it also carries a lot more. With this approach, we can say `mypage.mycontrol.click()`, the framework will handle waiting for the control to appear, and will click on it as soon as it's ready.

## Engine Based Testing Approach
But even better, because the object can wrap any data about the object, it can include information about how to test the control. So if the control has a dictionary called `self.validation`, it can contain keys such as:
* VERIFY_ENABLED
* VERIFY_EXIST
* VERIFY_PROPERTY
* VERIFY_UNIQUE
* VERIFY_VALUE
* VERIFY_VISIBLE

And several more... If the value is say `{VERIFY_EXIST: True}`, and the control is asked to validate itself, then it will pass if the control is present. If the value were `{VERIFY_EXIST: False}`, then it would pass only if the control were not present.

Most importantly, this allows you to do things like:
```
    def user_login(self):
        self.load_page()
        self.validate_controls(
            self.base_page_control_list,
            {VERIFY_VISIBLE: True},
        )
        self.validate_controls(
            self.controls_visible_only_after_login,
            {VERIFY_VISIBLE: False},
        )
```
This also allows us to do this:
```
def validate_loaded(self, controls=None, fatal=True,
                    timeout=None, **kwargs):
        if not controls:
            controls = self.validate_loaded_queue
        result = self.validate_controls(
            controls=controls,
            fatal=fatal,
            timeout=timeout,
            validation={VALIDATE_VISIBLE: True},
            **kwargs,
        )
        return result
```
This validates that the page is loaded. `self.validate_loaded_queue` contains a list of controls which must be present to affirm the page is loaded. Note that `fatal=True`. That means that if this call fails, it's a fatal error and the test has to stop.

## How We Use It
When we arrive on a page, we can validate all their controls with a single call. If there is a change, such as more controls becoming available after a login, then we can have a list for before the login, and one for after.

Controls can have their own `validation` keyword, but we can also specify the validation we want... So before we're logged in, we might list `page.validate_controls(controls_visible_before_login, {VALIDATE_VISIBLE: True})` and `page.validate_controls(controls_not_visible_before_login, {VALIDATE_VISIBLE: False})`.

