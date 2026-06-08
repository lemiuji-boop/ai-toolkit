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
import AppLayout from "@/components/layout/AppLayout.vue";
import { useSyncStore } from "@/stores/sync.store";

const sync = useSyncStore();
const serverUrl = ref("");

onMounted(() => {
  serverUrl.value = sync.serverUrl;
});

function save() {
  sync.setServerUrl(serverUrl.value);
}
</script>

<template>
  <AppLayout>
    <div class="page pf-card">
      <h1 class="pf-section-title">Настройки</h1>
      <p class="pf-muted">URL сервера для desktop-синхронизации (не хранит API-ключи).</p>
      <label>
        Адрес API
        <input v-model="serverUrl" type="url" placeholder="http://127.0.0.1:8001" />
      </label>
      <button type="button" class="pf-btn pf-btn-primary" @click="save">Сохранить</button>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 480px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
input {
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
</style>
