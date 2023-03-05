@ECHO OFF
GOTO MAIN

:MAIN
pdm run python3.11 ./src/bot/main.py
PAUSE
GOTO MAIN