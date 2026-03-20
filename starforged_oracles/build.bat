@echo off
echo ============================================================
echo  Building Starforged Oracles -- standalone app
echo ============================================================
echo.

REM Make sure we run relative to this script's location
cd /d "%~dp0"

REM ---- Check Python ----------------------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python was not found.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to tick "Add Python to PATH" during setup.
    pause
    exit /b 1
)

REM ---- Install/upgrade build tools -------------------------------------------
echo Installing PyInstaller and PyYAML...
pip install --quiet --upgrade pyinstaller pyyaml
if errorlevel 1 (
    echo ERROR: pip install failed. See output above.
    pause
    exit /b 1
)

REM ---- Build -----------------------------------------------------------------
echo.
echo Running PyInstaller...
pyinstaller ^
    --name "StarforgedOracles" ^
    --windowed ^
    --onedir ^
    --add-data "data;data" ^
    --distpath "dist" ^
    --workpath "build_temp" ^
    --noconfirm ^
    src/starforged_app.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED. See the output above for details.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS!
echo.
echo  Give your brother the folder:
echo    dist\StarforgedOracles\
echo.
echo  He just needs to double-click  StarforgedOracles.exe
echo  inside that folder to launch the app.
echo ============================================================
pause
