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

export default function SettingsPage() {
  const { data } = useQuery({
    queryKey: ["settings"],
    queryFn: () => api.getSettings(),
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Настройки</h1>
      <dl className="space-y-2 text-sm">
        <div className="flex gap-2">
          <dt className="text-zinc-500">MOCK_GENERATION:</dt>
          <dd>{String(data?.mock_generation)}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="text-zinc-500">APP_ENV:</dt>
          <dd>{data?.app_env}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="text-zinc-500">API URL:</dt>
          <dd>{process.env.NEXT_PUBLIC_API_URL}</dd>
        </div>
      </dl>
      <p className="mt-6 text-xs text-zinc-600">
        API-ключи настраиваются в .env на сервере. См. docs/INPUTS_ACCOUNTS_API_KEYS.md
      </p>
    </div>
  );
}
