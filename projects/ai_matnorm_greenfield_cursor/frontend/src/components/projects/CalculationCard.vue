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
import ProgressBar from "@/components/ui/ProgressBar.vue";
import StatusBadge from "@/components/ui/StatusBadge.vue";

export type CalcCard = {
  id: string;
  title: string;
  designation: string;
  progress: number;
  status: string;
  filesCount: number;
  documentsCount: number;
  deadline?: string;
};

defineProps<{
  calc: CalcCard;
}>();

defineEmits<{
  view: [id: string];
  edit: [id: string];
}>();
</script>

<template>
  <article class="card">
    <div class="head">
      <h3>{{ calc.title }}</h3>
      <button class="menu" type="button">⋯</button>
    </div>
    <p v-if="calc.designation" class="des">{{ calc.designation }}</p>
    <ProgressBar :value="calc.progress" />
    <div class="meta">
      <StatusBadge :status="calc.status" />
      <span class="pf-muted">{{ calc.filesCount }} файлов · {{ calc.documentsCount }} док.</span>
    </div>
    <div class="foot">
      <button type="button" class="pf-btn pf-btn-ghost" @click="$emit('view', calc.id)">Открыть</button>
      <button type="button" class="pf-btn pf-btn-primary" @click="$emit('edit', calc.id)">Работа</button>
    </div>
  </article>
</template>

<style scoped>
.card {
  background: var(--pf-surface);
  border-radius: var(--pf-radius);
  padding: 20px;
  box-shadow: var(--pf-shadow);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.head h3 {
  margin: 0;
  font-size: 17px;
}
.menu {
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  color: var(--pf-text-muted);
}
.des {
  margin: 0;
  font-size: 13px;
  color: var(--pf-text-muted);
}
.meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.foot {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}
.foot .pf-btn {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
}
</style>
