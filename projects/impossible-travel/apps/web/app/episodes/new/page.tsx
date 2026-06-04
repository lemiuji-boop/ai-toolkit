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

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { api } from "@/lib/api";

const schema = z.object({
  topic: z.string().min(2, "Минимум 2 символа"),
  duration_target: z.number().min(30).max(90),
  language: z.string(),
});

type FormData = z.infer<typeof schema>;

export default function NewEpisodePage() {
  const router = useRouter();
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      topic: "",
      duration_target: 60,
      language: "ru",
    },
  });

  const create = useMutation({
    mutationFn: (data: FormData) =>
      api.createEpisode({
        ...data,
        platforms: ["instagram", "tiktok", "youtube_shorts"],
      }),
    onSuccess: (ep) => router.push(`/episodes/${ep.id}`),
  });

  return (
    <div className="max-w-lg">
      <h1 className="mb-6 text-2xl font-bold">Новый выпуск</h1>
      <form
        onSubmit={handleSubmit((d) => create.mutate(d))}
        className="space-y-4"
      >
        <div>
          <label className="mb-1 block text-sm text-zinc-400">Тема / идея</label>
          <input
            {...register("topic")}
            placeholder="жерло вулкана"
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2"
          />
          {errors.topic && (
            <p className="text-sm text-red-400">{errors.topic.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm text-zinc-400">Длительность (сек)</label>
          <input
            type="number"
            {...register("duration_target", { valueAsNumber: true })}
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm text-zinc-400">Язык</label>
          <select
            {...register("language")}
            className="w-full rounded border border-zinc-700 bg-zinc-900 px-3 py-2"
          >
            <option value="ru">Русский</option>
            <option value="en">English</option>
          </select>
        </div>
        <p className="text-xs text-zinc-500">
          Платформы: Instagram, TikTok, YouTube Shorts (по умолчанию)
        </p>
        <button
          type="submit"
          disabled={create.isPending}
          className="rounded-md bg-amber-500 px-4 py-2 font-medium text-zinc-950 disabled:opacity-50"
        >
          {create.isPending ? "Создание..." : "Создать"}
        </button>
      </form>
    </div>
  );
}
