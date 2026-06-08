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
import { useRoute, useRouter } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";
import KsiTree, { type KsiNode } from "@/components/ksi/KsiTree.vue";
import { apiFetch } from "@/api/client";
import { useAuthStore } from "@/stores/auth.store";

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();
const nodes = ref<KsiNode[]>([]);

onMounted(load);

async function load() {
  nodes.value = await apiFetch<KsiNode[]>(`/api/v1/ksi/${route.params.id}`, {}, auth.accessToken);
}

async function build() {
  nodes.value = await apiFetch<KsiNode[]>(
    "/api/v1/ksi/build",
    { method: "POST", body: JSON.stringify({ calculation_id: route.params.id }) },
    auth.accessToken,
  );
}
</script>

<template>
  <AppLayout>
    <div class="page">
      <button type="button" class="pf-btn pf-btn-ghost" @click="router.push(`/calculations/${route.params.id}`)">← Назад</button>
      <div class="pf-card head">
        <h1>КСИ</h1>
        <button type="button" class="pf-btn pf-btn-primary" @click="build">Построить КСИ</button>
      </div>
      <div class="pf-card">
        <KsiTree :nodes="nodes" />
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.page {
  max-width: 900px;
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
}
</style>
