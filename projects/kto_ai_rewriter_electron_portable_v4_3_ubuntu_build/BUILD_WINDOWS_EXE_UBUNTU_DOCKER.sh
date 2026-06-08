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
LOG="build-ubuntu-docker.log"
IMAGE="electronuserland/builder:wine"
echo "=== KTO AI Editor: Windows portable EXE build on Ubuntu via Docker ===" | tee "$LOG"
echo "Project: $PWD" | tee -a "$LOG"
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is not installed." | tee -a "$LOG"
  echo "Install Docker or use BUILD_WINDOWS_EXE_UBUNTU_LOCAL_WINE.sh" | tee -a "$LOG"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon is not available for this user." | tee -a "$LOG"
  echo "Try: sudo systemctl start docker" | tee -a "$LOG"
  echo "Or run: sudo ./BUILD_WINDOWS_EXE_UBUNTU_DOCKER.sh" | tee -a "$LOG"
  echo "Or add user to docker group: sudo usermod -aG docker $USER ; then reboot/login again" | tee -a "$LOG"
  exit 1
fi
mkdir -p .cache/electron .cache/electron-builder dist
HOST_UID="$(id -u)"
HOST_GID="$(id -g)"
echo "=== Pulling/using Docker image: $IMAGE ===" | tee -a "$LOG"
docker pull "$IMAGE" | tee -a "$LOG"
echo "=== Building EXE ===" | tee -a "$LOG"
docker run --rm -t \
  -e ELECTRON_CACHE="/root/.cache/electron" \
  -e ELECTRON_BUILDER_CACHE="/root/.cache/electron-builder" \
  -e HOST_UID="$HOST_UID" \
  -e HOST_GID="$HOST_GID" \
  -v "$PWD":/project \
  -v "$PWD/.cache/electron":/root/.cache/electron \
  -v "$PWD/.cache/electron-builder":/root/.cache/electron-builder \
  "$IMAGE" \
  /bin/bash -lc 'cd /project && npm install --no-audit --no-fund && npx electron-builder --win portable --x64 --publish=never && chown -R "$HOST_UID:$HOST_GID" /project/dist /project/node_modules /project/package-lock.json 2>/dev/null || true' \
  2>&1 | tee -a "$LOG"
echo "=== Done. Output files: ===" | tee -a "$LOG"
find dist -maxdepth 2 -type f -print | tee -a "$LOG"
