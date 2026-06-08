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
  <v-app>
    <v-main class="d-flex align-center justify-center">
      <v-card width="420" class="pa-6">
        <v-card-title class="text-h5 mb-2">Смена пароля</v-card-title>
        <p class="text-body-2 mb-4">Требуется задать новый пароль (минимум 8 символов).</p>
        <v-text-field v-model="current" label="Текущий пароль" type="password" />
        <v-text-field v-model="newPassword" label="Новый пароль" type="password" />
        <v-text-field v-model="confirm" label="Подтверждение" type="password" />
        <v-btn color="primary" block :loading="loading" @click="submit">Сохранить</v-btn>
        <v-alert v-if="error" type="error" class="mt-3" density="compact">{{ error }}</v-alert>
      </v-card>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { apiClient } from "../api/client";
import { useAuthStore } from "../store/auth";

const current = ref("");
const newPassword = ref("");
const confirm = ref("");
const loading = ref(false);
const error = ref("");
const router = useRouter();
const auth = useAuthStore();

const submit = async (): Promise<void> => {
  if (newPassword.value !== confirm.value) {
    error.value = "Пароли не совпадают";
    return;
  }
  if (newPassword.value.length < 8) {
    error.value = "Минимум 8 символов";
    return;
  }
  loading.value = true;
  error.value = "";
  try {
    await apiClient.post("/auth/change-password", {
      current_password: current.value,
      new_password: newPassword.value,
    });
    auth.mustChangePassword = false;
    await auth.fetchMe();
    await router.push("/catalog");
  } catch {
    error.value = "Не удалось сменить пароль";
  } finally {
    loading.value = false;
  }
};
</script>
