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
import { apiFetch } from "@/api/client";
import {
  createProvider,
  deleteProvider,
  listProviders,
  listSecurityEvents,
  testProvider,
  type AiProvider,
} from "@/api/admin.api";
import { useAuthStore } from "@/stores/auth.store";

const auth = useAuthStore();
const users = ref<{ email: string; full_name: string }[]>([]);
const tokens = ref<{ requests: number; prompt_tokens: number } | null>(null);
const providers = ref<AiProvider[]>([]);
const events = ref<{ event_type: string; created_at: string }[]>([]);
const testMsg = ref<Record<string, string>>({});

const form = ref({
  name: "",
  provider_type: "ollama",
  base_url: "http://127.0.0.1:11434",
  api_key: "",
  priority: 10,
});

onMounted(async () => {
  const t = auth.accessToken!;
  users.value = await apiFetch("/api/v1/admin/users", {}, t);
  tokens.value = await apiFetch("/api/v1/admin/token-usage", {}, t);
  providers.value = await listProviders(t);
  events.value = await listSecurityEvents(t);
});

async function addProvider() {
  if (!form.value.name.trim()) return;
  const t = auth.accessToken!;
  await createProvider(t, {
    name: form.value.name,
    provider_type: form.value.provider_type,
    base_url: form.value.base_url || undefined,
    api_key: form.value.api_key || undefined,
    priority: form.value.priority,
  });
  form.value.name = "";
  form.value.api_key = "";
  providers.value = await listProviders(t);
}

async function runTest(id: string) {
  const r = await testProvider(auth.accessToken!, id);
  testMsg.value[id] = `${r.status}: ${r.detail}`;
}

async function remove(id: string) {
  await deleteProvider(auth.accessToken!, id);
  providers.value = await listProviders(auth.accessToken!);
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <h1 class="pf-section-title">Админ-панель</h1>
      <div class="grid">
        <section class="pf-card">
          <h2>Пользователи</h2>
          <ul>
            <li v-for="u in users" :key="u.email">{{ u.email }} — {{ u.full_name }}</li>
          </ul>
        </section>
        <section class="pf-card">
          <h2>Расход токенов</h2>
          <p v-if="tokens" class="pf-muted">
            Запросов: {{ tokens.requests }}, prompt: {{ tokens.prompt_tokens }}
          </p>
        </section>
        <section class="pf-card wide">
          <h2>ИИ-провайдеры</h2>
          <form class="provider-form" @submit.prevent="addProvider">
            <input v-model="form.name" placeholder="Имя" required />
            <select v-model="form.provider_type">
              <option value="ollama">Ollama</option>
              <option value="openai_compatible">OpenAI-compatible</option>
              <option value="mock">Mock</option>
            </select>
            <input v-model="form.base_url" placeholder="Base URL" />
            <input v-model="form.api_key" type="password" placeholder="API key (не показывается после сохранения)" />
            <button type="submit" class="pf-btn pf-btn-primary">Добавить</button>
          </form>
          <ul class="prov-list">
            <li v-for="p in providers" :key="p.id">
              <span>{{ p.name }} ({{ p.provider_type }}) — priority {{ p.priority }}</span>
              <button type="button" class="pf-btn pf-btn-ghost" @click="runTest(p.id)">Проверить</button>
              <button type="button" class="pf-btn pf-btn-ghost" @click="remove(p.id)">Удалить</button>
              <span v-if="testMsg[p.id]" class="test-result">{{ testMsg[p.id] }}</span>
            </li>
          </ul>
        </section>
        <section class="pf-card">
          <h2>События безопасности</h2>
          <ul>
            <li v-for="e in events.slice(0, 20)" :key="e.created_at + e.event_type">
              {{ e.event_type }} — {{ e.created_at }}
            </li>
          </ul>
        </section>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 1100px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}
.wide {
  grid-column: 1 / -1;
}
h2 {
  margin: 0 0 12px;
  font-size: 16px;
}
ul {
  padding-left: 18px;
}
.provider-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.provider-form input,
.provider-form select {
  padding: 8px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}
.prov-list li {
  margin-bottom: 8px;
  list-style: none;
  padding-left: 0;
}
.test-result {
  display: block;
  font-size: 12px;
  color: var(--pf-text-muted);
}
</style>
