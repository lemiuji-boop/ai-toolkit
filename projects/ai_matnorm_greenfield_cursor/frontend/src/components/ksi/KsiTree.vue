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

export type KsiNode = {
  id: string;
  designation: string;
  name: string;
  level: number;
  quantity_total: number;
  confidence: number;
};

defineProps<{ nodes: KsiNode[] }>();
</script>

<template>
  <ul class="ksi-tree">
    <li
      v-for="n in nodes"
      :key="n.id"
      :style="{ paddingLeft: `${n.level * 20}px` }"
      :class="{ low: n.confidence < 0.7 }"
    >
      <strong>{{ n.designation }}</strong> — {{ n.name }}
      <span class="qty">× {{ n.quantity_total }}</span>
      <ProgressBar :value="Math.round(n.confidence * 100)" />
    </li>
  </ul>
</template>

<style scoped>
.ksi-tree {
  list-style: none;
  padding: 0;
  margin: 0;
}
.ksi-tree li {
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
}
.qty {
  margin-left: 8px;
  color: var(--pf-text-muted);
  font-size: 13px;
}
.low {
  color: #b45309;
}
</style>
