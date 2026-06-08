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
      <h1 class="text-h5 mb-4">Профиль</h1>
      <v-card class="pa-4" max-width="480">
        <div>Логин: {{ auth.login }}</div>
        <div>Роль: {{ auth.role }}</div>
      </v-card>
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import AppShell from "../layouts/AppShell.vue";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
</script>
