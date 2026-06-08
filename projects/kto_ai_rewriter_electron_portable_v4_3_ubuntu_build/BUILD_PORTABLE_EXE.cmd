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
echo  KTO AI Editor - Portable EXE build
echo =========================================================
echo.
echo Project folder:
echo %CD%
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js not found.
  echo Install Node.js LTS, close this window, open the project folder again and rerun this file.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm not found. It is normally installed with Node.js.
  pause
  exit /b 1
)

echo Environment versions:
node -v
npm -v
echo.

echo Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build-log.txt del /q build-log.txt

echo Installing dependencies. First run can take several minutes.
echo Log file: build-log.txt
call npm install --no-audit --no-fund >> build-log.txt 2>&1
if errorlevel 1 goto error

echo.
echo Building portable EXE...
call npm run dist:portable >> build-log.txt 2>&1
if errorlevel 1 goto error

echo.
echo =========================================================
echo  DONE
echo =========================================================
echo Portable EXE is in this folder:
echo %CD%\dist
echo.
dir dist
echo.
pause
exit /b 0

:error
echo.
echo =========================================================
echo  BUILD ERROR
echo =========================================================
echo Open build-log.txt and check the last lines.
echo Common reasons:
echo 1. No internet access to download Electron packages.
echo 2. Corporate proxy/antivirus blocks npm.
echo 3. Project path contains Cyrillic, spaces or special characters.
echo 4. No write access to project folder.
echo.
echo Recommended path:
echo C:\kto_ai_rewriter_electron_portable_v4_2_ascii_fixed
echo.
echo Last 40 lines of build-log.txt:
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path build-log.txt) { Get-Content build-log.txt -Tail 40 }"
echo.
pause
exit /b 1
