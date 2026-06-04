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

"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function CharactersPage() {
  const { data: characters } = useQuery({
    queryKey: ["characters"],
    queryFn: () => api.listCharacters(),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Персонажи</h1>
      <div className="space-y-4">
        {characters?.map((c) => (
          <div
            key={c.id}
            className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4"
          >
            <h2 className="font-medium">
              {c.name} <span className="text-zinc-500">({c.external_id})</span>
            </h2>
            <p className="text-sm text-zinc-500">{c.role}</p>
            <pre className="mt-2 overflow-auto text-xs text-zinc-400">
              {JSON.stringify(c.bible, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
}
