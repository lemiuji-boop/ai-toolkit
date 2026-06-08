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
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import { apiFetch } from "@/api/client";
import { useAuthStore } from "@/stores/auth.store";

type Report = {
  id: string;
  title: string;
  content: {
    materials_count: number;
    ksi_nodes_count: number;
    items: { material: string; gross_qty: number; unit: string }[];
  };
};

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const report = ref<Report | null>(null);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    report.value = await apiFetch<Report>(
      `/api/v1/reports/calculation/${route.params.id}`,
      {},
      auth.accessToken,
    );
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Сначала выполните расчёт материалов";
  }
});
</script>

<template>
  <AppLayout>
    <div class="page">
      <button type="button" class="pf-btn pf-btn-ghost" @click="router.push(`/calculations/${route.params.id}`)">
        ← Назад
      </button>
      <div v-if="report" class="pf-card">
        <h1>{{ report.title }}</h1>
        <p class="pf-muted">
          Материалов: {{ report.content.materials_count }}, узлов КСИ: {{ report.content.ksi_nodes_count }}
        </p>
        <table v-if="report.content.items?.length">
          <thead>
            <tr>
              <th>Материал</th>
              <th>Брутто</th>
              <th>Ед.</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in report.content.items" :key="i">
              <td>{{ row.material }}</td>
              <td>{{ row.gross_qty }}</td>
              <td>{{ row.unit }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="pf-muted">{{ error }}</p>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 800px;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}
th,
td {
  border-bottom: 1px solid #f1f5f9;
  padding: 8px;
}
</style>
