@ECHO OFF
GOTO MAIN

:MAIN
pdm run py -3.11 ./src/bot/main.py
PAUSE
GOTO MAIN