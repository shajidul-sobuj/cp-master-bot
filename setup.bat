@echo off
REM CP Master Bot - Setup Script for Windows

echo ====================================
echo CP Master Bot - Setup Script
echo ====================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.9 or higher.
    pause
    exit /b 1
)
echo Python is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created
echo.

REM Activate virtual environment and install requirements
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo .env file created
    echo.
    echo IMPORTANT: Edit .env file and add your BOT_TOKEN
    echo Get your token from @BotFather on Telegram
) else (
    echo .env file already exists
)

echo.
echo ====================================
echo Setup complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file and add your BOT_TOKEN
echo 2. Run: run.bat ^(or python bot.py^)
echo.
echo Happy coding!
pause
