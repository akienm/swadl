# SWADL: Selenium Webdriver Accelerated Development Library
Akien Maciain akienm@gmail.com

## Purpose of this library
Implements a best practices based reusable Test Automation framework suitable for 
process automation. This includes test automation, business process automation, 
and any similar.

While this is currently implemented only to talk to selenium, one TODO item is to make
the selenium interface component a layer, and add libraries for pywinauto and other 
low level interfaces/

This is intended to be both reusable code to launch from, and to be an illustration of test automation framework design best practices.

## Installation for Automation Developers
1) Go to a location on your local hard drive to put SWADL. 
   Personally, I reccomend having one folder for all your repos, 
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
All the examples and support code was developed on Windows. Almost all the 
python code, including the SWADL components, is platform independent. The
batch files and shell scripts try to mirror one another, but are not perfect.

The demo tests run on either nose2 or pytest.

On Windows, the demo code can be run once the setup is complete by typing either:

        googledemo
or 

        googledemo p      (this one for pytest on windows)

On Linux, we can try

        bash $SWADL_HOME\bin\googledemo.sh

by default, these will run under nose2 (because I like the output better) and
the second one runs under pytest.

## Status of the code as of this writing
Originally developed as a proof of concept. Not all functions yet fully implemented and
debugged as of this writing. See TODO.md for more information.

## Overview of Major Architectural Goals:
1) This code implements a set of interfaces intended to replace the 
   Selenium interfaces, and to handle all the synchronization for you.
3) Implement flows (also sometimes called storyboards), and strict 
   encapsulation between tests, flows, and pages.
4) Demonstrate "engine-based-testing", where an engine can validate 
   all the controls on a given page.
5) Portray code that can gather all the errors, not just stop at the 
   first one.

## Terminology:
- Assertion - Assertions are condition tests which prove the test case. 
- Validation - a validation is basically an automatically generated assertion
- Error - This means the test experienced an error and was unable to complete. This is not the same as a "failure".

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
│       selenium-server-standalone.jar
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
4) All conditions that should be met before performaing a test should be explicitly asserted or validated before the test continues. This means pages assert that they're loaded before attempting to access controls.
5) Tests often put their data into dictionaries, and put that into `cfgdict[SUBSTITUTION_SOURCES]`, from which values are pulled at runtime.

## Engine Based Testing:
Engine based testing means controls are processed from a list, and told to validate given properties of the control. An example of this is the `SWADLPageSection.validate_loaded()` which uses the page's `validate_loaded_queue` to scan to see if the page is loaded.

But it's not just validate the states of the control, the engine can also set values and so on. So a list of controls, with the `key` property set on one, tells the engine to put that value into the control.

See seleniumpoc\ENGINE.md

## Other notes:
* Uses unitTest style fixtures of setUp() and tearDown(). IMPORTANT: YOU MUST CALL SUPER! Both methods are used in the framework.
* Calls to methods who's name starts with `validate_` are calls to code which will verify different aspects of the code. FOr example, `SWADLPage.validate_loaded()` will verify that the page is loaded. Unlike most `validate_` methods, this one is assumed to be fatal if it fails (the keyword `fatal=True` is the default on this validate, most of the others have `fatal=False`).
