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
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const email = ref("admin@example.com");
// В dev подставляем пароль из .env, чтобы не путать с пустым полем
const password = ref(import.meta.env.DEV ? "admin_change_me" : "");
const showPassword = ref(false);
const error = ref<string | null>(null);
const loading = ref(false);
const auth = useAuthStore();
const router = useRouter();

async function submit() {
  error.value = null;
  loading.value = true;
  try {
    await auth.login(email.value, password.value);
    await router.push("/");
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Ошибка входа";
  } finally {
    loading.value = false;
  }
}

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value;
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg" />
    <form class="login-card" @submit.prevent="submit">
      <div class="logo">М</div>
      <h1>AI-МАТНОРМ</h1>
      <p class="pf-muted">Ассистент технолога</p>
      <label>
        Email
        <input v-model="email" type="email" autocomplete="username" required />
      </label>
      <label>
        Пароль
        <div class="password-field">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            autocomplete="current-password"
            required
          />
          <button
            type="button"
            class="password-toggle"
            :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
            :title="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
            @click="togglePasswordVisibility"
          >
            <svg
              v-if="showPassword"
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path
                d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"
              />
              <path
                d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"
              />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
            <svg
              v-else
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
          </button>
        </div>
      </label>
      <p class="hint pf-muted">
        По умолчанию: <code>admin@example.com</code> / <code>admin_change_me</code>
        (из <code>.env</code>). Если не входит — в backend:
        <code>python -m app.cli seed_admin</code>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" class="pf-btn pf-btn-primary" :disabled="loading">
        {{ loading ? "Вход..." : "Войти" }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.login-bg {
  position: fixed;
  inset: 0;
  background: var(--pf-bg-gradient);
}
.login-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  padding: 32px;
  border-radius: 20px;
  box-shadow: var(--pf-shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.logo {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #60a5fa, #2563eb);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
}
h1 {
  margin: 0;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
}
.password-field {
  position: relative;
  display: flex;
  align-items: center;
}
.password-field input {
  width: 100%;
  padding-right: 44px;
}
.password-field input,
label > input {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}
.password-toggle {
  position: absolute;
  right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
}
.password-toggle:hover {
  color: #2563eb;
  background: #f1f5f9;
}
.hint {
  font-size: 12px;
  line-height: 1.45;
  margin: 0;
}
.hint code {
  font-size: 11px;
  background: #f1f5f9;
  padding: 1px 4px;
  border-radius: 4px;
}
.error {
  color: var(--pf-danger);
  font-size: 14px;
}
</style>
