#!/usr/bin/env bash
# Copyright 2026 Rinat Ishmaev
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail
cd "$(dirname "$0")"
LOG="build-ubuntu-local-wine.log"
echo "=== KTO AI Editor: Windows portable EXE build on Ubuntu via local Wine ===" | tee "$LOG"
echo "Project: $PWD" | tee -a "$LOG"
if ! command -v node >/dev/null 2>&1; then
  echo "ERROR: Node.js is not installed." | tee -a "$LOG"
  echo "Recommended install via nvm or NodeSource, then rerun this script." | tee -a "$LOG"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm is not installed." | tee -a "$LOG"
  exit 1
fi
if ! command -v wine >/dev/null 2>&1; then
  echo "ERROR: Wine is not installed." | tee -a "$LOG"
  echo "Install on Ubuntu: sudo apt update && sudo apt install -y wine64" | tee -a "$LOG"
  exit 1
fi
echo "Node: $(node -v)" | tee -a "$LOG"
echo "npm: $(npm -v)" | tee -a "$LOG"
echo "Wine: $(wine --version)" | tee -a "$LOG"
echo "=== Installing dependencies ===" | tee -a "$LOG"
npm install --no-audit --no-fund 2>&1 | tee -a "$LOG"
echo "=== Building EXE ===" | tee -a "$LOG"
DEBUG=electron-builder npx electron-builder --win portable --x64 --publish=never 2>&1 | tee -a "$LOG"
echo "=== Done. Output files: ===" | tee -a "$LOG"
find dist -maxdepth 2 -type f -print | tee -a "$LOG"
