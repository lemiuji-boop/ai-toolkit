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

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import { EpisodeStatusBadge } from "@/components/episode-status-badge";
import { api } from "@/lib/api";

const TABS = [
  "Idea",
  "Location",
  "Script",
  "Shotlist",
  "Images",
  "Videos",
  "Audio",
  "Packages",
  "Compliance",
  "Tasks",
] as const;

export default function EpisodeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<(typeof TABS)[number]>("Idea");

  const { data: episode, refetch } = useQuery({
    queryKey: ["episode", id],
    queryFn: () => api.getEpisode(id),
    refetchInterval: (q) =>
      q.state.data?.status === "generating" ? 2000 : false,
  });

  const generate = useMutation({
    mutationFn: () => api.generateEpisode(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["episode", id] });
      refetch();
    },
  });

  const approve = useMutation({
    mutationFn: () => api.approveEpisode(id),
    onSuccess: () => refetch(),
  });

  if (!episode) {
    return <p className="text-zinc-500">Загрузка...</p>;
  }

  const images = episode.assets?.filter((a) => a.asset_type === "image") || [];
  const videos = episode.assets?.filter((a) => a.asset_type === "video") || [];
  const audio = episode.assets?.filter((a) => a.asset_type === "audio") || [];

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            {episode.title || episode.topic}
          </h1>
          <p className="text-zinc-500">{episode.topic}</p>
          <div className="mt-2">
            <EpisodeStatusBadge status={episode.status} />
          </div>
        </div>
        <div className="flex gap-2">
          {["draft", "failed"].includes(episode.status) && (
            <button
              onClick={() => generate.mutate()}
              disabled={generate.isPending}
              className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950"
            >
              {generate.isPending ? "Запуск..." : "Сгенерировать"}
            </button>
          )}
          {episode.status === "generating" && (
            <span className="text-sm text-zinc-400">Генерация...</span>
          )}
          {episode.status === "ready_for_review" && (
            <button
              onClick={() => approve.mutate()}
              disabled={approve.isPending}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white"
            >
              Утвердить
            </button>
          )}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-1 border-b border-zinc-800">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-3 py-2 text-sm ${
              tab === t
                ? "border-b-2 border-amber-500 text-amber-400"
                : "text-zinc-500"
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="rounded-lg border border-zinc-800 bg-zinc-900/30 p-4">
        {tab === "Idea" && (
          <pre className="overflow-auto text-sm text-zinc-300">
            {JSON.stringify(episode.idea, null, 2)}
          </pre>
        )}
        {tab === "Location" && (
          <pre className="overflow-auto text-sm text-zinc-300">
            {JSON.stringify(episode.worldbuilding, null, 2)}
          </pre>
        )}
        {tab === "Script" && (
          <pre className="whitespace-pre-wrap text-sm text-zinc-300">
            {episode.script || "—"}
          </pre>
        )}
        {tab === "Shotlist" && (
          <pre className="overflow-auto text-sm text-zinc-300">
            {JSON.stringify(episode.shotlist, null, 2)}
          </pre>
        )}
        {tab === "Images" && (
          <div className="grid gap-4 sm:grid-cols-2">
            {images.map((a) => (
              <a key={a.id} href={a.url} target="_blank" rel="noreferrer">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={a.url} alt="" className="rounded border border-zinc-700" />
              </a>
            ))}
            {images.length === 0 && <p className="text-zinc-500">Нет изображений</p>}
          </div>
        )}
        {tab === "Videos" && (
          <ul className="space-y-2 text-sm">
            {videos.map((a) => (
              <li key={a.id}>
                <a href={a.url} className="text-amber-400 hover:underline">
                  {a.storage_key}
                </a>
              </li>
            ))}
          </ul>
        )}
        {tab === "Audio" && (
          <ul className="space-y-2 text-sm">
            {audio.map((a) => (
              <li key={a.id}>
                <audio controls src={a.url} className="w-full" />
              </li>
            ))}
          </ul>
        )}
        {tab === "Packages" && (
          <pre className="overflow-auto text-sm text-zinc-300">
            {JSON.stringify(episode.platform_packages, null, 2)}
          </pre>
        )}
        {tab === "Compliance" && (
          <div>
            <pre className="overflow-auto text-sm text-zinc-300">
              {JSON.stringify(episode.compliance_report, null, 2)}
            </pre>
            <pre className="mt-4 overflow-auto text-sm text-amber-200/80">
              {JSON.stringify(episode.quality_report, null, 2)}
            </pre>
          </div>
        )}
        {tab === "Tasks" && (
          <ul className="space-y-1 text-sm">
            {episode.generation_tasks?.map((t) => (
              <li key={t.id} className="flex justify-between gap-4">
                <span>{t.step}</span>
                <span className="text-zinc-500">
                  {t.status} ({Math.round(t.progress * 100)}%)
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
