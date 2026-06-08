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
import { useRouter } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import { useProjectStore } from "@/stores/project.store";
import { useAuthStore } from "@/stores/auth.store";
import { createCalculation } from "@/api/projects.api";

const store = useProjectStore();
const auth = useAuthStore();
const router = useRouter();
const newName = ref("");
const newDesc = ref("");

onMounted(() => store.load());

async function createProject() {
  if (!newName.value.trim()) return;
  await store.add(newName.value, newDesc.value);
  newName.value = "";
  newDesc.value = "";
  await store.load();
}

async function newCalculation(projectId: string) {
  const calc = await createCalculation(auth.accessToken!, projectId, "Новый расчёт");
  await router.push(`/calculations/${calc.id}`);
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <div class="hero pf-card">
        <h1 class="pf-section-title">Проекты</h1>
        <form class="create" @submit.prevent="createProject">
          <input v-model="newName" placeholder="Название проекта" required />
          <input v-model="newDesc" placeholder="Описание" />
          <button type="submit" class="pf-btn pf-btn-primary">Создать</button>
        </form>
      </div>
      <div class="list">
        <article v-for="p in store.projects" :key="p.id" class="pf-card row">
          <div>
            <h3>{{ p.name }}</h3>
            <p class="pf-muted">{{ p.description || "Без описания" }}</p>
          </div>
          <button type="button" class="pf-btn pf-btn-primary" @click="newCalculation(p.id)">+ Расчёт</button>
        </article>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 800px;
}
.hero {
  margin-bottom: 20px;
}
.create {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.create input {
  flex: 1;
  min-width: 140px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.row h3 {
  margin: 0 0 4px;
}
</style>
