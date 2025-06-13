@echo off
setlocal

REM Set paths
set VENV_DIR=.venv
set PYINSTALLER=%VENV_DIR%\Scripts\pyinstaller.exe
set SPEC_FILE=app.spec

REM Check virtual environment
if not exist "%PYINSTALLER%" (
    echo ❌ PyInstaller not found at %PYINSTALLER%
    echo 👉 Run: .venv\Scripts\activate && pip install pyinstaller
    exit /b 1
)

REM Check that .spec file exists
if not exist "%SPEC_FILE%" (
    echo ❌ Spec file "%SPEC_FILE%" not found.
    exit /b 1
)

REM Run PyInstaller with --onefile and the .spec file
echo 🚀 Building executable using PyInstaller...
"%PYINSTALLER%" "%SPEC_FILE%"

echo ✅ Build complete. Check the dist\ directory.

endlocal
