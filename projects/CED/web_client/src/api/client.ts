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

import axios, { type AxiosInstance } from "axios";
import { useAuthStore } from "../store/auth";

/** Docker/nginx: /api; Windows-шлюз (mode lan): http://host:8000 */
export const apiBase =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") || "/api";

export const apiClient: AxiosInstance = axios.create({
  baseURL: apiBase,
});

apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore();
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const auth = useAuthStore();
    if (error.response?.status === 403 && error.response?.data?.detail === "password_change_required") {
      auth.setMustChangePassword(true);
      if (window.location.pathname !== "/change-password") {
        window.location.href = "/change-password";
      }
      return Promise.reject(error);
    }
    if (error.response?.status === 401 && auth.refreshToken) {
      const refresh = await axios.post(`${apiBase}/auth/refresh`, { refresh_token: auth.refreshToken });
      auth.setTokens(refresh.data.access_token, refresh.data.refresh_token);
      error.config.headers.Authorization = `Bearer ${auth.accessToken}`;
      return apiClient.request(error.config);
    }
    return Promise.reject(error);
  },
);
