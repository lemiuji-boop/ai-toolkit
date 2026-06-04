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

/** Типы API */

export interface EpisodeSummary {
  id: string;
  topic: string;
  title: string | null;
  status: string;
  language: string;
  duration_target: number;
  platforms: string[];
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  episode_id: string;
  asset_type: string;
  url: string;
  storage_key: string;
  meta: Record<string, unknown>;
}

export interface GenerationTask {
  id: string;
  episode_id: string;
  step: string;
  status: string;
  progress: number;
  error: string | null;
}

export interface EpisodeDetail extends EpisodeSummary {
  style: string;
  idea: Record<string, unknown> | null;
  worldbuilding: Record<string, unknown> | null;
  science_check: Record<string, unknown> | null;
  architect: Record<string, unknown> | null;
  script: string | null;
  shotlist: Record<string, unknown>[] | null;
  visual_style: Record<string, unknown> | null;
  platform_packages: Record<string, unknown> | null;
  compliance_report: Record<string, unknown> | null;
  quality_report: Record<string, unknown> | null;
  episode_metadata: Record<string, unknown> | null;
  assets: Asset[];
  generation_tasks: GenerationTask[];
}

export interface Character {
  id: string;
  external_id: string;
  name: string;
  role: string;
  bible: Record<string, unknown>;
}
