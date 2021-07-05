@echo off
py -m coverage run --source=. -m pytest
py -m coverage report
IF "%1"=="html" (py -m coverage html & start htmlcov/index.html)