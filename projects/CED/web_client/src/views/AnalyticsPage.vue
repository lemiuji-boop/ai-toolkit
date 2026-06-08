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

<template>
  <AppShell>
    <v-container class="pa-6">
      <h1 class="text-h5 mb-4">Аналитика ИИ</h1>
      <v-row>
        <v-col cols="12" md="4"><v-card class="pa-4"><div class="text-h4">{{ stats.total }}</div><div>Всего КД</div></v-card></v-col>
        <v-col cols="12" md="4"><v-card class="pa-4"><div class="text-h4">{{ stats.review }}</div><div>На проверке</div></v-card></v-col>
        <v-col cols="12" md="4"><v-card class="pa-4"><div class="text-h4">{{ stats.pendingInbox }}</div><div>INBOX pending</div></v-card></v-col>
      </v-row>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";

const stats = ref({ total: 0, review: 0, pendingInbox: 0 });

onMounted(async () => {
  const catalog = await apiClient.get("/catalog", { params: { size: 1 } });
  const review = await apiClient.get("/catalog", { params: { status: "needs_review", size: 1 } });
  const inbox = await apiClient.get("/inbox/pending");
  stats.value = {
    total: catalog.data.total_count,
    review: review.data.total_count,
    pendingInbox: inbox.data.length,
  };
});
</script>
