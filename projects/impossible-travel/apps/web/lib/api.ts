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

/** HTTP-клиент API */

import type { Character, EpisodeDetail, EpisodeSummary, GenerationTask } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listEpisodes: (status?: string) =>
    request<EpisodeSummary[]>(status ? `/episodes?status=${status}` : "/episodes"),

  getEpisode: (id: string) => request<EpisodeDetail>(`/episodes/${id}`),

  createEpisode: (body: {
    topic: string;
    duration_target: number;
    platforms: string[];
    language: string;
    style?: string;
  }) =>
    request<EpisodeSummary>("/episodes", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  generateEpisode: (id: string) =>
    request<{ celery_task_id: string; message: string }>(`/episodes/${id}/generate`, {
      method: "POST",
    }),

  approveEpisode: (id: string) =>
    request<{ status: string }>(`/episodes/${id}/approve`, { method: "POST" }),

  listCharacters: () => request<Character[]>("/characters"),

  listTasks: (episodeId: string) =>
    request<GenerationTask[]>(`/tasks?episode_id=${episodeId}`),

  getSettings: () =>
    request<{ mock_generation: boolean; app_env: string }>("/settings"),
};
