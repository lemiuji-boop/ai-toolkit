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

export type DocumentSummary = {
  id: string;
  document_type: string;
  file_id: string;
  page_count: number;
  quality_score: number | null;
};

export type FactDto = {
  id: string;
  field: string;
  value: string;
  confidence: number;
  method: string;
  evidence_text?: string | null;
  source_page?: number | null;
  review_status?: string;
};

export function listCalculationDocuments(token: string, calculationId: string) {
  return apiFetch<DocumentSummary[]>(
    `/api/v1/calculations/${calculationId}/documents`,
    {},
    token,
  );
}

export function listDocumentFacts(token: string, documentId: string) {
  return apiFetch<FactDto[]>(`/api/v1/documents/${documentId}/facts`, {}, token);
}

export function patchFact(token: string, factId: string, value: string) {
  return apiFetch<FactDto>(
    `/api/v1/facts/${factId}`,
    { method: "PATCH", body: JSON.stringify({ value }) },
    token,
  );
}

export function confirmFact(token: string, factId: string) {
  return apiFetch<FactDto>(`/api/v1/facts/${factId}/confirm`, { method: "POST" }, token);
}
