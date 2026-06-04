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

import Link from "next/link";
import type { EpisodeSummary } from "@/lib/types";
import { EpisodeStatusBadge } from "./episode-status-badge";

export function EpisodeCard({ episode }: { episode: EpisodeSummary }) {
  return (
    <Link
      href={`/episodes/${episode.id}`}
      className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition hover:border-amber-500/50"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-zinc-100">
          {episode.title || episode.topic}
        </h3>
        <EpisodeStatusBadge status={episode.status} />
      </div>
      <p className="mt-1 text-sm text-zinc-500">{episode.topic}</p>
      <p className="mt-2 text-xs text-zinc-600">
        {episode.duration_target}с · {episode.platforms.join(", ")}
      </p>
    </Link>
  );
}
