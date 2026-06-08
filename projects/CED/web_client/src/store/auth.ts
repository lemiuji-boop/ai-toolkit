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
import { apiClient } from "../api/client";

interface AuthState {
  accessToken: string;
  refreshToken: string;
  login: string;
  role: string;
  mustChangePassword: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    accessToken: localStorage.getItem("access_token") || "",
    refreshToken: localStorage.getItem("refresh_token") || "",
    login: localStorage.getItem("login") || "",
    role: localStorage.getItem("role") || "",
    mustChangePassword: localStorage.getItem("must_change_password") === "true",
  }),
  actions: {
    setTokens(accessToken: string, refreshToken: string): void {
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
    },
    setMustChangePassword(value: boolean): void {
      this.mustChangePassword = value;
      localStorage.setItem("must_change_password", String(value));
    },
    async fetchMe(): Promise<void> {
      const response = await apiClient.get("/auth/me");
      this.login = response.data.login;
      this.role = response.data.role;
      this.setMustChangePassword(Boolean(response.data.must_change_password));
      localStorage.setItem("login", this.login);
      localStorage.setItem("role", this.role);
    },
    clear(): void {
      this.accessToken = "";
      this.refreshToken = "";
      this.login = "";
      this.role = "";
      this.mustChangePassword = false;
      localStorage.clear();
    },
  },
});
