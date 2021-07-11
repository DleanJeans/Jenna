@echo off
py -m coverage run --source=. -m pytest
py -m coverage report
IF "%1"=="html" py -m coverage html
CHOICE /N /C YN /M "Do you wanna open the coverage report website? (Y/N)"%2
IF ERRORLEVEL==2 GOTO :EOF
start htmlcov/index.html