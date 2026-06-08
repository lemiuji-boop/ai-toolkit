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
import ProgressBar from "@/components/ui/ProgressBar.vue";
import {
  confirmFact as apiConfirmFact,
  listCalculationDocuments,
  listDocumentFacts,
  patchFact,
  type FactDto,
} from "@/api/calculations.api";
import { useAuthStore } from "@/stores/auth.store";
import { useJobStore } from "@/stores/job.store";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const jobStore = useJobStore();
const facts = ref<FactDto[]>([]);
const documentId = ref("");
const documents = ref<{ id: string; document_type: string }[]>([]);

onMounted(async () => {
  const calcId = route.params.id as string;
  documents.value = await listCalculationDocuments(auth.accessToken!, calcId);
  const q = route.query.document_id as string;
  const fromJob = jobStore.documentIds[0];
  documentId.value = q || fromJob || documents.value[0]?.id || "";
  if (documentId.value) await loadFacts();
});

async function loadFacts() {
  facts.value = await listDocumentFacts(auth.accessToken!, documentId.value);
}

async function saveFact(f: FactDto) {
  await patchFact(auth.accessToken!, f.id, f.value);
}

async function confirmFact(f: FactDto) {
  await apiConfirmFact(auth.accessToken!, f.id);
  f.review_status = "approved";
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <div class="head">
        <button type="button" class="pf-btn pf-btn-ghost" @click="router.push(`/calculations/${route.params.id}`)">
          ← Назад
        </button>
        <h1>Извлечённые факты</h1>
      </div>
      <div class="pf-card toolbar">
        <label>
          Документ
          <select v-model="documentId" @change="loadFacts">
            <option v-for="d in documents" :key="d.id" :value="d.id">
              {{ d.document_type }} ({{ d.id.slice(0, 8) }})
            </option>
          </select>
        </label>
      </div>
      <div class="pf-card">
        <table v-if="facts.length">
          <thead>
            <tr>
              <th>Поле</th>
              <th>Значение</th>
              <th>Уверенность</th>
              <th>Метод</th>
              <th>Источник</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in facts" :key="f.id" :class="{ low: f.confidence < 0.7 }">
              <td>{{ f.field }}</td>
              <td><input v-model="f.value" class="cell-input" /></td>
              <td><ProgressBar :value="Math.round(f.confidence * 100)" /></td>
              <td>{{ f.method }}</td>
              <td class="evidence">
                <span v-if="f.source_page">стр. {{ f.source_page }}</span>
                {{ f.evidence_text || "—" }}
              </td>
              <td>
                <button type="button" class="pf-btn pf-btn-ghost" @click="saveFact(f)">Сохранить</button>
                <button type="button" class="pf-btn pf-btn-ghost" @click="confirmFact(f)">✓</button>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="pf-muted">Нет фактов для выбранного документа</p>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 1100px;
}
.head {
  margin-bottom: 16px;
}
.head h1 {
  margin: 12px 0 0;
}
.toolbar {
  margin-bottom: 16px;
}
select {
  margin-left: 8px;
  padding: 8px;
  border-radius: 8px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border-bottom: 1px solid #f1f5f9;
  padding: 10px;
  text-align: left;
}
.low {
  background: #fffbeb;
}
.cell-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}
.evidence {
  font-size: 12px;
  max-width: 200px;
}
</style>
