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
echo "=== KTO AI Editor: Ubuntu build environment check ==="
echo "Project folder: $PWD"
echo
if command -v node >/dev/null 2>&1; then
  echo "Node.js: $(node -v)"
else
  echo "Node.js: NOT FOUND"
fi
if command -v npm >/dev/null 2>&1; then
  echo "npm: $(npm -v)"
else
  echo "npm: NOT FOUND"
fi
if command -v docker >/dev/null 2>&1; then
  echo "Docker: $(docker --version)"
  if docker info >/dev/null 2>&1; then
    echo "Docker daemon: OK"
  else
    echo "Docker daemon: NOT AVAILABLE for this user"
    echo "Tip: start Docker or add current user to docker group, or run the build command with sudo docker."
  fi
else
  echo "Docker: NOT FOUND"
fi
if command -v wine >/dev/null 2>&1; then
  echo "Wine: $(wine --version)"
else
  echo "Wine: NOT FOUND"
fi
echo
echo "Recommended build method: BUILD_WINDOWS_EXE_UBUNTU_DOCKER.sh"
echo "Alternative: BUILD_WINDOWS_EXE_UBUNTU_LOCAL_WINE.sh"
