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

import { vuetify } from "../plugins/vuetify";
import { getPreset, THEME_PRESETS } from "./presets";

const THEME_LIGHT = "cedLight";
const THEME_DARK = "cedDark";

/** Применяет палитру к Vuetify и обновляет CSS-переменные (с переключением темы для перерисовки). */
export function applyCedTheme(themeId: string, darkMode: boolean): void {
  const preset = getPreset(themeId);
  const palette = darkMode ? { ...preset.dark } : { ...preset.light };
  const themeName = darkMode ? THEME_DARK : THEME_LIGHT;

  const global = vuetify.theme;
  const themeEntry = global.themes.value[themeName];
  if (!themeEntry) return;

  themeEntry.dark = darkMode;
  for (const [key, value] of Object.entries(palette)) {
    themeEntry.colors[key] = value;
  }

  const prev = global.name.value;
  if (prev !== themeName) {
    global.name.value = themeName;
  } else {
    // Vuetify 3: при смене только colors нужен перезапуск темы
    global.name.value = darkMode ? THEME_LIGHT : THEME_DARK;
    requestAnimationFrame(() => {
      global.name.value = themeName;
    });
  }

  const root = document.documentElement;
  root.classList.toggle("ced-dark", darkMode);
  root.dataset.cedTheme = themeId;

  THEME_PRESETS.forEach((p) => root.classList.remove(p.texture));
  root.classList.add(preset.texture);
}
