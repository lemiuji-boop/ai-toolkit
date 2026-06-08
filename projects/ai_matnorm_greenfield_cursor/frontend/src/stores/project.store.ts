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
import { ref } from "vue";
import { createProject, listProjects, type Project } from "@/api/projects.api";
import { useAuthStore } from "./auth.store";

export const useProjectStore = defineStore("project", () => {
  const projects = ref<Project[]>([]);
  const loading = ref(false);

  async function load() {
    const auth = useAuthStore();
    if (!auth.accessToken) return;
    loading.value = true;
    try {
      projects.value = await listProjects(auth.accessToken);
    } finally {
      loading.value = false;
    }
  }

  async function add(name: string, description: string) {
    const auth = useAuthStore();
    const p = await createProject(auth.accessToken!, name, description);
    projects.value.unshift(p);
    return p;
  }

  return { projects, loading, load, add };
});
