@echo off
if not %1.==/q. (
    echo nose2runner.bat called with %1 %2 %3 %4 %5 %6 %7 %8 %9
    echo 2024 Akien Maciain
    echo Purpose: To run the google_unit_tests demo using nose2
    echo Usage:
    echo    Runs under cmd.exe
    echo    Run with: nose2runner [script name without .py] [and whatever other arguments]
    echo    Batch file does:
    echo        calls runatest which cleans up output from last time
    echo        passing in nose2 as the runner
    echo        along with whatever other specified parameters
)
runatest nose2 %1 %2 %3 %4 %5 %6 %7 %8 %9
