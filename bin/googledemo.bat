@echo off
if not %1.==/q. (
    echo googledemo.bat called with %1 %2 %3 %4 %5 %6 %7 %8 %9
    echo 2024 Akien Maciain
    echo Purpose: To run the google_unit_tests demo.
    echo Usage:
    echo    Runs under cmd.exe
    echo    Run with: googledemo
    echo    or: googledemo p
    echo    Runs using nose2 runner by default, because it shows output as it goes
    echo        (easier to debug when running from command line)
    echo    Using the p argument causes pytest to be used instead.
    echo    Batch file does:
    echo        checks environment variable
    echo        cd to demos folder
    echo        calls runatest with either nose2 or pytest
    echo        runatest cleans up output from last time, then runs the test
    echo.
)
if not %SWADL_HOME%.==. goto keep_going
echo.
echo So sad.
echo Friendly person, I cant do this without the
echo SWADL_HOME environment variable being set first
echo Please google how to set environment variables
echo under Windows and try your call again.
echo this is a recoding.
echo.
goto done

:keep_going
cd %SWADL_HOME%
cd Project\demos
if %1.==p. (
    runatest pytest google_unit_tests.py %1 %2 %3 %4 %5 %6 %7 %8 %9
) else (
    runatest nose2 google_unit_tests %1 %2 %3 %4 %5 %6 %7 %8 %9
)
:done
