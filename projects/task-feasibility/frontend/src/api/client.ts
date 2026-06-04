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

/** HTTP-клиент MATFES API */

export interface AnalyzeRequest {
  project_name: string;
  task: string;
  context_lines: number;
}

export interface SafetyPayload {
  is_safe_to_export: boolean;
  detected_violations: string[];
  sanitized_prompt: string;
  encryption_required: boolean;
  hard_blocked: boolean;
}

export interface AnalyzeResponse {
  complexity_level: string;
  feasibility_score: number;
  is_feasible: boolean;
  modified_options: Array<Record<string, string>>;
  estimated_tokens: Record<string, unknown>;
  cost_forecast_markdown: string;
  final_markdown: string;
  safety: SafetyPayload;
  selected_stack: Record<string, string>;
  warnings: string[];
}

const API_BASE = import.meta.env.VITE_API_URL ?? "";

export async function analyzeTask(
  body: AnalyzeRequest,
): Promise<AnalyzeResponse> {
  const resp = await fetch(`${API_BASE}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    const detail = err.detail;
    if (resp.status === 422 && detail) {
      const msg =
        typeof detail === "string"
          ? detail
          : detail.message ??
            "Запрос заблокирован guardrail-слоем. Проверьте текст на секреты.";
      const violations =
        typeof detail === "object" && detail.detected_violations
          ? ` Нарушения: ${detail.detected_violations.join(", ")}`
          : "";
      throw new Error(msg + violations);
    }
    throw new Error(
      typeof detail === "string" ? detail : `Ошибка API: ${resp.status}`,
    );
  }

  return resp.json() as Promise<AnalyzeResponse>;
}
