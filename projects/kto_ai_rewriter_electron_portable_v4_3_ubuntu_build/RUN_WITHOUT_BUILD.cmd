REM Copyright 2026 Rinat Ishmaev
REM
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.
REM You may obtain a copy of the License at
REM
REM     http://www.apache.org/licenses/LICENSE-2.0
REM
REM Unless required by applicable law or agreed to in writing, software
REM distributed under the License is distributed on an "AS IS" BASIS,
REM WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
REM See the License for the specific language governing permissions and
REM limitations under the License.

@echo off
setlocal
chcp 65001 >nul

echo =========================================================
echo  KTO AI Editor - run without EXE build
echo =========================================================
echo.

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm not found. Install Node.js LTS.
  pause
  exit /b 1
)

call npm install --no-audit --no-fund
if errorlevel 1 goto error

call npm start
exit /b 0

:error
echo.
echo [ERROR] Dependency installation or application start failed.
echo Check internet connection, proxy, antivirus and write access.
pause
exit /b 1
