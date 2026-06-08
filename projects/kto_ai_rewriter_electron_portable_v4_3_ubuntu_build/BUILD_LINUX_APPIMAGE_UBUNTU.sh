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
LOG="build-linux-appimage.log"
echo "=== KTO AI Editor: Linux AppImage build on Ubuntu ===" | tee "$LOG"
npm install --no-audit --no-fund 2>&1 | tee -a "$LOG"
npx electron-builder --linux AppImage --x64 --publish=never 2>&1 | tee -a "$LOG"
echo "=== Done. Output files: ===" | tee -a "$LOG"
find dist -maxdepth 2 -type f -print | tee -a "$LOG"
