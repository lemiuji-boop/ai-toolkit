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
import CalculationCard, { type CalcCard } from "@/components/projects/CalculationCard.vue";
import { fetchOverview } from "@/api/activity.api";
import { useAuthStore } from "@/stores/auth.store";
import { useProjectStore } from "@/stores/project.store";
import { apiFetch } from "@/api/client";

const auth = useAuthStore();
const projects = useProjectStore();
const router = useRouter();
const cards = ref<CalcCard[]>([]);
const loading = ref(true);

onMounted(async () => {
  await projects.load();
  const all: CalcCard[] = [];
  for (const p of projects.projects) {
    const calcs = await apiFetch<{ id: string; title: string; designation: string }[]>(
      `/api/v1/projects/${p.id}/calculations`,
      {},
      auth.accessToken!,
    );
    for (const c of calcs) {
      const ov = await fetchOverview(auth.accessToken!, c.id);
      all.push({
        id: c.id,
        title: c.title,
        designation: c.designation,
        progress: ov.last_job_progress || (ov.documents_count ? 60 : 10),
        status: ov.jobs_running ? "running" : ov.jobs_completed ? "completed" : "pending",
        filesCount: ov.files_count,
        documentsCount: ov.documents_count,
      });
    }
  }
  cards.value = all;
  loading.value = false;
});

function openCalc(id: string) {
  router.push(`/calculations/${id}`);
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <div class="hero pf-card">
        <div>
          <h1>Мои расчёты</h1>
          <p class="pf-muted">Мониторинг обработки КД, КСИ и норм материалов</p>
        </div>
        <router-link to="/projects" class="pf-btn pf-btn-primary">+ Новый проект</router-link>
      </div>
      <p v-if="loading" class="pf-muted">Загрузка...</p>
      <div v-else class="grid">
        <CalculationCard
          v-for="c in cards"
          :key="c.id"
          :calc="c"
          @view="openCalc"
          @edit="openCalc"
        />
        <div v-if="!cards.length" class="empty pf-card pf-muted">
          Нет расчётов. Создайте проект и добавьте расчёт.
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 1200px;
}
.hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.hero h1 {
  margin: 0 0 6px;
  font-size: 26px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}
.empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
}
</style>
