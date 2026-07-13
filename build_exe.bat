@echo off
REM Builds BungusTweaks.exe - a single file, no Python required to run it.
REM Run this FROM the pc-tweaker folder (double-click it or run in a terminal).
 
echo Installing PyInstaller if needed...
python -m pip install pyinstaller --quiet
 
echo.
echo Building BungusTweaks.exe ...
python -m PyInstaller --onefile --noconsole --uac-admin --name "BungusTweaks" --icon "assets\icon.ico" --add-data "assets;assets" --add-data "tools;tools" app.py
 
if not exist "dist\BungusTweaks.exe" (
    echo.
    echo ============================================================
    echo BUILD FAILED - dist\BungusTweaks.exe was not created.
    echo Scroll up and check the error message above.
    echo ============================================================
    pause
    exit /b 1
)
 
echo.
echo Done! Find your app at: dist\BungusTweaks.exe
echo You can copy just that one .exe to any Windows PC and run it - no Python needed.
pause