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
    <v-main class="d-flex align-center justify-center bg-grey-lighten-4">
      <v-card width="400" class="pa-6">
        <v-card-title class="text-h5 mb-4">Вход в CED Catalog</v-card-title>
        <v-text-field v-model="login" label="Логин" />
        <v-text-field v-model="password" label="Пароль" type="password" />
        <v-btn color="primary" block :loading="loading" @click="onSubmit">Войти</v-btn>
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

const login = ref("admin");
const password = ref("admin");
const loading = ref(false);
const error = ref("");
const router = useRouter();
const auth = useAuthStore();

const onSubmit = async (): Promise<void> => {
  loading.value = true;
  error.value = "";
  try {
    const response = await apiClient.post("/auth/login", { login: login.value, password: password.value });
    auth.setTokens(response.data.access_token, response.data.refresh_token);
    auth.setMustChangePassword(Boolean(response.data.must_change_password));
    await auth.fetchMe();
    if (auth.mustChangePassword) {
      await router.push("/change-password");
    } else {
      await router.push("/catalog");
    }
  } catch (e: unknown) {
    const status = (e as { response?: { status?: number } })?.response?.status;
    error.value = status === 429 ? "Слишком много попыток. Подождите 15 минут." : "Неверный логин или пароль";
  } finally {
    loading.value = false;
  }
};
</script>
