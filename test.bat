@echo off
IF "%1"=="fast" (
    py -m pytest --durations=5 -m "not (enable_socket or slow)"
    GOTO :EOF
) ELSE (
IF "%1"=="slow" (
    py -m pytest --durations=5 -m "enable_socket or slow"
    GOTO :EOF
))
py -m pytest --durations=5 %*