@echo off
echo Rice Mill Management System - Dependency Installation
echo =====================================================

echo Checking Python version...
python --version

echo.
echo Installing dependencies with Python 3.13 compatibility...
python install_dependencies.py

echo.
echo Installation completed!
pause
