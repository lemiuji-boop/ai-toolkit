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
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const auth = useAuthStore();
const router = useRouter();

const initials = computed(() => {
  const n = auth.user?.full_name || auth.user?.email || "?";
  return n
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
});

function logout() {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <header class="header">
    <div class="search">
      <span class="search-icon">⌕</span>
      <input type="search" placeholder="Поиск проектов и расчётов..." />
    </div>
    <div class="actions">
      <button class="bell" title="Уведомления">🔔</button>
      <div class="user" @click="logout">
        <span class="avatar">{{ initials }}</span>
        <div class="user-text">
          <strong>{{ auth.user?.full_name || "Пользователь" }}</strong>
          <small>{{ auth.user?.email }}</small>
        </div>
        <span class="chev">▾</span>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  gap: 20px;
  position: relative;
  z-index: 1;
}
.search {
  flex: 1;
  max-width: 480px;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 999px;
  padding: 10px 18px;
  box-shadow: var(--pf-shadow);
}
.search input {
  border: none;
  outline: none;
  flex: 1;
  font-size: 14px;
  background: transparent;
}
.search-icon {
  margin-right: 10px;
  color: var(--pf-text-muted);
}
.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
.bell {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  cursor: pointer;
  box-shadow: var(--pf-shadow);
}
.user {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.95);
  padding: 6px 14px 6px 6px;
  border-radius: 999px;
  cursor: pointer;
  box-shadow: var(--pf-shadow);
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}
.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.user-text strong {
  font-size: 13px;
}
.user-text small {
  font-size: 11px;
  color: var(--pf-text-muted);
}
.chev {
  color: var(--pf-text-muted);
  font-size: 12px;
}
</style>
