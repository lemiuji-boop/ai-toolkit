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
import { fetchSyncEvents } from "@/api/sync.api";

/** Статус синхронизации для desktop/web offline queue (расширяется по мере необходимости). */
export const useSyncStore = defineStore("sync", () => {
  const pendingCount = ref(0);
  const lastSyncAt = ref<string | null>(null);
  const serverUrl = ref(localStorage.getItem("ai_matnorm_server_url") || import.meta.env.VITE_API_BASE_URL);

  function setServerUrl(url: string) {
    serverUrl.value = url;
    localStorage.setItem("ai_matnorm_server_url", url);
  }

  async function pullEvents(token: string) {
    const events = await fetchSyncEvents(token);
    pendingCount.value = 0;
    lastSyncAt.value = new Date().toISOString();
    return events;
  }

  return { pendingCount, lastSyncAt, serverUrl, setServerUrl, pullEvents };
});
