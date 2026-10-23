@echo off
title Git OCR Hub
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\run-hub.ps1"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [INFO] Une erreur s'est produite ou l'application s'est terminee.
    pause
)
