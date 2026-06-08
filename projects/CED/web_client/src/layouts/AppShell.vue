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
    <v-navigation-drawer permanent width="240" color="sidebar" class="sidebar-drawer">
      <div class="pa-4 text-h6 font-weight-bold sidebar-title">CED Catalog</div>
      <v-list nav density="compact" bg-color="transparent" class="sidebar-list">
        <v-list-item prepend-icon="mdi-folder-table" title="Каталог КД" :to="'/catalog'" />
        <v-list-item prepend-icon="mdi-monitor-dashboard" title="Мониторинг" :to="'/monitoring'" />
        <v-list-item prepend-icon="mdi-cog" title="Настройки" :to="'/settings'" />
        <v-list-item prepend-icon="mdi-account" title="Профиль" :to="'/profile'" />
        <v-divider class="my-2" />
        <v-list-item
          v-if="auth.role === 'admin' || auth.role === 'moderator'"
          prepend-icon="mdi-account-group"
          title="Пользователи"
          :to="'/admin/users'"
        />
      </v-list>
    </v-navigation-drawer>

    <v-app-bar flat border color="surface">
      <v-select
        v-model="project"
        :items="projects"
        label="Проект"
        density="compact"
        hide-details
        style="max-width: 220px"
        class="ml-2"
      />
      <v-spacer />
      <v-chip :color="aiChipColor" variant="flat" size="small" class="mr-2">ИИ: {{ aiStatusLabel }}</v-chip>
      <v-menu>
        <template #activator="{ props }">
          <v-btn v-bind="props" icon variant="text">
            <v-badge v-if="notifications.unreadCount" :content="notifications.unreadCount" color="error">
              <v-icon>mdi-bell-outline</v-icon>
            </v-badge>
            <v-icon v-else>mdi-bell-outline</v-icon>
          </v-btn>
        </template>
        <v-list max-width="420">
          <v-list-item v-if="!notifications.items.length" title="Нет сообщений" />
          <v-list-item
            v-for="m in notifications.items"
            :key="m.id"
            :title="m.title"
            :subtitle="m.body"
            @click="showMessage(m)"
          />
        </v-list>
      </v-menu>
      <v-menu>
        <template #activator="{ props }">
          <v-btn v-bind="props" variant="text" append-icon="mdi-chevron-down">
            {{ auth.login || "Гость" }}
          </v-btn>
        </template>
        <v-list>
          <v-list-item title="Выйти" @click="logout" />
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-main>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import { useNotificationsStore, type SystemMessage } from "../store/notifications";
import { apiClient } from "../api/client";

const auth = useAuthStore();
const notifications = useNotificationsStore();
const router = useRouter();
const project = ref("Основной проект");
const projects = ["Основной проект", "Опытный образец"];
const aiStatusLabel = ref("Активен");
const aiChipColor = ref("success");

let heartbeatTimer: ReturnType<typeof setInterval> | null = null;

const showMessage = (m: SystemMessage): void => {
  alert(`${m.title}\n\n${m.body}`);
};

const logout = async (): Promise<void> => {
  auth.clear();
  await router.push("/login");
};

onMounted(() => {
  void notifications.fetch();
  heartbeatTimer = setInterval(() => {
    void apiClient.post("/auth/heartbeat").catch(() => undefined);
    void notifications.fetch();
  }, 60000);
});
onUnmounted(() => {
  if (heartbeatTimer) clearInterval(heartbeatTimer);
});
</script>

<style scoped>
.sidebar-title {
  color: rgb(var(--v-theme-on-sidebar));
}
</style>
