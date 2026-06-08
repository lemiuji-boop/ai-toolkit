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
import { useAuthStore } from "../store/auth";
import CatalogDashboard from "../views/CatalogDashboard.vue";
import LoginPage from "../views/LoginPage.vue";
import DocumentDetailPage from "../views/DocumentDetailPage.vue";
import AdminUsersPage from "../views/AdminUsersPage.vue";
import AdminInboxPage from "../views/AdminInboxPage.vue";
import MonitoringPage from "../views/MonitoringPage.vue";
import SettingsPage from "../views/SettingsPage.vue";
import ProfilePage from "../views/ProfilePage.vue";
import ChangePasswordPage from "../views/ChangePasswordPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", component: LoginPage, meta: { public: true } },
    { path: "/change-password", component: ChangePasswordPage, meta: { changePasswordOnly: true } },
    { path: "/", redirect: "/catalog" },
    { path: "/catalog", component: CatalogDashboard },
    { path: "/documents/:id", component: DocumentDetailPage },
    { path: "/analytics", redirect: "/monitoring" },
    { path: "/monitoring", component: MonitoringPage },
    { path: "/settings", component: SettingsPage },
    { path: "/profile", component: ProfilePage },
    { path: "/admin/users", component: AdminUsersPage },
    { path: "/admin/inbox", component: AdminInboxPage },
    { path: "/admin/providers", redirect: { path: "/settings", query: { tab: "providers" } } },
    { path: "/admin/upload", redirect: { path: "/settings", query: { tab: "upload" } } },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (to.meta.public) return true;
  if (!auth.accessToken) return { path: "/login" };
  if (!auth.role) {
    try {
      await auth.fetchMe();
    } catch {
      auth.clear();
      return { path: "/login" };
    }
  }
  if (auth.mustChangePassword && !to.meta.changePasswordOnly) {
    return { path: "/change-password" };
  }
  if (!auth.mustChangePassword && to.path === "/change-password") {
    return { path: "/catalog" };
  }
  return true;
});
