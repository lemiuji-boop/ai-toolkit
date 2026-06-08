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

<script setup lang="ts">
import ProgressBar from "@/components/ui/ProgressBar.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";

export type JobLog = {
  type: string;
  payload?: Record<string, unknown>;
  at?: string;
};

defineProps<{
  progress: number;
  status: string;
  logs: JobLog[];
  active: boolean;
}>();

defineEmits<{
  pause: [];
  resume: [];
  cancel: [];
}>();
</script>

<template>
  <section class="monitor pf-card">
    <div class="head">
      <h2 class="pf-section-title">Ход обработки</h2>
      <StatusBadge :status="status" />
    </div>
    <ProgressBar :value="progress" label="Общий прогресс" />
    <div v-if="active" class="controls">
      <button type="button" class="pf-btn pf-btn-ghost" @click="$emit('pause')">Пауза</button>
      <button type="button" class="pf-btn pf-btn-ghost" @click="$emit('resume')">Продолжить</button>
      <button type="button" class="pf-btn pf-btn-ghost danger" @click="$emit('cancel')">Стоп</button>
    </div>
    <div class="log">
      <div v-for="(e, i) in logs" :key="i" class="log-row">
        <span class="type">{{ e.type }}</span>
        <code v-if="e.payload">{{ JSON.stringify(e.payload) }}</code>
      </div>
      <p v-if="!logs.length" class="pf-muted">Ожидание событий...</p>
    </div>
  </section>
</template>

<style scoped>
.monitor .head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.monitor .pf-section-title {
  margin: 0;
}
.controls {
  display: flex;
  gap: 8px;
  margin: 16px 0;
}
.danger {
  color: var(--pf-danger);
  border-color: #fecaca;
}
.log {
  max-height: 200px;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: var(--pf-radius-sm);
  padding: 12px;
  font-size: 12px;
}
.log-row {
  margin-bottom: 8px;
}
.type {
  font-weight: 600;
  color: var(--pf-primary);
  margin-right: 8px;
}
code {
  color: var(--pf-text-muted);
  word-break: break-all;
}
</style>
