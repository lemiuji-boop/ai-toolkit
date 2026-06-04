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
import { EpisodeCard } from "@/components/episode-card";
import { api } from "@/lib/api";
import { useState } from "react";

export default function EpisodesPage() {
  const [status, setStatus] = useState<string>("");
  const { data: episodes } = useQuery({
    queryKey: ["episodes", status],
    queryFn: () => api.listEpisodes(status || undefined),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Выпуски</h1>
      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="mb-4 rounded border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm"
      >
        <option value="">Все статусы</option>
        <option value="draft">draft</option>
        <option value="generating">generating</option>
        <option value="ready_for_review">ready_for_review</option>
        <option value="approved">approved</option>
      </select>
      <div className="grid gap-4 sm:grid-cols-2">
        {episodes?.map((ep) => (
          <EpisodeCard key={ep.id} episode={ep} />
        ))}
      </div>
    </div>
  );
}
