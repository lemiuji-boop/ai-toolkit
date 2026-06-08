<!--
Copyright 2026 Rinat Ishmaev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<template>
  <AppShell>
    <v-container fluid class="pa-6">
      <h1 class="text-h5 mb-4">Мониторинг и аналитика</h1>

      <v-row v-if="overview?.ai">
        <v-col cols="12" md="4">
          <v-card class="pa-4">
            <div class="text-caption">ИИ-агент</div>
            <div :class="overview.ai.agent_reachable ? 'text-success' : 'text-error'">
              {{ overview.ai.agent_reachable ? "доступен" : "недоступен" }}
            </div>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card class="pa-4">
            <div class="text-caption">Ollama (туннель)</div>
            <div :class="overview.ai.ollama_available ? 'text-success' : 'text-warning'">
              {{ overview.ai.ollama_available ? "доступен" : "нет (OCR без LLM)" }}
            </div>
            <div v-if="overview.ai.ollama_url" class="text-caption mt-1">{{ overview.ai.ollama_url }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row v-if="overview">
        <v-col cols="12" md="3">
          <v-card class="pa-4">
            <div class="text-caption">Документов в БД</div>
            <div class="text-h4">{{ overview.database.documents }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="pa-4">
            <div class="text-caption">Обрабатывается</div>
            <div class="text-h4 text-warning">{{ overview.database.analysis_pending }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="pa-4">
            <div class="text-caption">Ошибки анализа</div>
            <div class="text-h4 text-error">{{ overview.database.analysis_failed }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" md="3">
          <v-card class="pa-4">
            <div class="text-caption">INBOX на разбор</div>
            <div class="text-h4">{{ overview.database.inbox_pending }}</div>
          </v-card>
        </v-col>
      </v-row>

      <v-card class="pa-4 mt-4">
        <div class="text-subtitle-1 mb-2">Подключены сейчас ({{ overview?.active_count ?? 0 }})</div>
        <v-table density="compact">
          <thead>
            <tr>
              <th>Логин</th>
              <th>Роль</th>
              <th>Последняя активность</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in overview?.active_sessions ?? []" :key="s.user_id">
              <td>{{ s.login }}</td>
              <td>{{ s.role }}</td>
              <td>{{ formatTime(s.last_seen) }}</td>
            </tr>
          </tbody>
        </v-table>
      </v-card>

      <v-alert v-if="overview?.database.stuck_processing" type="warning" class="mt-4">
        Зависшие обработки: {{ overview.database.stuck_processing }}
      </v-alert>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

interface Overview {
  ai?: {
    agent_reachable: boolean;
    ollama_available: boolean;
    ollama_url: string;
  };
  database: Record<string, number>;
  active_sessions: Array<{ user_id: number; login: string; role: string; last_seen: string }>;
  active_count: number;
}

const overview = ref<Overview | null>(null);
let timer: ReturnType<typeof setInterval> | null = null;

const formatTime = (v: string): string => new Date(v).toLocaleString("ru-RU");

const load = async (): Promise<void> => {
  const { data } = await apiClient.get("/monitoring/overview");
  overview.value = data;
};

onMounted(() => {
  void load();
  timer = setInterval(() => void load(), 30000);
});
onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>
