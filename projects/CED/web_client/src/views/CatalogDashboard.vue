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
      <h1 class="text-h4 font-weight-bold mb-4">CD &amp; AI Catalog</h1>

      <v-card elevation="1" class="mb-4">
        <v-card-text>
          <v-row dense>
            <v-col cols="12" md="3">
              <v-text-field v-model="filters.doc_number" label="Обозначение" density="compact" hide-details />
            </v-col>
            <v-col cols="12" md="3">
              <v-text-field v-model="filters.name" label="Наименование" density="compact" hide-details />
            </v-col>
            <v-col cols="12" md="2">
              <v-text-field v-model="filters.order_number" label="№ ИИ" density="compact" hide-details />
            </v-col>
            <v-col cols="12" md="2">
              <v-btn color="primary" class="mt-1" @click="load">Найти</v-btn>
              <v-btn variant="outlined" class="mt-1 ml-2" @click="exportExcel">Экспорт</v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card elevation="1">
        <v-data-table :headers="headers" :items="items" item-value="id" hover @click:row="onRowClick">
          <template #item.name="{ item }">
            <div class="d-flex align-center ga-2">
              <v-icon color="red">mdi-file-pdf-box</v-icon>
              <span>{{ item.name }}</span>
            </div>
          </template>
          <template #item.ai_status="{ item }">
            <v-chip :color="statusColor(item.ai_status?.code)" size="small" variant="flat">
              {{ item.ai_status?.label || "—" }}
            </v-chip>
          </template>
          <template #item.updated_at="{ item }">
            {{ formatDate(item.updated_at) }}
          </template>
          <template #item.actions="{ item }">
            <v-btn icon="mdi-pencil-outline" size="small" variant="text" @click.stop="openDoc(item.id)" />
            <v-btn
              v-if="canEdit"
              icon="mdi-delete-outline"
              size="small"
              variant="text"
              color="error"
              @click.stop="removeDoc(item.id)"
            />
          </template>
        </v-data-table>
      </v-card>

      <v-row class="mt-4" dense>
        <v-col cols="12" md="4">
          <v-card elevation="1" class="pa-4">
            <div class="text-subtitle-1 font-weight-bold mb-2">Модуль КД</div>
            <div class="text-body-2 mb-3">{{ selected?.name || "—" }}</div>
            <div class="d-flex flex-wrap ga-2">
              <v-btn variant="outlined" :disabled="!selected" @click="openFile">Открыть файл</v-btn>
              <v-btn variant="outlined" :disabled="!selected" @click="openHistory">История</v-btn>
              <v-btn variant="outlined" :disabled="!selected || aiBusy" @click="runValidate">Нормоконтроль</v-btn>
            </div>
            <v-btn
              v-if="lastPath"
              class="mt-2"
              size="small"
              variant="text"
              @click="copyPath"
            >
              Копировать путь: {{ lastPath }}
            </v-btn>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card elevation="1" class="pa-4">
            <div class="text-subtitle-1 font-weight-bold mb-2">ИИ-чат по каталогу</div>
            <v-textarea v-model="chatInput" rows="2" density="compact" hide-details placeholder="Например: покажи АБВГ.123 или открой папку..." />
            <v-btn block color="primary" class="mt-2" :loading="chatBusy" @click="sendChat">Спросить</v-btn>
            <v-alert class="mt-2" :type="chatAlert" variant="tonal" density="compact">{{ chatReply }}</v-alert>
          </v-card>
        </v-col>
        <v-col cols="12" md="4">
          <v-card elevation="1" class="pa-4">
            <div class="text-subtitle-1 font-weight-bold mb-2">Анализ записи</div>
            <v-alert :type="aiAlertType" variant="tonal" density="compact" class="mb-2">
              {{ aiMessage || selected?.ai_insight || "Выберите строку" }}
            </v-alert>
            <v-btn color="primary" block :disabled="!selected || aiBusy" :loading="aiBusy" @click="runAnalyze">
              Исправить / анализ
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { apiBase, apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";
import { useAuthStore } from "../store/auth";

interface CatalogRow {
  id: number;
  doc_number: string;
  name: string;
  product_number: string | null;
  status: string;
  catalog_path: string | null;
  version_index: string | null;
  updated_at: string | null;
  ai_status?: { label: string; code: string; percent: number };
  ai_insight?: string | null;
}

const auth = useAuthStore();
const router = useRouter();
const items = ref<CatalogRow[]>([]);
const selected = ref<CatalogRow | null>(null);
const filters = reactive({ doc_number: "", name: "", order_number: "" });
const aiBusy = ref(false);
const aiMessage = ref("");
const aiAlertType = ref<"info" | "success" | "warning" | "error">("info");
const chatInput = ref("");
const chatReply = ref("");
const chatBusy = ref(false);
const chatAlert = ref<"info" | "success" | "warning">("info");
const lastPath = ref("");

const canEdit = computed(() => auth.role === "admin" || auth.role === "moderator");

const headers = [
  { title: "Название", key: "name" },
  { title: "Обозначение", key: "doc_number" },
  { title: "Версия", key: "version_index" },
  { title: "Статус обработки", key: "ai_status" },
  { title: "Дата изм.", key: "updated_at" },
  { title: "Действия", key: "actions", sortable: false },
];

/** Зелёный: загружен/обработан; оранжевый: обрабатывается; красный: ошибка */
const statusColor = (code?: string): string => {
  if (code === "processing") return "orange";
  if (code === "error") return "error";
  if (code === "uploaded" || code === "loaded" || code === "done") return "success";
  return "grey";
};

const formatDate = (value: string | null): string => {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("ru-RU");
};

const load = async (): Promise<void> => {
  const response = await apiClient.get("/catalog", { params: filters });
  items.value = response.data.items;
};

const onRowClick = (_: unknown, ctx: { item: CatalogRow }): void => {
  selected.value = ctx.item;
};

const openDoc = async (id: number): Promise<void> => {
  await router.push(`/documents/${id}`);
};

const openFile = (): void => {
  if (!selected.value) return;
  window.open(`${apiBase}/documents/${selected.value.id}/file`, "_blank");
};

const openHistory = async (): Promise<void> => {
  if (!selected.value) return;
  await router.push(`/documents/${selected.value.id}?tab=history`);
};

const removeDoc = async (id: number): Promise<void> => {
  await apiClient.delete(`/documents/${id}`);
  await load();
};

const runAnalyze = async (): Promise<void> => {
  if (!selected.value) return;
  aiBusy.value = true;
  try {
    const response = await apiClient.post(`/documents/${selected.value.id}/analyze`);
    aiMessage.value = response.data?.data?.insight || "Анализ выполнен";
    aiAlertType.value = "success";
    await load();
  } catch {
    aiMessage.value = "Ошибка анализа — уведомление отправлено модератору";
    aiAlertType.value = "error";
  } finally {
    aiBusy.value = false;
  }
};

const runValidate = async (): Promise<void> => {
  if (!selected.value) return;
  aiBusy.value = true;
  try {
    const response = await apiClient.post(`/documents/${selected.value.id}/validate`);
    const valid = response.data?.valid ?? response.data?.is_valid;
    aiMessage.value = valid ? "Нормоконтроль пройден" : JSON.stringify(response.data?.issues || response.data);
    aiAlertType.value = valid ? "success" : "warning";
  } catch {
    aiMessage.value = "Ошибка нормоконтроля";
    aiAlertType.value = "error";
  } finally {
    aiBusy.value = false;
  }
};

const sendChat = async (): Promise<void> => {
  if (!chatInput.value.trim()) return;
  chatBusy.value = true;
  try {
    const { data } = await apiClient.post("/catalog/chat", { message: chatInput.value });
    chatReply.value = data.reply;
    chatAlert.value = "success";
    if (data.filters) {
      Object.assign(filters, data.filters);
      await load();
    }
    if (data.actions?.length) {
      lastPath.value = data.actions[0].path || "";
    }
    if (data.items?.length === 1) {
      selected.value = items.value.find((i) => i.id === data.items[0].id) || selected.value;
    }
  } catch {
    chatReply.value = "Не удалось обработать запрос";
    chatAlert.value = "warning";
  } finally {
    chatBusy.value = false;
  }
};

const copyPath = (): void => {
  if (lastPath.value) void navigator.clipboard.writeText(lastPath.value);
};

const exportExcel = async (): Promise<void> => {
  const response = await apiClient.get("/catalog/export", { params: filters, responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = "catalog_export.xlsx";
  link.click();
};

onMounted(load);
</script>
