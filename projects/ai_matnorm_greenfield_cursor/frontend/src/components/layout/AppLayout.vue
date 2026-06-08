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
import AppSidebar from "./AppSidebar.vue";
import AppHeader from "./AppHeader.vue";
</script>

<template>
  <div class="pf-app">
    <div class="pf-bg" />
    <AppSidebar />
    <div class="pf-main">
      <AppHeader />
      <div class="pf-content">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.pf-app {
  display: flex;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}
.pf-bg {
  position: fixed;
  inset: 0;
  background: var(--pf-bg-gradient);
  z-index: 0;
}
.pf-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  min-width: 0;
}
.pf-content {
  flex: 1;
  padding: 0 28px 28px;
  overflow: auto;
}
</style>
