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

import { FormEvent, useState } from "react";
import { analyzeTask, type AnalyzeResponse } from "../api/client";
import ReportView from "../components/ReportView";

export default function AnalyzePage() {
  const [projectName, setProjectName] = useState("My Project");
  const [task, setTask] = useState("");
  const [contextLines, setContextLines] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await analyzeTask({
        project_name: projectName,
        task,
        context_lines: contextLines,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Неизвестная ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <form onSubmit={onSubmit}>
        <label>
          Название проекта
          <input
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
          />
        </label>
        <label>
          Описание задачи (мин. 10 символов)
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            required
            minLength={10}
            placeholder="Например: Создать CRUD REST API для каталога..."
          />
        </label>
        <label>
          Строк контекста (файлы)
          <input
            type="number"
            min={0}
            value={contextLines}
            onChange={(e) => setContextLines(Number(e.target.value))}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Анализ..." : "Запустить MATFES"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      {result && <ReportView data={result} />}
    </>
  );
}
