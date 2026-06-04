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
import Link from "next/link";
import { EpisodeCard } from "@/components/episode-card";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const { data: episodes, isLoading } = useQuery({
    queryKey: ["episodes"],
    queryFn: () => api.listEpisodes(),
  });

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-zinc-500">Виртуальные экспедиции Миры</p>
        </div>
        <Link
          href="/episodes/new"
          className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950"
        >
          Создать выпуск
        </Link>
      </div>
      {isLoading && <p className="text-zinc-500">Загрузка...</p>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {episodes?.map((ep) => (
          <EpisodeCard key={ep.id} episode={ep} />
        ))}
      </div>
      {!isLoading && episodes?.length === 0 && (
        <p className="text-zinc-500">Пока нет выпусков. Создайте первый!</p>
      )}
    </div>
  );
}
