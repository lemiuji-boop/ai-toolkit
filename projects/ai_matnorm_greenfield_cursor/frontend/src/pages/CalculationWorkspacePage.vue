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
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import FileManager from "@/components/files/FileManager.vue";
import ActivityHistory from "@/components/activity/ActivityHistory.vue";
import JobMonitor from "@/components/jobs/JobMonitor.vue";
import ProgressBar from "@/components/ui/ProgressBar.vue";
import {
  fetchActivity,
  fetchCalculationFiles,
  fetchOverview,
  type ActivityItem,
} from "@/api/activity.api";
import { startDocumentJob, jobControl } from "@/api/jobs.api";
import { uploadFiles, fileDownloadUrl } from "@/api/files.api";
import { getCalculation } from "@/api/projects.api";
import { useAuthStore } from "@/stores/auth.store";
import { useJobStore } from "@/stores/job.store";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const jobStore = useJobStore();

const calcId = computed(() => route.params.id as string);
const title = ref("Расчёт");
const overview = ref({ files_count: 0, documents_count: 0, last_job_progress: 0, jobs_running: 0 });
const files = ref<{ id: string; name: string; size: string; mime: string; time: string }[]>([]);
const activity = ref<ActivityItem[]>([]);
const uploading = ref(false);
const pipelineStep = ref(0);

const steps = [
  "Загрузка КД",
  "Очередь / OCR",
  "Извлечение фактов",
  "КСИ",
  "Материалы",
  "Excel",
];

const stepProgress = computed(() => {
  const base = overview.value.last_job_progress || jobStore.progress;
  if (pipelineStep.value === 0) return Math.min(base, 15);
  return Math.min(100, base + pipelineStep.value * 12);
});

async function refresh() {
  const id = calcId.value;
  const c = await getCalculation(auth.accessToken!, id);
  title.value = c.title;
  overview.value = await fetchOverview(auth.accessToken!, id);
  const fl = await fetchCalculationFiles(auth.accessToken!, id);
  files.value = fl.map((f) => ({
    id: f.id,
    name: f.original_name,
    size: `${(f.size_bytes / 1024).toFixed(1)} KB`,
    mime: f.mime_type,
    time: new Date(f.created_at).toLocaleString("ru-RU"),
  }));
  activity.value = await fetchActivity(auth.accessToken!, id);
  pipelineStep.value = overview.value.documents_count > 0 ? 2 : overview.value.files_count > 0 ? 1 : 0;
}

async function onUpload(fileList: FileList) {
  uploading.value = true;
  try {
    const uploaded = await uploadFiles(auth.accessToken!, calcId.value, fileList);
    await refresh();
    const job = await startDocumentJob(
      auth.accessToken!,
      calcId.value,
      uploaded.map((x) => x.id),
    );
    jobStore.subscribe(job.id);
    pipelineStep.value = 1;
    pollTimer = window.setInterval(() => refresh(), 3000);
  } finally {
    uploading.value = false;
  }
}

let pollTimer: number | undefined;

onMounted(async () => {
  await refresh();
});

onUnmounted(() => {
  jobStore.disconnect();
  if (pollTimer) clearInterval(pollTimer);
});

watch(
  () => jobStore.documentIds.length,
  (n) => {
    if (n > 0) {
      pipelineStep.value = 2;
      refresh();
    }
  },
);

watch(
  () => jobStore.status,
  (s) => {
    if (s === "completed") {
      pipelineStep.value = 2;
      refresh();
    }
  },
);

function downloadFile(id: string) {
  window.open(fileDownloadUrl(id), "_blank");
}

async function controlJob(action: "pause" | "resume" | "cancel") {
  if (!jobStore.jobId) return;
  await jobControl(auth.accessToken!, jobStore.jobId, action);
  jobStore.status = action === "pause" ? "paused" : action === "cancel" ? "cancelled" : "running";
}

function go(sub: string) {
  router.push(`/calculations/${calcId.value}/${sub}`);
}
</script>

<template>
  <AppLayout>
    <div class="workspace">
      <div class="top pf-card">
        <div>
          <h1>{{ title }}</h1>
          <p class="pf-muted">Полный цикл: КД → факты → КСИ → материалы → Excel</p>
        </div>
        <div class="steps-nav">
          <button type="button" class="pf-btn pf-btn-ghost" @click="go('review')">Факты</button>
          <button type="button" class="pf-btn pf-btn-ghost" @click="go('ksi')">КСИ</button>
          <button type="button" class="pf-btn pf-btn-ghost" @click="go('materials')">Материалы</button>
          <button type="button" class="pf-btn pf-btn-ghost" @click="go('report')">Отчёт</button>
          <button type="button" class="pf-btn pf-btn-primary" @click="go('excel')">Excel</button>
        </div>
      </div>

      <div class="pipeline pf-card">
        <h2 class="pf-section-title">Этапы обработки</h2>
        <ProgressBar :value="stepProgress" label="Общий прогресс пайплайна" />
        <div class="steps">
          <div
            v-for="(s, i) in steps"
            :key="s"
            class="step"
            :class="{ done: i < pipelineStep, active: i === pipelineStep }"
          >
            <span class="num">{{ i + 1 }}</span>
            {{ s }}
          </div>
        </div>
      </div>

      <div class="cols">
        <div class="main-col">
          <FileManager
            :files="files"
            :calculation-id="calcId"
            :uploading="uploading"
            @upload="onUpload"
            @download="downloadFile"
          />
          <JobMonitor
            :progress="jobStore.progress || overview.last_job_progress"
            :status="jobStore.status"
            :logs="jobStore.logs"
            :active="!!jobStore.jobId"
            @pause="controlJob('pause')"
            @resume="controlJob('resume')"
            @cancel="controlJob('cancel')"
          />
        </div>
        <ActivityHistory :items="activity" />
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.workspace {
  max-width: 1280px;
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  gap: 16px;
  flex-wrap: wrap;
}
.top h1 {
  margin: 0 0 6px;
}
.steps-nav {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.pipeline {
  margin-bottom: 20px;
}
.steps {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}
.step {
  padding: 8px 14px;
  border-radius: 999px;
  background: #f1f5f9;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.step.done {
  background: #dcfce7;
  color: #15803d;
}
.step.active {
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 600;
}
.num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}
.cols {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;
  align-items: start;
}
@media (max-width: 960px) {
  .cols {
    grid-template-columns: 1fr;
  }
}
.main-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
