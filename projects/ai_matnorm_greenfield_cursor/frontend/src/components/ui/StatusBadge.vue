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
  status: string;
}>();

const map: Record<string, string> = {
  pending: "warning",
  running: "info",
  completed: "success",
  failed: "danger",
  paused: "warning",
  cancelled: "muted",
  draft: "muted",
};
</script>

<template>
  <span class="badge" :class="map[status] || 'info'">{{ status }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  text-transform: capitalize;
}
.success {
  background: #dcfce7;
  color: #15803d;
}
.warning {
  background: #fef9c3;
  color: #a16207;
}
.info {
  background: #dbeafe;
  color: #1d4ed8;
}
.danger {
  background: #fee2e2;
  color: #b91c1c;
}
.muted {
  background: #f1f5f9;
  color: #64748b;
}
</style>
