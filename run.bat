@echo off
setlocal enableextensions enabledelayedexpansion
chcp 65001 >nul

REM Переходим в папку скрипта (корень проекта)
cd /d "%~dp0"

echo === Строим Docker-образ ===
docker build -t converter .

echo === Запускаем контейнер на http://127.0.0.1:63591 ===
docker stop converter_container >nul 2>&1
docker rm converter_container >nul 2>&1
docker run --name converter_container -p 63591:8000 converter

pause