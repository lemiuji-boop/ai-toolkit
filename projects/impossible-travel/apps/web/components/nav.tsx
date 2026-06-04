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

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/episodes", label: "Выпуски" },
  { href: "/characters", label: "Персонажи" },
  { href: "/assets", label: "Ассеты" },
  { href: "/settings", label: "Настройки" },
];

export function Nav() {
  return (
    <nav className="border-b border-zinc-800 bg-zinc-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
        <Link href="/dashboard" className="font-semibold text-amber-400">
          Impossible Travel AI
        </Link>
        {links.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            className="text-sm text-zinc-400 hover:text-zinc-100"
          >
            {l.label}
          </Link>
        ))}
        <Link
          href="/episodes/new"
          className="ml-auto rounded-md bg-amber-500 px-3 py-1.5 text-sm font-medium text-zinc-950 hover:bg-amber-400"
        >
          + Создать выпуск
        </Link>
      </div>
    </nav>
  );
}
