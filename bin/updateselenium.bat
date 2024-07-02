@echo off
if not %1.==/q (
    echo updateselenium.bat called with %1 %2 %3 %4 %5 %6 %7 %8 %9
    echo 2024 Akien Maciain
    echo Purpose: updates selenium to latest
    echo Usage:
    echo    Runs under cmd.exe
    echo    updateselenium
    echo.
    echo Now updating selenium
    echo python.exe -m pip install --upgrade pip
)
call updatepip /q
echo y | pip uninstall selenium
echo y | pip install selenium