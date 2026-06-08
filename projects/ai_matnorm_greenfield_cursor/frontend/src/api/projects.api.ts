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

import { apiFetch } from "./client";

export type Project = { id: string; name: string; description: string; owner_id: string; created_at: string };
export type Calculation = {
  id: string;
  project_id: string;
  title: string;
  designation: string;
  created_by_id: string;
  created_at: string;
};

export function listProjects(token: string) {
  return apiFetch<Project[]>("/api/v1/projects", {}, token);
}

export function createProject(token: string, name: string, description: string) {
  return apiFetch<Project>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  }, token);
}

export function createCalculation(token: string, projectId: string, title: string) {
  return apiFetch<Calculation>("/api/v1/calculations", {
    method: "POST",
    body: JSON.stringify({ project_id: projectId, title, designation: "" }),
  }, token);
}

export function getCalculation(token: string, id: string) {
  return apiFetch<Calculation>(`/api/v1/calculations/${id}`, {}, token);
}
