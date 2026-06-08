<!--
Copyright 2026 Rinat Ishmaev

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

<script setup lang="ts">
import { ref } from "vue";

export type FileItem = {
  id: string;
  name: string;
  size: string;
  mime: string;
  time: string;
};

defineProps<{
  files: FileItem[];
  calculationId?: string;
  uploading?: boolean;
}>();

const emit = defineEmits<{
  upload: [files: FileList];
  download: [id: string];
}>();

const dragOver = ref(false);

function onDrop(e: DragEvent) {
  dragOver.value = false;
  if (e.dataTransfer?.files?.length) emit("upload", e.dataTransfer.files);
}

function iconFor(name: string) {
  if (name.endsWith(".pdf")) return "📄";
  if (/\.(png|jpg|jpeg|webp)$/i.test(name)) return "🖼";
  if (/\.(xls|xlsx)$/i.test(name)) return "📊";
  if (/\.(doc|docx)$/i.test(name)) return "📝";
  return "📁";
}
</script>

<template>
  <section class="fm pf-card">
    <h2 class="pf-section-title">Файлы КД</h2>
    <div
      class="dropzone"
      :class="{ over: dragOver, busy: uploading }"
      @dragover.prevent="dragOver = true"
      @dragleave="dragOver = false"
      @drop.prevent="onDrop"
    >
      <div class="cloud">☁</div>
      <p><strong>Drag & Drop</strong> или выберите файлы</p>
      <p class="pf-muted">PDF, DOCX, XLSX, PNG, JPG, ZIP — до 100 МБ</p>
      <label class="pf-btn pf-btn-primary pick">
        Выбрать файлы
        <input
          type="file"
          multiple
          hidden
          @change="(e) => (e.target as HTMLInputElement).files && emit('upload', (e.target as HTMLInputElement).files!)"
        />
      </label>
    </div>
    <ul class="list">
      <li v-for="f in files" :key="f.id">
        <span class="ico">{{ iconFor(f.name) }}</span>
        <div class="info">
          <strong>{{ f.name }}</strong>
          <span class="pf-muted">{{ f.size }} · {{ f.time }}</span>
        </div>
        <button type="button" class="icon-btn" title="Скачать" @click="emit('download', f.id)">⬇</button>
      </li>
      <li v-if="!files.length" class="empty pf-muted">Файлов пока нет</li>
    </ul>
  </section>
</template>

<style scoped>
.fm {
  margin-top: 0;
}
.dropzone {
  border: 2px dashed #93c5fd;
  border-radius: var(--pf-radius);
  padding: 28px;
  text-align: center;
  background: #f8fbff;
  margin-bottom: 20px;
  transition: 0.2s;
}
.dropzone.over {
  background: #eff6ff;
  border-color: var(--pf-primary);
}
.dropzone.busy {
  opacity: 0.7;
}
.cloud {
  font-size: 36px;
  margin-bottom: 8px;
}
.pick {
  margin-top: 12px;
  cursor: pointer;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}
.ico {
  font-size: 22px;
}
.info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.info strong {
  font-size: 14px;
}
.icon-btn {
  border: none;
  background: #f1f5f9;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
}
.empty {
  padding: 16px 0;
}
</style>
