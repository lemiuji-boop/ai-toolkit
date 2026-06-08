// Copyright 2026 Rinat Ishmaev
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth.store";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: () => import("@/pages/LoginPage.vue"), meta: { public: true } },
    { path: "/", name: "dashboard", component: () => import("@/pages/DashboardPage.vue") },
    { path: "/projects", name: "projects", component: () => import("@/pages/ProjectPage.vue") },
    { path: "/monitoring", name: "monitoring", component: () => import("@/pages/MonitoringPage.vue") },
    { path: "/calculations/:id", name: "calculation", component: () => import("@/pages/CalculationWorkspacePage.vue") },
    { path: "/calculations/:id/review", name: "review", component: () => import("@/pages/ReviewPage.vue") },
    { path: "/calculations/:id/ksi", name: "ksi", component: () => import("@/pages/KsiPage.vue") },
    { path: "/calculations/:id/materials", name: "materials", component: () => import("@/pages/MaterialsPage.vue") },
    { path: "/calculations/:id/excel", name: "excel", component: () => import("@/pages/ExcelEditorPage.vue") },
    { path: "/calculations/:id/report", name: "report", component: () => import("@/pages/ReportPage.vue") },
    { path: "/settings", name: "settings", component: () => import("@/pages/SettingsPage.vue") },
    { path: "/admin", name: "admin", component: () => import("@/pages/AdminPage.vue") },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (auth.isAuthenticated && !auth.user && !to.meta.public) {
    try {
      await auth.fetchMe();
    } catch {
      auth.logout();
      return { name: "login" };
    }
  }
  return true;
});

export default router;
