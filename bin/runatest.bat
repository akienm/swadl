@echo off
cls
if not %1.==/q. (
    echo runatest.bat called with %1 %2 %3 %4 %5 %6 %7 %8 %9
    echo 2024 Akien Maciain
    echo Purpose: To clean up from the last run, and display output files
    echo Usage:
    echo    Runs under cmd.exe
    echo    Run with: runatest [1] [2] [3]
    echo        [1] = runner (nose2 or pytest or whatever)
    echo        [2] = script name in whatever form the specified test runner wants
    echo              nose2 prefers without the .py
    echo              pytest prefers with the .py
    echo        [3] whatever other arguments
)
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
echo.
if exist FAILURE_*.png del FAILURE_*.png
if exist test_*.log del test_*.log
echo Calling: %1 %2 %3 %4 %5 %6 %7 %8 %9
%1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist test_failures.log goto done
echo test_failures.log:
type test_failures.log
echo.
echo For all test results: type test_results.log
:done
