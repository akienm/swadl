@echo off
:: Cleans up debris from last time
cls
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
