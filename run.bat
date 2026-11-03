@echo off
rem Starts Portimao without a terminal window (this window closes at once).
cd /d "%~dp0"
where pyw >nul 2>&1
if not errorlevel 1 (
    start "" pyw -3 "%~dp0Portimao.pyw"
    exit /b 0
)
where pythonw >nul 2>&1
if not errorlevel 1 (
    start "" pythonw "%~dp0Portimao.pyw"
    exit /b 0
)
echo Python 3 was not found. Please install it from https://www.python.org/downloads/
echo and tick "Add Python to PATH" during the installation, then run this again.
pause
exit /b 1
