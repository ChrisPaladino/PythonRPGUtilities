@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PY=.venv\Scripts\python.exe"
) else (
    set "PY=python"
)

echo Validating content JSON files...
%PY% -c "from ker_nethalas.content.repository import validate_all_content; validate_all_content(); print('Content validation passed.')"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Content validation failed with code %EXIT_CODE%.
)

pause
exit /b %EXIT_CODE%
