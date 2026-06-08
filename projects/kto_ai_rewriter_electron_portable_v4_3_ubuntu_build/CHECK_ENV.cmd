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
echo  KTO AI Editor - environment check
echo =========================================================
echo.
echo Project folder:
echo %CD%
echo.

echo Checking Node.js...
where node
if errorlevel 1 (
  echo [ERROR] Node.js not found.
) else (
  node -v
)
echo.

echo Checking npm...
where npm
if errorlevel 1 (
  echo [ERROR] npm not found.
) else (
  npm -v
)
echo.

echo Checking npm registry access...
npm ping
echo.
echo If npm ping fails, build cannot download Electron/electron-builder.
echo.
pause
