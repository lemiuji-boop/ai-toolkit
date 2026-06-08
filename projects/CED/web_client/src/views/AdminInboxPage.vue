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
    <v-container class="pa-6">
      <h1 class="text-h5 mb-4">Разбор INBOX</h1>
      <v-btn color="primary" class="mb-4" @click="processAll">Запустить разбор</v-btn>
      <v-data-table :headers="headers" :items="pending" />
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

const pending = ref<Array<Record<string, unknown>>>([]);
const headers = [
  { title: "Файл", key: "file_path" },
  { title: "Статус", key: "status" },
  { title: "Причина", key: "reason" },
  { title: "Confidence", key: "confidence" },
];

const load = async (): Promise<void> => {
  pending.value = (await apiClient.get("/inbox/pending")).data;
};

const processAll = async (): Promise<void> => {
  await apiClient.post("/inbox/process");
  await load();
};

onMounted(load);
</script>
