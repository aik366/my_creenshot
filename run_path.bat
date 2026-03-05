@echo off
cd /d "%~dp0"

:: Активация виртуального окружения
call .venv\Scripts\activate.bat

:: Запуск бота
python run.py

pause