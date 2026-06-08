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

import { defineStore } from "pinia";
import { ref } from "vue";
import { API_BASE } from "@/api/client";
import { useAuthStore } from "./auth.store";

export type JobLogEntry = {
  type: string;
  payload?: Record<string, unknown>;
};

export const useJobStore = defineStore("job", () => {
  const jobId = ref<string | null>(null);
  const progress = ref(0);
  const status = ref("pending");
  const logs = ref<JobLogEntry[]>([]);
  const documentIds = ref<string[]>([]);
  let eventSource: EventSource | null = null;

  function disconnect() {
    eventSource?.close();
    eventSource = null;
  }

  function subscribe(id: string) {
    disconnect();
    jobId.value = id;
    logs.value = [];
    progress.value = 0;
    status.value = "running";
    documentIds.value = [];

    const auth = useAuthStore();
    const url = `${API_BASE}/api/v1/jobs/${id}/stream?token=${encodeURIComponent(auth.accessToken || "")}`;
    eventSource = new EventSource(url);

    const handleEvent = (eventName: string, raw: string) => {
      try {
        const data = JSON.parse(raw) as { type?: string; payload?: Record<string, unknown> };
        const type = data.type || eventName;
        logs.value.push({ type, payload: data.payload });
        if (type === "job_completed") {
          status.value = "completed";
          progress.value = 100;
          const ids = data.payload?.document_ids;
          if (Array.isArray(ids)) documentIds.value = ids as string[];
        }
        if (type === "job_failed") status.value = "failed";
        if (type === "file_classified" && data.payload?.document_id) {
          const docId = String(data.payload.document_id);
          if (!documentIds.value.includes(docId)) documentIds.value.push(docId);
        }
      } catch {
        logs.value.push({ type: eventName, payload: { raw } });
      }
      pollProgress(id);
    };

    eventSource.onmessage = (ev) => handleEvent("message", ev.data);

    const named = [
      "job_started",
      "file_processing",
      "file_classified",
      "fact_extracted",
      "job_completed",
      "job_failed",
      "stream_end",
    ];
    for (const name of named) {
      eventSource.addEventListener(name, (ev) => {
        handleEvent(name, (ev as MessageEvent).data);
        if (name === "stream_end") disconnect();
      });
    }
  }

  async function pollProgress(id: string) {
    const auth = useAuthStore();
    const r = await fetch(`${API_BASE}/api/v1/jobs/${id}`, {
      headers: { Authorization: `Bearer ${auth.accessToken}` },
    });
    if (r.ok) {
      const j = await r.json();
      progress.value = j.progress_percent ?? 0;
      status.value = j.status ?? status.value;
    }
  }

  return {
    jobId,
    progress,
    status,
    logs,
    documentIds,
    subscribe,
    disconnect,
    pollProgress,
  };
});
