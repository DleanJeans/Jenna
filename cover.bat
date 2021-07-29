@echo off

set slow_tests=enable_socket or slow
if "%1"=="fast" (
    set marker=-m "not (%slow_tests%)"
) else (
if "%1"=="slow" (
    set marker=-m "%slow_tests%"
))

if [%marker%] == [] (
    set args=%*
    goto run_test
)

set args=

:remove_first_arg
shift
if "%1"=="" goto run_test
set args=%args% %1
goto remove_first_arg


:run_test
py -m pytest ^
    --durations=5 ^
    --cov=. ^
    --cov-report xml:cov/cov.xml ^
    --cov-report html:cov/html/ ^
    %marker% %args%

choice /N /C YN /M "Open report page? (Y/N)"
if ERRORLEVEL==2 goto :eof
start cov/html/index.html