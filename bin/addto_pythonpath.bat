@echo off
setlocal enabledelayedexpansion

set "current_dir=%cd%"
set "found="

for %%i in ("%PYTHONPATH:;=" "%") do (
    if /i "%%~i"=="%current_dir%" set "found=1"
)

if not defined found (
    set "PYTHONPATH=%current_dir%;%PYTHONPATH%"
    echo Added %current_dir% to PYTHONPATH
) else (
    echo %current_dir% is already in PYTHONPATH
)

endlocal & set "PYTHONPATH=%PYTHONPATH%"
