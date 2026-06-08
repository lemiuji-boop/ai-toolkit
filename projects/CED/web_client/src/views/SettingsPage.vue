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
      <h1 class="text-h5 mb-4">Настройки</h1>
      <v-tabs v-model="tab" class="mb-4">
        <v-tab value="connection">Подключение</v-tab>
        <v-tab value="catalog">Каталог и INBOX</v-tab>
        <v-tab value="upload">Пакетная загрузка</v-tab>
        <v-tab value="appearance">Оформление</v-tab>
        <v-tab v-if="isAdmin" value="providers">ИИ-провайдеры</v-tab>
      </v-tabs>

      <v-window v-model="tab">
        <v-window-item value="connection">
          <v-card class="pa-4 mb-4">
            <v-text-field v-model="serverUrl" label="Адрес API" hint="Веб: /api через nginx. Desktop: http://хост/api" persistent-hint />
            <v-text-field
              v-model="catalogRoot"
              label="Корень каталога (UNC) — подсказка для клиента"
              hint="Серверный путь: {{ serverCatalogRoot }}"
              persistent-hint
            />
            <v-alert type="info" variant="tonal" class="mt-4">{{ help.catalog_root_text }}</v-alert>
            <v-alert type="info" variant="tonal" class="mt-2">{{ help.api_text }}</v-alert>
            <v-btn color="primary" class="mt-4" @click="saveConnection">Сохранить</v-btn>
          </v-card>
        </v-window-item>

        <v-window-item value="catalog">
          <v-card class="pa-4">
            <h3 class="text-subtitle-1 mb-2">{{ help.inbox_title }}</h3>
            <p class="text-body-2 mb-4">{{ help.inbox_text }}</p>
            <v-chip class="mr-2">Режим хранилища: {{ storageMode }}</v-chip>
            <v-chip>Папка INBOX: {{ inboxSubdir }}</v-chip>
            <v-btn v-if="canModerate" class="mt-4" color="primary" :to="'/admin/inbox'">Открыть разбор INBOX</v-btn>
          </v-card>
        </v-window-item>

        <v-window-item value="upload">
          <v-card class="pa-4">
            <p class="text-body-2 mb-4">Выберите несколько PDF — обозначение берётся из имени файла.</p>
            <v-file-input v-model="batchFiles" label="Файлы КД" multiple accept=".pdf" show-size />
            <v-progress-linear v-if="uploading" indeterminate class="my-3" />
            <v-btn color="primary" :loading="uploading" :disabled="!batchFiles?.length" @click="uploadBatch">
              Загрузить пакет
            </v-btn>
            <v-list v-if="batchResults.length" class="mt-4">
              <v-list-item v-for="r in batchResults" :key="r.file">
                <v-list-item-title>{{ r.file }}</v-list-item-title>
                <v-list-item-subtitle>{{ r.status }} {{ r.error || "" }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card>
        </v-window-item>

        <v-window-item value="appearance">
          <v-card class="pa-4">
            <v-switch v-model="darkMode" label="Тёмный режим" @update:model-value="onDarkChange" />
            <v-row class="mt-2">
              <v-col v-for="t in themeStore.presets" :key="t.id" cols="6" md="4" lg="3">
                <v-card
                  :variant="themeStore.themeId === t.id ? 'outlined' : 'flat'"
                  :color="themeStore.themeId === t.id ? 'primary' : undefined"
                  class="pa-3 cursor-pointer"
                  @click="pickTheme(t.id)"
                >
                  <div class="text-subtitle-2">{{ t.name }}</div>
                  <div class="d-flex ga-1 mt-2">
                    <div :style="{ width: '24px', height: '24px', borderRadius: '4px', background: t.light.primary }" />
                    <div :style="{ width: '24px', height: '24px', borderRadius: '4px', background: t.dark.primary }" />
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>
        </v-window-item>

        <v-window-item v-if="isAdmin" value="providers">
          <SettingsProvidersSection />
        </v-window-item>
      </v-window>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";
import SettingsProvidersSection from "../components/SettingsProvidersSection.vue";
import { useAuthStore } from "../store/auth";
import { useThemeStore } from "../store/theme";

const auth = useAuthStore();
const themeStore = useThemeStore();
const route = useRoute();
const tab = ref((route.query.tab as string) || "connection");

const serverUrl = ref(localStorage.getItem("server_url") || "/api");
const catalogRoot = ref(localStorage.getItem("catalog_root") || "");
const serverCatalogRoot = ref("");
const storageMode = ref("—");
const inboxSubdir = ref("_INBOX");
const help = ref({ catalog_root_text: "", api_text: "", inbox_title: "", inbox_text: "" });
const darkMode = ref(themeStore.darkMode);
const batchFiles = ref<File[]>([]);
const uploading = ref(false);
const batchResults = ref<Array<{ file: string; status: string; error?: string }>>([]);

const isAdmin = computed(() => auth.role === "admin");
const canModerate = computed(() => auth.role === "admin" || auth.role === "moderator");

const loadHelp = async (): Promise<void> => {
  const [h, p] = await Promise.all([
    apiClient.get("/settings/catalog-help"),
    apiClient.get("/settings/preferences"),
  ]);
  help.value = h.data;
  serverCatalogRoot.value = p.data.server_catalog_root;
  storageMode.value = p.data.storage_mode;
  inboxSubdir.value = p.data.inbox_subdir;
  catalogRoot.value = p.data.catalog_root_hint || catalogRoot.value;
};

const saveConnection = async (): Promise<void> => {
  localStorage.setItem("server_url", serverUrl.value);
  localStorage.setItem("catalog_root", catalogRoot.value);
  await apiClient.put("/settings/preferences", { catalog_root_hint: catalogRoot.value });
};

const pickTheme = async (id: string): Promise<void> => {
  themeStore.setTheme(id);
  darkMode.value = themeStore.darkMode;
  try {
    await themeStore.saveToServer();
  } catch {
    /* локальная тема уже применена */
  }
};

const onDarkChange = async (v: boolean | null): Promise<void> => {
  themeStore.setDarkMode(!!v);
  darkMode.value = themeStore.darkMode;
  try {
    await themeStore.saveToServer();
  } catch {
    /* локально применено */
  }
};

const uploadBatch = async (): Promise<void> => {
  if (!batchFiles.value?.length) return;
  uploading.value = true;
  const body = new FormData();
  batchFiles.value.forEach((f) => body.append("files", f));
  try {
    const { data } = await apiClient.post("/documents/upload-batch", body, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    batchResults.value = data.results;
  } finally {
    uploading.value = false;
  }
};

watch(
  () => route.query.tab,
  (t) => {
    if (typeof t === "string" && t) tab.value = t;
  },
);

onMounted(async () => {
  await loadHelp();
  darkMode.value = themeStore.darkMode;
});
</script>
