@echo on
if not %SWADL_HOME%.==. goto keep_going
echo.
echo SWADL_HOME not set error.
goto done

:keep_going
cd %SWADL_HOME%
cd demos
::pytestrunner google_unit_tests.py
nose2runner google_unit_tests
:done
