@echo off
if not %1.==/q (
    echo updatepip.bat called with %1 %2 %3 %4 %5 %6 %7 %8 %9
    echo 2024 Akien Maciain
    echo Purpose: updates pip so i don't have to remember the command line
    echo Usage:
    echo    Runs under cmd.exe
    echo    updatepip
    echo.
    echo Now updating pip
    echo python.exe -m pip install --upgrade pip
)
python.exe -m pip install --upgrade pip