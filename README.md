# SWADL: Selenium Webdriver Accelerated Development Library
Akien Maciain akienm@gmail.com

## Purpose:
Implements a best practices based reusable selenium framework suitable for process automation. This includes test automation, business process automation, and any similar. 

This is intended to be both reusable code to launch from, and to be an illustration of test automation framework design best practices.

## Installation
This discussion assumes a Windows 10 compatible machine. The paths will be different on other
platforms, but should be substantially the same.

You will need:
    * winget install --id=Oracle.JDK.18  -e 
    * Download the Selenium JAR file. https://www.selenium.dev/downloads/
      and put it on your path

## Status:
As of this writing, this is a work in progress. See TODO.md for more information

## Organization:
* `seleniumpoc/bin`: various whatnot I use to develop this
* `seleniumpoc/demos`: The demos. As of now, there's one
* `seleniumpoc/engine`: The SWADL Framework
* `seleniumpoc/README.md`: This file
* `seleniumpoc/TODO.md`: An overview of some of the major points of this framework still to implement
* `seleniumpoc/ToO.md`: Theory of operation

## Overview of Major Architectural Goals:
1) This code implements a set of interfaces intended to replace the Selenium interfaces, and to handle all the synchronization for you.
3) Implement flows (also sometimes called storyboards), and strict encapulation between tests, flows, and pages.
4) Demonstrate "engine-based-testing", where an engine can validate all the controls on a given page.
5) Portray code that can gather all the errors, not just stop at the first one.

## Platform:
All the examples and support code was developed on Windows. Almost all the python code, including the SWADL components, is platform independent. 

The one known exception is the driver creation code in SWADL_constants.py. You will need to add code there to support additional platforms as needed.

The demo tests run on either nose2 or pytest.

## Terminology:
- Assertion - Assertions are condition tests which prove that the test can continue or not. Failed assertions are almost always "Errors".
- Error - This means the test experienced an error and was unable to complete. This is not the same as a "failure".
- Failure - This means that the thing the test was actually testing didn't meet expectations. This may mean something as small as a control which was the wrong color, it's noted and the test continues. Validattions can usually be marked with the keyword `fatal`. If the call has `fatal=True`, that means if it fails, raise an exception.
- Validate - this means to perform a test that, if it fails, means a test failure. Sometimes Validations with fatal=True are ALSO errors.

## Setup
For use in developing automation, just pip install swadl (TODO)

For development on the framework, you will need:
* a SWADL_HOME environment variable, which is the root of the SWADL system.
* Typical directory layout:
```
%SWADL_HOME%
├───bin
│       selenium-server-standalone.jar
└───swadl
    ├───bin
    ├───demos
    └───engine
```
* Add `%SWADL_HOME%\bin` to your path
* Download Selenium from https://www.selenium.dev/downloads/ - put it in `%SWADL_USERHOME%\bin`, and rename it from something like selenium-server-standalone-3.141.59.jar to selenium-server-standalone.jar
* You will also need to download a driver, such as chromedriver, edgedriver, firefox, etc, and add that to `%SWADL_USERHOME%\bin`, which also has to be on your path.
* Setting up SWADL to handle your browser selection happens inside of SWADLconstants.py, toward the end. This will eventually be separated out into it's own file.
* Install python libraries from `seleniumpoc/requirements.txt`

## Usage (within tests):
1) In a general sense, tests are responsible for DATA and KNOWING WHICH FLOWS TO INVOKE. Tests NEVER talk to pages directly.
2) Flows know which pages do the work, and what to ask them to do, but encapsulation prevents them from knowing anything about how it's done.
3) Pages are responsible for determining that they're loaded before they perform any actions.
4) All conditions that should be met before performaing a test should be explicitly asserted or validated before the test continues. This means pages assert that they're loaded before attempting to access controls.
5) Tests often put their data into dictionaries, and put that into `cfgdict[SUBSTITUTION_SOURCES]`, from which values are pulled at runtime.

## Engine Based Testing:
Engine based testing means controls are processed from a list, and told to validate given properties of the control. An example of this is the `SWADLPageSection.validate_loaded()` which uses the page's `validate_loaded_queue` to scan to see if the page is loaded.

But it's not just validate the states of the control, the engine can also set values and so on. So a list of controls, with the `key` property set on one, tells the engine to put that value into the control.

See seleniumpoc\ENGINE.md

## Other notes:
* Uses unitTest style fixtures of setUp() and tearDown(). IMPORTANT: YOU MUST CALL SUPER! Both methods are used in the framework.
* Calls to methods who's name starts with `validate_` are calls to code which will verify different aspects of the code. FOr example, `SWADLPage.validate_loaded()` will verify that the page is loaded. Unlike most `validate_` methods, this one is assumed to be fatal if it fails (the keyword `fatal=True` is the default on this validate, most of the others have `fatal=False`).
