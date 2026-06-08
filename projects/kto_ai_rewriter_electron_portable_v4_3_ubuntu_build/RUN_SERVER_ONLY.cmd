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

set PORT=8787
if "%ADMIN_PASSWORD%"=="" set ADMIN_PASSWORD=admin123

echo Starting local server on port %PORT%...
echo Admin password is taken from ADMIN_PASSWORD environment variable.
echo If not set, temporary password is admin123.
echo.
node server.js
pause
