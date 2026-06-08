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

/** 20 цветовых тем: у каждой свой фон, сайдбар и акцент. */

export interface ThemePreset {
  id: string;
  name: string;
  texture: string;
  light: Record<string, string>;
  dark: Record<string, string>;
}

const makePalette = (
  primary: string,
  secondary: string,
  accent: string,
  lightBg: string,
  darkBg: string,
  lightSurface: string,
  darkSurface: string,
) => ({
  light: {
    primary,
    secondary,
    accent,
    background: lightBg,
    surface: lightSurface,
    sidebar: secondary,
    "on-primary": "#ffffff",
    "on-secondary": "#ffffff",
    "on-background": "#0f172a",
    "on-surface": "#0f172a",
    "on-sidebar": "#f8fafc",
  },
  dark: {
    primary,
    secondary,
    accent,
    background: darkBg,
    surface: darkSurface,
    sidebar: secondary,
    "on-primary": "#ffffff",
    "on-secondary": "#ffffff",
    "on-background": "#f1f5f9",
    "on-surface": "#e2e8f0",
    "on-sidebar": "#f8fafc",
  },
});

export const THEME_PRESETS: ThemePreset[] = [
  { id: "ocean", name: "Океан", texture: "texture-dots", ...makePalette("#0284c7", "#0369a1", "#38bdf8", "#f0f9ff", "#0c1929", "#ffffff", "#1e3a5f") },
  { id: "forest", name: "Лес", texture: "texture-lines", ...makePalette("#15803d", "#166534", "#4ade80", "#f0fdf4", "#052e16", "#ffffff", "#14532d") },
  { id: "slate", name: "Сланец", texture: "texture-grid", ...makePalette("#475569", "#334155", "#94a3b8", "#f8fafc", "#0f172a", "#ffffff", "#1e293b") },
  { id: "sunset", name: "Закат", texture: "texture-waves", ...makePalette("#ea580c", "#c2410c", "#fb923c", "#fff7ed", "#431407", "#ffffff", "#7c2d12") },
  { id: "grape", name: "Виноград", texture: "texture-dots", ...makePalette("#7c3aed", "#6d28d9", "#a78bfa", "#f5f3ff", "#2e1065", "#ffffff", "#4c1d95") },
  { id: "mint", name: "Мята", texture: "texture-lines", ...makePalette("#059669", "#047857", "#34d399", "#ecfdf5", "#022c22", "#ffffff", "#064e3b") },
  { id: "sand", name: "Песок", texture: "texture-paper", ...makePalette("#b45309", "#92400e", "#fbbf24", "#fffbeb", "#451a03", "#ffffff", "#78350f") },
  { id: "rose", name: "Роза", texture: "texture-waves", ...makePalette("#e11d48", "#be123c", "#fb7185", "#fff1f2", "#4c0519", "#ffffff", "#881337") },
  { id: "midnight", name: "Полночь", texture: "texture-grid", ...makePalette("#6366f1", "#312e81", "#818cf8", "#eef2ff", "#0f0a2e", "#ffffff", "#1e1b4b") },
  { id: "steel", name: "Сталь", texture: "texture-metal", ...makePalette("#64748b", "#475569", "#cbd5e1", "#f1f5f9", "#0f172a", "#ffffff", "#334155") },
  { id: "amber", name: "Янтарь", texture: "texture-paper", ...makePalette("#d97706", "#b45309", "#fcd34d", "#fffbeb", "#422006", "#ffffff", "#92400e") },
  { id: "coral", name: "Коралл", texture: "texture-dots", ...makePalette("#f97316", "#ea580c", "#fdba74", "#fff7ed", "#431407", "#ffffff", "#9a3412") },
  { id: "lavender", name: "Лаванда", texture: "texture-waves", ...makePalette("#a855f7", "#9333ea", "#d8b4fe", "#faf5ff", "#3b0764", "#ffffff", "#6b21a8") },
  { id: "olive", name: "Олива", texture: "texture-lines", ...makePalette("#65a30d", "#4d7c0f", "#a3e635", "#f7fee7", "#1a2e05", "#ffffff", "#365314") },
  { id: "arctic", name: "Арктика", texture: "texture-grid", ...makePalette("#0891b2", "#0e7490", "#67e8f9", "#ecfeff", "#083344", "#ffffff", "#155e75") },
  { id: "coffee", name: "Кофе", texture: "texture-paper", ...makePalette("#a16207", "#78350f", "#d6b38a", "#fefce8", "#292524", "#ffffff", "#44403c") },
  { id: "neon", name: "Неон", texture: "texture-neon", ...makePalette("#06b6d4", "#0891b2", "#f0abfc", "#ecfeff", "#0c1222", "#ffffff", "#164e63") },
  { id: "graphite", name: "Графит", texture: "texture-metal", ...makePalette("#6b7280", "#374151", "#9ca3af", "#f3f4f6", "#111827", "#ffffff", "#1f2937") },
  { id: "cinnamon", name: "Корица", texture: "texture-dots", ...makePalette("#e11d48", "#9f1239", "#fda4af", "#fff1f2", "#4c0519", "#ffffff", "#881337") },
  { id: "sky", name: "Небо", texture: "texture-waves", ...makePalette("#2563eb", "#1d4ed8", "#60a5fa", "#eff6ff", "#172554", "#ffffff", "#1e3a8a") },
];

export const getPreset = (id: string): ThemePreset =>
  THEME_PRESETS.find((t) => t.id === id) ?? THEME_PRESETS[0];
