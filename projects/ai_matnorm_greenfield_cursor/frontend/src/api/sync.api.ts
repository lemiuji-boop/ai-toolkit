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

export interface SyncEventDto {
  id: string;
  event_type: string;
  payload: Record<string, unknown> | null;
  created_at: string;
}

export function fetchSyncEvents(token: string) {
  return apiFetch<SyncEventDto[]>("/api/v1/sync/events", {}, token);
}

export function pushSyncEvent(
  token: string,
  event_type: string,
  payload?: Record<string, unknown>,
) {
  return apiFetch<SyncEventDto>(
    "/api/v1/sync/push",
    { method: "POST", body: JSON.stringify({ event_type, payload }) },
    token,
  );
}
