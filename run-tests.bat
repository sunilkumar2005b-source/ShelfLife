@echo off
title ShelfLife Test Suite Runner
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run-tests.ps1"
pause
