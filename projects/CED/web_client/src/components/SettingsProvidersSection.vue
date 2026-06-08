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
  <v-card class="pa-4">
    <v-switch v-model="settings.allow_external_providers" label="Разрешить внешних провайдеров" @change="saveSettings" />
    <v-data-table :headers="headers" :items="providers" density="compact" class="mb-4">
      <template #item.actions="{ item }">
        <v-btn size="x-small" variant="text" @click="edit(item)">Изм.</v-btn>
        <v-btn size="x-small" variant="text" color="error" @click="remove(item.id)">Уд.</v-btn>
      </template>
    </v-data-table>
    <v-text-field v-model="form.name" label="Имя" density="compact" />
    <v-select v-model="form.provider_type" :items="['local', 'external']" label="Тип" density="compact" />
    <v-text-field v-model="form.base_url" label="URL" density="compact" />
    <v-text-field v-model="form.model_name" label="Модель" density="compact" />
    <v-btn color="primary" size="small" @click="save">Сохранить провайдер</v-btn>
  </v-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { apiClient } from "../api/client";

const providers = ref<Array<Record<string, unknown>>>([]);
const settings = ref({ allow_external_providers: false });
const editId = ref<number | null>(null);
const form = reactive({ name: "", provider_type: "local", base_url: "", model_name: "", is_active: true });
const headers = [
  { title: "Имя", key: "name" },
  { title: "Тип", key: "provider_type" },
  { title: "URL", key: "base_url" },
  { title: "Действия", key: "actions" },
];

const load = async (): Promise<void> => {
  providers.value = (await apiClient.get("/admin/ai-providers")).data;
  settings.value = (await apiClient.get("/admin/ai-providers/settings")).data;
};

const saveSettings = async (): Promise<void> => {
  await apiClient.put("/admin/ai-providers/settings", settings.value);
};

const edit = (row: Record<string, unknown>): void => {
  editId.value = row.id as number;
  form.name = row.name as string;
  form.provider_type = row.provider_type as string;
  form.base_url = row.base_url as string;
  form.model_name = (row.model_name as string) || "";
};

const save = async (): Promise<void> => {
  if (editId.value) await apiClient.put(`/admin/ai-providers/${editId.value}`, form);
  else await apiClient.post("/admin/ai-providers", form);
  editId.value = null;
  await load();
};

const remove = async (id: number): Promise<void> => {
  await apiClient.delete(`/admin/ai-providers/${id}`);
  await load();
};

onMounted(load);
</script>
