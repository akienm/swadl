# SWADL: Selenium Webdriver Accelerated Development Library
Akien Maciain akienm@gmail.com

## Purpose of this library
Implements the AutomationBlox best practices based reusable Test Automation framework 
suitable for process automation. This includes test automation, business process 
automation, and any similar.

While this is currently implemented only to talk to selenium, one TODO item is to make
the selenium interface component a layer, and add libraries for pywinauto and other 
low level interfaces.

This is intended to be both reusable code to launch from, and to be an illustration of test automation framework design best practices.

## Installation for Automation Developers
1) Go to a location on your local hard drive to put SWADL. 
   Personally, I recommend having one folder for all your repos, 
   but you do you. :) 


2) Fetch the repo: 

        git clone https://github.com/akienm/swadl.git
3) cd into the new repo

        cd swadl

4) Set the environment variable SWADL_HOME to point to the repo's local
   directory. You can use SystemPropertiesAdvanced.exe to set an environment 
   variable.

        CMD.EXE: google for setting environment variables under windows

        bash: SWADL_HOME=$(pwd)     (recommend putting in .bashrc or similar)

3) Add %SWADL_HOME%\bin to your path

        CMD.EXE: google for setting environment variables under windows

        bash: PATH=PATH:$(pwd)/bin     (recommend putting in .bashrc or similar)
4) Install the repo:

        pip install -e %SWADL_HOME%
    Doing this will also take care of installing your requirements

## Running the demo:
All the python code, including the SWADL components, is platform independent. 
The batch files and shell scripts do their best to mirror one another.
The shell scripts are all written for Bash. This means that on a mac, there's 
another step. Please ask google how to set bash as your default shell (no, it won't 
break anything else). 

The demo tests run on either nose2 or pytest.

On both Linux and Windows, the demo code can be run once the setup is complete by 
typing either:

        googledemo
or 

        googledemo p      (this one for pytest)

by default, these will run under nose2 (because I like the output better) and
the second one runs under pytest.

## Running the a test you write:
First, you need to be in the same folder as the file you're trying to run.
Then you need to decide if you wanna run nose2 or pytest:

        runatest nose2 --log=debug you_python_test_file_goes_here_without_the_py_at_the_end
or

        runatest pytest --log=debug you_python_test_file_goes_here_with_the_py_at_the_end.py

runatest is another batch/shell script file that cleans up from the last run before launching the test.


## Terminology:
Sorry this isn't in alpha order, but this is the order to understand them in.

- AutomationBlox - This is a set of best practices which minimizes maintenance of automation. It includes:
  - Test case - only knows data and which flows to call. Assertions all performed here.
  - Flow layer - knows which pages and what to ask them to do, but nothing else.
  - Page "Sections" - Pages have headers and footers and other reusable parts, so we call 'em "Sections"
  - Page strict encapsulation
    - Test cases can't use data from or call methods on a page object.
That's what we mean by encapsulation.
    - Test cases may ONLY make calls to flow objects. Those know which pages
and what to ask them to do. But that information is hidden from the tests
themselves.
  - Single data dictionary to pass from test cases to flows to pages.
    - This causes the test case to become a state machine, and we can examine all
the state data in the test_data dictionary.
  - Smart page object methods - no more separate methods for login_successfully() and 
login_with_error(). One method handles all cases and reports back.
  - Same dictionary carries "what happened" indicators back on known keys. Eg: 
    - Each page loaded will add itself to the test data
    - Smart page objects note whether operations succeeded or failed
  - Common calling conventions for all methods. eg All page and control interaction methods have 
timeout=20 as a default. Any of these will accept timeout=new value. 
  - Language independent best practices model. 
to the failure log.
- Validation - A validation is the general case of an assertion. Which is to say, an assertion is a validation.
  - Validations come in 3 forms, and assertions are just one.
    - Assertion - Assertions are condition tests which prove the test case. 
      - Assertions are only performed by the test case in AutomationBlox
      - Assertions are never performed by the flow or section(page) levels.
      - Assertions raise assertion errors, and that is used by the test runners to indicate failure. 
      - Assertions can be either fatal or non-fatal, and are non-fatal by default. 
      - If an assertion failure means the test cannot continue, it must be marked fatal=True. 
      - Assertions which are not fatal are accumulated and a fatal assertion is raised at the end.
      - Basic assertions are defined in swadl_base.py. Section and control assertions are defined
    in their respective base classes.
      - Each assertion will emit a banner to the debug log, and if it has failed, 
    - Requires - The second kind of validation is a require. 
      - Where all assertions default to non-fatal, requires all default to fatal.
      - Require failures produce a SWADLTestError exception.
      - Requires can be called from anywhere. Tests, flows or sections.
      - For each assertion, there is a complementary require. So assert_true() 
    is accompanied by require_true()
      - Requires also produce the same kind of banner output as an assertion.
      - A require failure usually means the test can't continue, but is not the
test case itself that has failed, rather we couldn't complete the test.
    specific thing the test is trying to test.
    - Expects - The third kind of validation is an expect. 
      - Expects all default to fatal=False.
      - Expects do not raise an exception
      - Expect failures log a warning
      - For each assertion, there is a complementary expect. So assert_true() 
    is accompanied by expect_true()
      - Expects also produce the same kind of banner output as an assertion.
 
    
## Status of the code as of this writing
Originally developed as a proof of concept. Not all functions yet fully implemented and
debugged as of this writing. See TODO.md for more information.


## How to make your own test
* First, if you haven't done it already, follow the instructions at the
top of this file to get set up. Including running the pip install for this repo.
* Next, make your own repo. 
* For structure, look to the Project folder in this repo, but replace demos
with tests, automation, or whatever is relevant to your project.
* The requirements.txt in the project folder specifies swadl already

## Organization of the code
* `swadl/bin`: various whatnot I use to develop this
* `swadl/Project`: The demos. As of now, there's one
* `swadl/engine`: The SWADL Framework
* `swadl/README.md`: This file
* `swadl/TODO.md`: An overview of some of the major points of this framework still to implement
* `swadl/ToO.md`: Theory of operation (planned)

```
%SWADL_HOME%
├───bin
├───Project
│   ├───demos
│   ├───flows
│   └───page_sections
└───swadl
    ├───engine
    └───helpers
```

## Usage (within tests):
1) In a general sense, tests are responsible for DATA and KNOWING WHICH FLOWS TO INVOKE. Tests NEVER talk to pages directly.
2) Flows know which pages do the work, and what to ask them to do, but encapsulation prevents them from knowing anything about how it's done.
3) Pages are responsible for determining that they're loaded before they perform any actions.
4) All conditions that should be met before performing a test should be explicitly asserted or validated before the test continues. This means pages assert that they're loaded before attempting to access controls.
5) Tests often put their data into dictionaries, and put that into `cfgdict[SUBSTITUTION_SOURCES]`, from which values are pulled at runtime.

## Other notes:
* Uses unitTest style fixtures of setUp() and tearDown(). IMPORTANT: YOU MUST CALL SUPER! Both methods are used in the framework.
* Calls to methods who's name starts with `validate_` are calls to code which will verify different aspects of the code. FOr example, `SWADLPage.validate_loaded()` will verify that the page is loaded. Unlike most `validate_` methods, this one is assumed to be fatal if it fails (the keyword `fatal=True` is the default on this validate, most of the others have `fatal=False`).

## Engine Based Testing:
Engine based testing means controls are processed from a list, and told to validate given properties of the control. An example of this is the `SWADLPageSection.validate_loaded()` which uses the page's `validate_loaded_queue` to scan to see if the page is loaded.

But it's not just validate the states of the control, the engine can also set values and so on. So a list of controls, with the `key` property set on one, tells the engine to put that value into the control.

## Overview of Major Architectural Goals:
1) This code implements a set of interfaces intended to replace the 
   Selenium interfaces, and to handle all the synchronization for you.
3) Implement flows (also sometimes called storyboards), and strict 
   encapsulation between tests, flows, and pages.
4) Demonstrate "engine-based-testing", where an engine can validate 
   all the controls on a given page.
5) Portray code that can gather all the errors, not just stop at the 
   first one.

