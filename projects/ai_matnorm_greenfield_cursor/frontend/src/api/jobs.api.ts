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

import { API_BASE, apiFetch } from "./client";

export function startDocumentJob(
  token: string,
  calculationId: string,
  fileIds: string[],
) {
  return apiFetch<{ id: string; status: string; progress_percent: number }>(
    "/api/v1/jobs/document-processing",
    {
      method: "POST",
      body: JSON.stringify({ calculation_id: calculationId, file_ids: fileIds }),
    },
    token,
  );
}

export async function jobControl(token: string, jobId: string, action: "pause" | "resume" | "cancel") {
  await fetch(`${API_BASE}/api/v1/jobs/${jobId}/${action}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}
