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
      <h1 class="text-h5 mb-4">ИИ-провайдеры</h1>
      <v-switch v-model="settings.allow_external_providers" label="Разрешить внешних провайдеров" @change="saveSettings" />
      <v-alert type="warning" variant="tonal" class="mb-4">
        Внешние провайдеры отправляют данные за периметр сети. По умолчанию используется только локальный Ollama.
      </v-alert>

      <v-data-table :headers="headers" :items="providers" class="mb-4">
        <template #item.is_active="{ item }">
          <v-chip :color="item.is_active ? 'success' : 'grey'" size="small">{{ item.is_active ? "Да" : "Нет" }}</v-chip>
        </template>
        <template #item.actions="{ item }">
          <v-btn size="small" variant="text" @click="editProvider(item)">Изменить</v-btn>
          <v-btn size="small" variant="text" color="error" @click="removeProvider(item.id)">Удалить</v-btn>
        </template>
      </v-data-table>

      <v-card variant="outlined" class="pa-4">
        <div class="text-subtitle-1 mb-3">{{ editId ? "Редактирование" : "Новый провайдер" }}</div>
        <v-text-field v-model="form.name" label="Имя" />
        <v-select v-model="form.provider_type" :items="['local', 'external']" label="Тип" />
        <v-text-field v-model="form.base_url" label="Base URL" />
        <v-text-field v-model="form.model_name" label="Модель" />
        <v-text-field v-model="form.api_key" label="API Key (опционально)" type="password" />
        <v-switch v-model="form.is_active" label="Активен" />
        <v-btn color="primary" class="mr-2" @click="saveProvider">Сохранить</v-btn>
        <v-btn variant="outlined" @click="resetForm">Сброс</v-btn>
      </v-card>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

interface ProviderRow {
  id: number;
  name: string;
  provider_type: string;
  base_url: string;
  model_name: string | null;
  is_active: boolean;
}

const providers = ref<ProviderRow[]>([]);
const settings = ref({ allow_external_providers: false, active_provider_id: null as number | null });
const editId = ref<number | null>(null);
const form = reactive({
  name: "",
  provider_type: "local",
  base_url: "http://ollama:11434",
  model_name: "llama3",
  api_key: "",
  is_active: true,
});

const headers = [
  { title: "Имя", key: "name" },
  { title: "Тип", key: "provider_type" },
  { title: "URL", key: "base_url" },
  { title: "Модель", key: "model_name" },
  { title: "Активен", key: "is_active" },
  { title: "Действия", key: "actions", sortable: false },
];

const load = async (): Promise<void> => {
  providers.value = (await apiClient.get("/admin/ai-providers")).data;
  settings.value = (await apiClient.get("/admin/ai-providers/settings")).data;
};

const saveSettings = async (): Promise<void> => {
  await apiClient.put("/admin/ai-providers/settings", settings.value);
};

const resetForm = (): void => {
  editId.value = null;
  form.name = "";
  form.provider_type = "local";
  form.base_url = "http://ollama:11434";
  form.model_name = "llama3";
  form.api_key = "";
  form.is_active = true;
};

const editProvider = (row: ProviderRow): void => {
  editId.value = row.id;
  form.name = row.name;
  form.provider_type = row.provider_type;
  form.base_url = row.base_url;
  form.model_name = row.model_name || "";
  form.api_key = "";
  form.is_active = row.is_active;
};

const saveProvider = async (): Promise<void> => {
  const payload = { ...form };
  if (editId.value) {
    await apiClient.put(`/admin/ai-providers/${editId.value}`, payload);
  } else {
    await apiClient.post("/admin/ai-providers", payload);
  }
  resetForm();
  await load();
};

const removeProvider = async (id: number): Promise<void> => {
  await apiClient.delete(`/admin/ai-providers/${id}`);
  await load();
};

onMounted(load);
</script>
