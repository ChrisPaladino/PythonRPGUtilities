@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)

echo Launching Ker Nethalas Manager...
%PY% -m ker_nethalas.interfaces.pyqt_main
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Program exited with code %EXIT_CODE%.
    echo If dependencies are missing, run: %PY% -m pip install -e .[dev]
    pause
)

exit /b %EXIT_CODE%
