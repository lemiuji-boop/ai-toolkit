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
defineProps<{
  value: number;
  label?: string;
}>();
</script>

<template>
  <div class="progress-wrap">
    <div v-if="label" class="label">
      <span>{{ label }}</span>
      <span>{{ value }}%</span>
    </div>
    <div class="track">
      <div class="fill" :style="{ width: `${Math.min(100, Math.max(0, value))}%` }">
        <span class="thumb" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.progress-wrap {
  width: 100%;
}
.label {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--pf-text-muted);
  margin-bottom: 6px;
}
.track {
  height: 8px;
  background: #e2e8f0;
  border-radius: 999px;
  overflow: visible;
}
.fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  border-radius: 999px;
  position: relative;
  transition: width 0.4s ease;
  min-width: 8px;
}
.thumb {
  position: absolute;
  right: -4px;
  top: 50%;
  transform: translateY(-50%);
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #fff;
  border: 3px solid #3b82f6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.6);
}
</style>
