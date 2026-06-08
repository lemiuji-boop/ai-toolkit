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
export type ActivityRow = {
  id: string;
  type: string;
  title: string;
  detail?: string | null;
  progress?: number | null;
  created_at: string;
};

defineProps<{
  items: ActivityRow[];
  loading?: boolean;
}>();

function icon(type: string) {
  if (type.includes("job") || type.includes("file_processing")) return "⚙";
  if (type.includes("file")) return "📎";
  if (type.includes("fact")) return "✓";
  if (type.includes("fail")) return "✕";
  return "•";
}

function formatTime(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleString("ru-RU", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}
</script>

<template>
  <section class="history pf-card">
    <h2 class="pf-section-title">История</h2>
    <p v-if="loading" class="pf-muted">Загрузка...</p>
    <ul v-else class="list">
      <li v-for="row in items" :key="row.id">
        <span class="ico">{{ icon(row.type) }}</span>
        <div class="body">
          <strong>{{ row.title }}</strong>
          <span v-if="row.detail" class="pf-muted detail">{{ row.detail }}</span>
          <span class="time">{{ formatTime(row.created_at) }}</span>
        </div>
        <span v-if="row.progress != null" class="pct">{{ row.progress }}%</span>
      </li>
      <li v-if="!items.length" class="pf-muted">Событий пока нет</li>
    </ul>
  </section>
</template>

<style scoped>
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 420px;
  overflow-y: auto;
}
.list li {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
  align-items: flex-start;
}
.ico {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.body strong {
  font-size: 14px;
}
.detail {
  font-size: 12px;
  word-break: break-word;
}
.time {
  font-size: 11px;
  color: var(--pf-text-muted);
}
.pct {
  font-size: 12px;
  font-weight: 700;
  color: var(--pf-primary);
}
</style>
