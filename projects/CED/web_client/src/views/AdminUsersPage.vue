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
      <h1 class="text-h5 mb-4">Пользователи</h1>
      <v-row v-if="auth.role === 'admin'" class="mb-4" dense>
        <v-col md="3"><v-text-field v-model="form.login" label="Логин" density="compact" /></v-col>
        <v-col md="3"><v-text-field v-model="form.password" label="Пароль" type="password" density="compact" /></v-col>
        <v-col md="2">
          <v-select v-model="form.role" :items="['admin', 'moderator', 'user']" label="Роль" density="compact" />
        </v-col>
        <v-col md="2"><v-btn color="primary" @click="createUser">Создать</v-btn></v-col>
      </v-row>
      <v-data-table :headers="headers" :items="users" />
    </v-container>
  </AppShell>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { apiClient } from "../api/client";
import AppShell from "../layouts/AppShell.vue";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const users = ref<Array<Record<string, unknown>>>([]);
const form = reactive({ login: "", password: "", role: "user" });
const headers = [
  { title: "Логин", key: "login" },
  { title: "ФИО", key: "full_name" },
  { title: "Роль", key: "role" },
  { title: "Активен", key: "is_active" },
];

const load = async (): Promise<void> => {
  const response = await apiClient.get("/admin/users");
  users.value = response.data;
};

const createUser = async (): Promise<void> => {
  await apiClient.post("/admin/users", form);
  form.login = "";
  form.password = "";
  await load();
};

onMounted(load);
</script>
