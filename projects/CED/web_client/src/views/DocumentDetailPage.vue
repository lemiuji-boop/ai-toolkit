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
      <v-btn variant="text" prepend-icon="mdi-arrow-left" class="mb-4" @click="router.back()">Назад</v-btn>
      <v-row>
        <v-col cols="12" md="5">
          <v-card class="pa-4 mb-4">
            <div class="text-h6">{{ doc?.name }}</div>
            <div class="text-body-2">{{ doc?.doc_number }}</div>
            <v-chip class="mt-2" size="small">{{ doc?.status }}</v-chip>
          </v-card>
          <v-card class="pa-4">
            <div class="text-subtitle-1 mb-2">Связанные ИИ</div>
            <v-list density="compact">
              <v-list-item v-for="co in changeOrders" :key="co.id" :title="co.order_number" />
            </v-list>
          </v-card>
          <v-card v-if="showHistory" class="pa-4 mt-4">
            <div class="text-subtitle-1 mb-2">История правок</div>
            <v-timeline density="compact" side="end">
              <v-timeline-item v-for="rev in history" :key="rev.id" size="small">
                {{ rev.action }} — {{ new Date(rev.timestamp).toLocaleString("ru-RU") }}
              </v-timeline-item>
            </v-timeline>
          </v-card>
        </v-col>
        <v-col cols="12" md="7">
          <v-card class="pa-2" min-height="600">
            <canvas ref="pdfCanvas" style="width: 100%" />
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as pdfjsLib from "pdfjs-dist";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url,
).toString();

const route = useRoute();
const router = useRouter();
const doc = ref<Record<string, unknown> | null>(null);
const changeOrders = ref<Array<{ id: number; order_number: string }>>([]);
const history = ref<Array<{ id: number; action: string; timestamp: string }>>([]);
const pdfCanvas = ref<HTMLCanvasElement | null>(null);
const showHistory = ref(route.query.tab === "history");

onMounted(async () => {
  const id = route.params.id;
  const docRes = await apiClient.get(`/documents/${id}`);
  doc.value = docRes.data;
  const coRes = await apiClient.get(`/documents/${id}/change-orders`);
  changeOrders.value = coRes.data;
  const histRes = await apiClient.get(`/records/document/${id}/history`);
  history.value = histRes.data;
  await renderPdf(Number(id));
});

const renderPdf = async (id: number): Promise<void> => {
  const response = await apiClient.get(`/documents/${id}/file`, { responseType: "arraybuffer" });
  const pdf = await pdfjsLib.getDocument({ data: response.data }).promise;
  const page = await pdf.getPage(1);
  const viewport = page.getViewport({ scale: 1.2 });
  const canvas = pdfCanvas.value;
  if (!canvas) return;
  const context = canvas.getContext("2d");
  if (!context) return;
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  await page.render({ canvasContext: context, viewport }).promise;
};
</script>
