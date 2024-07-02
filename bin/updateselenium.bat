@echo off
call updatepip
echo y | pip uninstall selenium
echo y | pip install selenium