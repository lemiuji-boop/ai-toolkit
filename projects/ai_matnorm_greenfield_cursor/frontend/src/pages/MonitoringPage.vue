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
import ProgressBar from "@/components/ui/ProgressBar.vue";
import { apiFetch } from "@/api/client";
import { useAuthStore } from "@/stores/auth.store";

type JobRow = { id: string; status: string; type: string; progress: number };

type SystemStatus = {
  status: string;
  components: Record<string, string>;
};

const auth = useAuthStore();
const jobs = ref<JobRow[]>([]);
const system = ref<SystemStatus | null>(null);

onMounted(async () => {
  const t = auth.accessToken!;
  try {
    jobs.value = await apiFetch<JobRow[]>("/api/v1/admin/jobs", {}, t);
  } catch {
    jobs.value = [];
  }
  system.value = await apiFetch<SystemStatus>("/api/v1/monitoring/status", {}, t);
});
</script>

<template>
  <AppLayout>
    <div class="page">
      <h1 class="pf-section-title">Мониторинг</h1>
      <section v-if="system" class="pf-card status-card">
        <h2>Состояние системы</h2>
        <ul class="components">
          <li v-for="(st, name) in system.components" :key="name">
            <span>{{ name }}</span>
            <span :class="['badge', st]">{{ st }}</span>
          </li>
        </ul>
      </section>
      <section class="jobs">
        <h2 class="pf-section-title">Задачи</h2>
        <div class="grid">
          <article v-for="j in jobs" :key="j.id" class="pf-card">
            <div class="head">
              <strong>{{ j.type }}</strong>
              <span class="id">{{ j.id.slice(0, 8) }}…</span>
            </div>
            <ProgressBar :value="j.progress" :label="j.status" />
          </article>
          <p v-if="!jobs.length" class="pf-muted">Нет задач в очереди</p>
        </div>
      </section>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 900px;
}
.status-card {
  margin-bottom: 24px;
}
.components {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
}
.components li {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}
.badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  background: #f1f5f9;
}
.badge.ok {
  background: #dcfce7;
  color: #166534;
}
.badge.unavailable,
.badge.no_workers {
  background: #fef3c7;
  color: #92400e;
}
.grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.head {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}
.id {
  font-size: 12px;
  color: var(--pf-text-muted);
}
</style>
