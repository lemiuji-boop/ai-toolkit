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

import { API_BASE, apiFetch } from "./client";

export type UploadedFile = {
  id: string;
  original_name: string;
  mime_type: string;
  size_bytes: number;
  storage_key: string;
};

/** Загрузка файлов в карантин (multipart). */
export async function uploadFiles(
  token: string,
  calculationId: string,
  fileList: FileList | File[],
): Promise<UploadedFile[]> {
  const fd = new FormData();
  fd.append("calculation_id", calculationId);
  const files = fileList instanceof FileList ? Array.from(fileList) : fileList;
  for (const f of files) fd.append("files", f);
  const r = await fetch(`${API_BASE}/api/v1/files/upload`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: fd,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error((err as { detail?: string }).detail ?? "Ошибка загрузки");
  }
  return r.json() as Promise<UploadedFile[]>;
}

export function fileDownloadUrl(fileId: string): string {
  return `${API_BASE}/api/v1/files/${fileId}/download`;
}

export function getFile(token: string, fileId: string) {
  return apiFetch<UploadedFile>(`/api/v1/files/${fileId}`, {}, token);
}
