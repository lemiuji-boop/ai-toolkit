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

import { apiFetch } from "./client";

export type ActivityItem = {
  id: string;
  type: string;
  title: string;
  detail?: string | null;
  progress?: number | null;
  created_at: string;
};

export type CalculationOverview = {
  calculation_id: string;
  files_count: number;
  jobs_running: number;
  jobs_completed: number;
  last_job_progress: number;
  documents_count: number;
};

export function fetchActivity(token: string, calculationId: string) {
  return apiFetch<ActivityItem[]>(`/api/v1/calculations/${calculationId}/activity`, {}, token);
}

export function fetchOverview(token: string, calculationId: string) {
  return apiFetch<CalculationOverview>(`/api/v1/calculations/${calculationId}/overview`, {}, token);
}

export function fetchCalculationFiles(token: string, calculationId: string) {
  return apiFetch<
    { id: string; original_name: string; mime_type: string; size_bytes: number; created_at: string }[]
  >(`/api/v1/calculations/${calculationId}/files`, {}, token);
}
