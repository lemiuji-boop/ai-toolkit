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
import { useRoute } from "vue-router";

const route = useRoute();

const items = [
  { to: "/", label: "Панель", icon: "▦" },
  { to: "/projects", label: "Проекты", icon: "▤" },
  { to: "/monitoring", label: "Мониторинг", icon: "◔" },
  { to: "/settings", label: "Настройки", icon: "◇" },
  { to: "/admin", label: "Админ", icon: "⚙" },
];

function isActive(path: string) {
  if (path === "/") return route.path === "/";
  return route.path.startsWith(path);
}
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <span class="logo">М</span>
      <span class="name">AI-МАТНОРМ</span>
    </div>
    <nav>
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="nav-item"
        :class="{ active: isActive(item.to) }"
      >
        <span class="icon">{{ item.icon }}</span>
        {{ item.label }}
      </router-link>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 240px;
  margin: 16px;
  padding: 20px 14px;
  border-radius: 20px;
  background: var(--pf-sidebar-glass);
  backdrop-filter: blur(18px);
  border: 1px solid var(--pf-sidebar-border);
  position: relative;
  z-index: 2;
  flex-shrink: 0;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px 24px;
  color: #fff;
}
.logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #60a5fa, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}
.name {
  font-weight: 700;
  font-size: 15px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.75);
  margin-bottom: 4px;
  font-size: 14px;
  font-weight: 500;
  transition: 0.2s;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}
.nav-item.active {
  background: rgba(37, 99, 235, 0.85);
  color: #fff;
  box-shadow: 0 4px 16px rgba(37, 99, 235, 0.4);
}
.icon {
  font-size: 16px;
  opacity: 0.9;
}
</style>
