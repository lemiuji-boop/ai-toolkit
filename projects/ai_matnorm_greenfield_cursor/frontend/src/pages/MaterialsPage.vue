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

type Item = {
  material_name: string;
  net_qty: number;
  gross_qty: number;
  unit: string;
  formula: string;
  kim: number | null;
  requires_review: boolean;
};

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const items = ref<Item[]>([]);

onMounted(load);

async function load() {
  items.value = await apiFetch<Item[]>(`/api/v1/materials/results/${route.params.id}`, {}, auth.accessToken);
}

async function calculate() {
  items.value = await apiFetch<Item[]>(
    "/api/v1/materials/calculate",
    { method: "POST", body: JSON.stringify({ calculation_id: route.params.id }) },
    auth.accessToken,
  );
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <button type="button" class="pf-btn pf-btn-ghost" @click="router.push(`/calculations/${route.params.id}`)">← Назад</button>
      <div class="pf-card head">
        <h1>Материалы</h1>
        <button type="button" class="pf-btn pf-btn-primary" @click="calculate">Рассчитать</button>
      </div>
      <div class="pf-card">
        <table>
          <thead>
            <tr>
              <th>Материал</th>
              <th>Нетто</th>
              <th>Брутто</th>
              <th>КИМ</th>
              <th>Формула</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(i, idx) in items" :key="idx" :class="{ review: i.requires_review }">
              <td>{{ i.material_name }}</td>
              <td>{{ i.net_qty }}</td>
              <td>{{ i.gross_qty }}</td>
              <td>{{ i.kim }}</td>
              <td><code>{{ i.formula }}</code></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 1000px;
}
.head {
  display: flex;
  justify-content: space-between;
  margin: 16px 0;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border-bottom: 1px solid #f1f5f9;
  padding: 10px;
}
.review {
  background: #fffbeb;
}
</style>
