@echo on
if not %SWADL_HOME%.==. goto keep_going
echo.
echo SWADL_HOME not set error.
goto done

:keep_going
cd %SWADL_HOME%
cd Project\demos
if %1.==p. (
    pytestrunner google_unit_tests.py
) else (
    nose2runner google_unit_tests
)
:done
