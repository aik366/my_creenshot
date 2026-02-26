@echo off

call %~dp0.venv\Scripts\activate

cd %~dp0


python run.py

pause