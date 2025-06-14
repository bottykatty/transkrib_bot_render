@echo off
cd /d %~dp0
set /p msg=Введите сообщение коммита: 
git add .
git commit -m "%msg%"
git push origin main
pause