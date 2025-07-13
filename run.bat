@echo off
echo "Creating Venv"
python -m venv .venv

echo "Running main.py"
.venv\Scripts\python.exe src\main.py

echo ------------------------------------------
echo "The output folder contains the chat logs!"
echo ------------------------------------------
pause