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
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import { apiFetch } from "@/api/client";
import { useAuthStore } from "@/stores/auth.store";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const downloadUrl = ref<string | null>(null);
const draftKey = computed(() => `excel_draft_${route.params.id}`);

const rows = ref<string[][]>([
  ["Обозначение", "Материал", "Нетто", "Брутто", "Ед."],
]);

function saveDraft() {
  localStorage.setItem(draftKey.value, JSON.stringify(rows.value));
}

function loadDraft() {
  const raw = localStorage.getItem(draftKey.value);
  if (raw) {
    try {
      rows.value = JSON.parse(raw) as string[][];
    } catch {
      /* ignore */
    }
  }
}

onMounted(async () => {
  type Item = { material_name: string; net_qty: number; gross_qty: number; unit: string };
  const items = await apiFetch<Item[]>(
    `/api/v1/materials/results/${route.params.id}`,
    {},
    auth.accessToken,
  );
  const fromApi = [
    ["Обозначение", "Материал", "Нетто", "Брутто", "Ед."],
    ...items.map((i) => ["", i.material_name, String(i.net_qty), String(i.gross_qty), i.unit]),
  ];
  if (localStorage.getItem(draftKey.value)) {
    loadDraft();
  } else {
    rows.value = fromApi;
  }
});

async function exportExcel() {
  const res = await apiFetch<{ id: string; download_url: string }>(
    "/api/v1/exports/excel",
    { method: "POST", body: JSON.stringify({ calculation_id: route.params.id }) },
    auth.accessToken,
  );
  downloadUrl.value = res.download_url;
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <button type="button" class="pf-btn pf-btn-ghost" @click="router.push(`/calculations/${route.params.id}`)">← Назад</button>
      <div class="pf-card">
        <h1>Excel-ведомость</h1>
        <div class="grid">
          <div v-for="(row, ri) in rows" :key="ri" class="row">
            <input v-for="(_, ci) in row" :key="ci" v-model="rows[ri][ci]" class="cell" />
          </div>
        </div>
        <div class="actions">
          <button type="button" class="pf-btn pf-btn-ghost" @click="saveDraft">Сохранить черновик</button>
          <button type="button" class="pf-btn pf-btn-primary" @click="exportExcel">Экспорт</button>
        </div>
        <a v-if="downloadUrl" :href="downloadUrl" target="_blank" class="link">Скачать Excel</a>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 900px;
}
.grid {
  margin: 16px 0;
}
.row {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}
.cell {
  width: 120px;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}
.actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
.link {
  display: inline-block;
  margin-left: 12px;
  color: var(--pf-primary);
}
</style>
