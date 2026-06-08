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

param([int]$Port = 8787)

$ErrorActionPreference = "Stop"
$baseDir = Split-Path -Parent $PSScriptRoot

function Get-LocalIPv4 {
    $addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254.*" -and
            $_.PrefixOrigin -ne "WellKnown"
        } |
        Sort-Object InterfaceMetric

    if ($addresses -and $addresses.Count -gt 0) {
        return $addresses[0].IPAddress
    }

    $fallback = ipconfig | Select-String -Pattern "IPv4" | Select-Object -First 1
    if ($fallback) {
        return ($fallback.ToString().Split(":")[-1]).Trim()
    }
    return "127.0.0.1"
}

$ip = Get-LocalIPv4
$url = "http://$ip`:$Port"
$content = "[InternetShortcut]`r`nURL=$url`r`nIconFile=%SystemRoot%\System32\shell32.dll`r`nIconIndex=220`r`n"

$outName = "KTO_AI_Editor_Guest.url"
$outPath = Join-Path $baseDir $outName
Set-Content -Path $outPath -Value $content -Encoding ASCII

try {
    $desktop = [Environment]::GetFolderPath("Desktop")
    if ($desktop) {
        Set-Content -Path (Join-Path $desktop $outName) -Value $content -Encoding ASCII
    }
} catch {}

Write-Host "Guest link: $url"
Write-Host "Shortcut created: $outPath"
