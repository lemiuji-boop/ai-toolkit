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

const styles: Record<string, string> = {
  draft: "bg-zinc-700 text-zinc-200",
  generating: "bg-blue-900 text-blue-200",
  ready_for_review: "bg-amber-900 text-amber-200",
  approved: "bg-green-900 text-green-200",
  published: "bg-purple-900 text-purple-200",
  failed: "bg-red-900 text-red-200",
};

export function EpisodeStatusBadge({ status }: { status: string }) {
  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[status] || styles.draft}`}
    >
      {status}
    </span>
  );
}
