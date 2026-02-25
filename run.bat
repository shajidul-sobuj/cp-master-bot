@echo off
REM CP Master Bot - Run Script for Windows

echo ====================================
echo Starting CP Master Bot...
echo ====================================
echo.

REM Check if .env exists
if not exist .env (
    echo Error: .env file not found!
    echo Please run setup.bat first or create .env file manually
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the bot
echo Starting bot...
python bot.py

pause
