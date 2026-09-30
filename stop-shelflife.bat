@echo off
title Stop ShelfLife Services
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-shelflife.ps1"
pause
