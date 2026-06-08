// Copyright 2026 Rinat Ishmaev
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

using System.Diagnostics;

namespace KdCatalog;

/// <summary>
/// Запуск встроенного backend (KdCatalogServer.exe / KdCatalogWorker.exe) в режиме «сервер».
/// </summary>
public sealed class PortableHost : IDisposable
{
    private readonly List<Process> _processes = new();

    public void StartServer(string catalogRoot)
    {
        var baseDir = AppContext.BaseDirectory;
        ApplyEnvFile(baseDir);

        var serverExe = Path.Combine(baseDir, "KdCatalogServer.exe");
        var workerExe = Path.Combine(baseDir, "KdCatalogWorker.exe");
        var agentExe = Path.Combine(baseDir, "KdCatalogAiAgent", "KdCatalogAiAgent.exe");

        if (!string.IsNullOrWhiteSpace(catalogRoot))
        {
            Environment.SetEnvironmentVariable("CATALOG_ROOT", catalogRoot);
        }

        if (File.Exists(serverExe))
        {
            StartProcess(serverExe, "", baseDir);
        }
        else
        {
            StartPythonFallback(baseDir, catalogRoot);
        }

        if (File.Exists(workerExe))
        {
            StartProcess(workerExe, "", baseDir);
        }

        if (File.Exists(agentExe))
        {
            StartProcess(agentExe, "", Path.GetDirectoryName(agentExe) ?? baseDir);
        }
    }

    private static void ApplyEnvFile(string baseDir)
    {
        var envPath = Path.Combine(baseDir, ".env");
        if (!File.Exists(envPath))
        {
            return;
        }

        foreach (var rawLine in File.ReadAllLines(envPath))
        {
            var line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#'))
            {
                continue;
            }

            var eq = line.IndexOf('=');
            if (eq <= 0)
            {
                continue;
            }

            var key = line[..eq].Trim();
            var value = line[(eq + 1)..].Trim();
            Environment.SetEnvironmentVariable(key, value);
        }
    }

    private void StartProcess(string fileName, string arguments, string workingDirectory)
    {
        var startInfo = new ProcessStartInfo
        {
            FileName = fileName,
            Arguments = arguments,
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            CreateNoWindow = false,
        };
        var proc = Process.Start(startInfo);
        if (proc is not null)
        {
            _processes.Add(proc);
        }
    }

    private void StartPythonFallback(string baseDir, string catalogRoot)
    {
        var backendDir = Path.Combine(baseDir, "backend");
        if (!Directory.Exists(backendDir))
        {
            MessageBox.Show(
                "Не найден KdCatalogServer.exe и папка backend.\nУстановите полный пакет CED-Server.",
                "CED",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
            return;
        }

        var startInfo = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000",
            WorkingDirectory = backendDir,
            UseShellExecute = false,
            CreateNoWindow = false,
        };
        if (!string.IsNullOrWhiteSpace(catalogRoot))
        {
            startInfo.Environment["CATALOG_ROOT"] = catalogRoot;
        }

        var proc = Process.Start(startInfo);
        if (proc is not null)
        {
            _processes.Add(proc);
        }
    }

    public void Dispose()
    {
        foreach (var process in _processes)
        {
            try
            {
                if (!process.HasExited)
                {
                    process.Kill(entireProcessTree: true);
                }
            }
            catch
            {
                // игнорируем при завершении
            }
            finally
            {
                process.Dispose();
            }
        }
        _processes.Clear();
    }
}
