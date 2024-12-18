@echo off
:: USAGE AND COMMENTS
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

:: SORT PYTHONPATH
set "current_dir=%cd%"
set "root_dir="

:find_root
if exist "%current_dir%\swadl.root" (
    set "root_dir=%current_dir%"
    goto :found_root
)
if "%current_dir%"=="%current_dir:~0,3%" goto :not_found
for %%I in ("%current_dir%\..") do set "current_dir=%%~fI"
goto :find_root

:not_found
echo swadl.root not found in any parent directory.
goto :end_pythonpath

:found_root
set "found="
for %%i in ("%PYTHONPATH:;=" "%") do (
    if /i "%%~i"=="%root_dir%" set "found=1"
)

if not defined found (
    set "PYTHONPATH=%root_dir%;%PYTHONPATH%"
    echo Added %root_dir% to PYTHONPATH
) else (
    echo %root_dir% is already in PYTHONPATH
)

:end_pythonpath
endlocal & set "PYTHONPATH=%PYTHONPATH%"

:: SORT RUNNER
set runner=
if not %1.==pytest. if not %1.==nose2. set runner=nose2

:: SORT LOGGING
setlocal enabledelayedexpansion
set "found="
for %%a in (%*) do (
    if "%%a:~0,6%"=="--log=" set "found=1"
)
set "debugflag="
if not defined found set "debugflag=--log=debug"

:: NOW ANNOUNCE AND RUN
echo Calling: python -m %runner% %debugflag% %1 %2 %3 %4 %5 %6 %7 %8 %9
python -m %runner% %debugflag% %1 %2 %3 %4 %5 %6 %7 %8 %9

:: NOW TERMINAL REPORT
echo Done from: python -m %runner% %debugflag% %1 %2 %3 %4 %5 %6 %7 %8 %9
if not exist test_failures.log goto done
echo test_failures.log:
type test_failures.log
echo.
echo For all test results: type test_results.log
:done
