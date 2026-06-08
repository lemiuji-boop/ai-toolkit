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

import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { apiFetch } from "@/api/client";

type UserMe = {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
  is_superuser: boolean;
};

type TokenResponse = {
  access_token: string;
  refresh_token: string;
};

const ACCESS_KEY = "ai_matnorm_access";
const REFRESH_KEY = "ai_matnorm_refresh";

export const useAuthStore = defineStore("auth", () => {
  const accessToken = ref<string | null>(localStorage.getItem(ACCESS_KEY));
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_KEY));
  const user = ref<UserMe | null>(null);

  const isAuthenticated = computed(() => !!accessToken.value);

  function setTokens(access: string, refresh: string) {
    accessToken.value = access;
    refreshToken.value = refresh;
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  }

  function logout() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  async function login(email: string, password: string) {
    const tokens = await apiFetch<TokenResponse>("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setTokens(tokens.access_token, tokens.refresh_token);
    await fetchMe();
  }

  async function fetchMe() {
    if (!accessToken.value) return;
    user.value = await apiFetch<UserMe>("/api/v1/users/me", {}, accessToken.value);
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    login,
    logout,
    fetchMe,
  };
});
