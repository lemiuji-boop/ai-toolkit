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
    <v-container class="pa-6" style="max-width: 720px">
      <h1 class="text-h5 mb-4">Загрузка документа</h1>
      <v-form @submit.prevent="submit">
        <v-text-field v-model="form.doc_number" label="Обозначение" required />
        <v-text-field v-model="form.name" label="Наименование" required />
        <v-select v-model="form.doc_type" :items="docTypes" label="Тип документа" />
        <v-text-field v-model="form.version_index" label="Индекс версии" />
        <v-text-field v-model="form.department" label="Подразделение" />
        <v-file-input v-model="file" label="PDF файл" accept=".pdf" show-size required />
        <v-btn type="submit" color="primary" :loading="loading" class="mt-4">Загрузить</v-btn>
      </v-form>
      <v-alert v-if="message" :type="alertType" class="mt-4">{{ message }}</v-alert>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

const docTypes = ["drawing", "specification", "assembly", "other"];
const form = reactive({
  doc_number: "",
  name: "",
  doc_type: "drawing",
  version_index: "А",
  department: "",
});
const file = ref<File[]>([]);
const loading = ref(false);
const message = ref("");
const alertType = ref<"success" | "error">("success");

const submit = async (): Promise<void> => {
  if (!file.value.length) {
    message.value = "Выберите PDF";
    alertType.value = "error";
    return;
  }
  loading.value = true;
  message.value = "";
  try {
    const body = new FormData();
    body.append("doc_number", form.doc_number);
    body.append("name", form.name);
    body.append("doc_type", form.doc_type);
    body.append("version_index", form.version_index);
    if (form.department) body.append("department", form.department);
    body.append("file", file.value[0]);
    await apiClient.post("/documents/upload", body, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    message.value = "Документ загружен, анализ запущен в фоне";
    alertType.value = "success";
  } catch {
    message.value = "Ошибка загрузки";
    alertType.value = "error";
  } finally {
    loading.value = false;
  }
};
</script>
