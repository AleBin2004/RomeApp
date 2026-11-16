@echo off
cd /d "%~dp0"
py -m pip install -q -r requirements.txt
start "" http://localhost:8080
py server.py
