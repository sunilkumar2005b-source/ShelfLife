@echo off
title Reset ShelfLife Demo State
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0seed-demo.ps1"
pause
