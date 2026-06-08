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
import { applyCedTheme } from "../themes/applyTheme";
import { getPreset, THEME_PRESETS } from "../themes/presets";

export const useThemeStore = defineStore("theme", {
  state: () => ({
    themeId: localStorage.getItem("theme_id") || "ocean",
    darkMode: localStorage.getItem("dark_mode") === "true",
  }),
  getters: {
    presets: () => THEME_PRESETS,
    textureClass: (state) => getPreset(state.themeId).texture,
  },
  actions: {
    applyLocal() {
      applyCedTheme(this.themeId, this.darkMode);
    },
    setTheme(id: string) {
      this.themeId = id;
      localStorage.setItem("theme_id", id);
      this.applyLocal();
    },
    setDarkMode(value: boolean) {
      this.darkMode = value;
      localStorage.setItem("dark_mode", String(value));
      this.applyLocal();
    },
    async syncFromServer() {
      const token = localStorage.getItem("access_token");
      if (!token) {
        this.applyLocal();
        return;
      }
      try {
        const { apiClient } = await import("../api/client");
        const { data } = await apiClient.get("/settings/preferences");
        this.themeId = data.theme_id || this.themeId;
        this.darkMode = Boolean(data.dark_mode);
        localStorage.setItem("theme_id", this.themeId);
        localStorage.setItem("dark_mode", String(this.darkMode));
      } catch {
        /* оставляем локальные настройки */
      }
      this.applyLocal();
    },
    async saveToServer() {
      const token = localStorage.getItem("access_token");
      if (!token) return;
      const { apiClient } = await import("../api/client");
      await apiClient.put("/settings/preferences", {
        theme_id: this.themeId,
        dark_mode: this.darkMode,
      });
    },
  },
});
