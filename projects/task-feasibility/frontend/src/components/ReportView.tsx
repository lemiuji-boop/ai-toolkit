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

import { useState } from "react";
import type { AnalyzeResponse } from "../api/client";

interface ReportViewProps {
  data: AnalyzeResponse;
}

type Tab = "assignment" | "cost" | "safety";

export default function ReportView({ data }: ReportViewProps) {
  const [tab, setTab] = useState<Tab>("assignment");

  const downloadMd = () => {
    const blob = new Blob([data.final_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "matfes-assignment.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  const content =
    tab === "assignment"
      ? data.final_markdown
      : tab === "cost"
        ? data.cost_forecast_markdown
        : JSON.stringify(data.safety, null, 2);

  return (
    <section>
      <div className="report-meta">
        <span className="badge">Уровень: {data.complexity_level}</span>
        <span className="badge">FI: {data.feasibility_score.toFixed(2)}</span>
        <span className="badge">
          {data.is_feasible ? "Осуществимо" : "Требует pivot"}
        </span>
      </div>

      {data.modified_options.length > 0 && (
        <ul className="options-list">
          {data.modified_options.map((opt, i) => (
            <li key={i}>
              <strong>{opt.title}</strong>
              <p>{opt.scope}</p>
              <small>{opt.tradeoffs}</small>
            </li>
          ))}
        </ul>
      )}

      {data.warnings.length > 0 && (
        <p className="subtitle">Предупреждения: {data.warnings.join("; ")}</p>
      )}

      <div className="tabs">
        <button
          type="button"
          className={tab === "assignment" ? "active" : ""}
          onClick={() => setTab("assignment")}
        >
          Техзадание
        </button>
        <button
          type="button"
          className={tab === "cost" ? "active" : ""}
          onClick={() => setTab("cost")}
        >
          Стоимость
        </button>
        <button
          type="button"
          className={tab === "safety" ? "active" : ""}
          onClick={() => setTab("safety")}
        >
          Безопасность
        </button>
      </div>

      <pre className="report">{content}</pre>

      <div className="actions">
        <button type="button" className="secondary" onClick={downloadMd}>
          Скачать .md
        </button>
      </div>
    </section>
  );
}
