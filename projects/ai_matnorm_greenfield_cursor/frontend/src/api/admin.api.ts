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

import { apiFetch } from "@/api/client";

export type AiProvider = {
  id: string;
  name: string;
  provider_type: string;
  base_url: string | null;
  is_enabled: boolean;
  priority: number;
};

export function listProviders(token: string) {
  return apiFetch<AiProvider[]>("/api/v1/admin/ai-providers", {}, token);
}

export function createProvider(
  token: string,
  body: {
    name: string;
    provider_type: string;
    base_url?: string;
    api_key?: string;
    priority?: number;
  },
) {
  return apiFetch<AiProvider>("/api/v1/admin/ai-providers", {
    method: "POST",
    body: JSON.stringify(body),
  }, token);
}

export function testProvider(token: string, id: string) {
  return apiFetch<{ status: string; detail: string }>(
    `/api/v1/admin/ai-providers/${id}/test-connection`,
    { method: "POST" },
    token,
  );
}

export function deleteProvider(token: string, id: string) {
  return apiFetch<void>(`/api/v1/admin/ai-providers/${id}`, { method: "DELETE" }, token);
}

export function listSecurityEvents(token: string) {
  return apiFetch<{ id: string; event_type: string; created_at: string }[]>(
    "/api/v1/admin/security-events",
    {},
    token,
  );
}
