/** Админ-панель МАТНОРМ — vanilla JS, без сборки. */

const SERVICE_LABELS = {
  backend: "Backend",
  rag: "RAG",
  ollama: "Ollama",
  addin: "Excel add-in",
  tunnel: "Cloudflare tunnel",
};

const SECTION_TITLES = {
  dashboard: "Дашборд",
  exports: "Экспорт",
  rag: "RAG",
  jobs: "Задания",
  providers: "Провайдеры ИИ",
  clients: "Подключения",
  services: "Сервисы",
  system: "Система",
};

const STATUS_LABELS = {
  ok: "Работает",
  degraded: "Деградация",
  down: "Недоступен",
};

function apiBase() {
  return document.getElementById("api-url").value.replace(/\/$/, "");
}

// ---------- Аутентификация (T-16): JWT в localStorage ----------

const TOKEN_KEY = "matnorm_admin_token";

function authToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function showLogin(message) {
  document.getElementById("login-overlay").classList.add("visible");
  document.getElementById("login-msg").textContent = message || "";
}

function hideLogin() {
  document.getElementById("login-overlay").classList.remove("visible");
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  showLogin("Вы вышли из системы.");
}

async function submitLogin(event) {
  event.preventDefault();
  const msg = document.getElementById("login-msg");
  msg.textContent = "Вход…";
  try {
    const res = await fetch(`${apiBase()}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: document.getElementById("login-user").value.trim(),
        password: document.getElementById("login-password").value,
      }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      msg.textContent = body.detail || `Ошибка входа: HTTP ${res.status}`;
      return;
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.token);
    document.getElementById("login-password").value = "";
    hideLogin();
    refreshAll();
  } catch (err) {
    msg.textContent = `Сеть/CORS: ${err.message}`;
  }
}

async function fetchJson(path, options) {
  const opts = { ...(options || {}) };
  opts.headers = { ...(opts.headers || {}) };
  const token = authToken();
  if (token) opts.headers["Authorization"] = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${apiBase()}${path}`, opts);
  } catch (err) {
    const hint =
      err instanceof TypeError
        ? " (сеть/CORS: откройте панель с http://127.0.0.1:3010 и проверьте URL API)"
        : "";
    throw new Error(`${path}: ${err.message}${hint}`);
  }
  if (res.status === 401) {
    // Токен отсутствует/истёк — показать форму входа.
    showLogin(token ? "Сессия истекла — войдите заново." : "");
    throw new Error(`${path}: требуется вход (HTTP 401)`);
  }
  if (!res.ok) throw new Error(`${path}: HTTP ${res.status}`);
  return res.json();
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text != null) node.textContent = text;
  return node;
}

function formatBytes(n) {
  if (n == null) return "—";
  if (n < 1024) return `${n} Б`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} КБ`;
  return `${(n / (1024 * 1024)).toFixed(1)} МБ`;
}

function statusBadge(ok, stub) {
  const span = el("span", `badge ${ok ? "ok" : stub ? "warn" : "err"}`);
  span.textContent = ok ? "доступен" : stub ? "заглушка" : "недоступен";
  return span;
}

function renderStatusBar(status) {
  const badge = document.getElementById("overall-status");
  const cls = status.status === "ok" ? "ok" : status.status === "degraded" ? "warn" : "err";
  badge.className = `overall-badge ${cls}`;
  badge.textContent = STATUS_LABELS[status.status] || status.status;

  const link = document.getElementById("tunnel-link");
  const url = status.tunnel_url || status.services?.tunnel?.url;
  if (url) {
    link.href = url;
    link.textContent = url;
  } else {
    link.href = "#";
    link.textContent = "не настроен";
  }
}

function renderProgress(progress) {
  const pct = progress.percent ?? 0;
  document.getElementById("progress-fill").style.width = `${Math.min(pct, 100)}%`;
  document.getElementById("progress-percent").textContent = `${pct}%`;
  document.getElementById("progress-label").textContent =
    progress.total > 0
      ? `Завершено ${progress.completed} из ${progress.total}`
      : "Нет данных об экспорте";

  const dl = document.getElementById("progress-stats");
  dl.replaceChildren();
  [
    ["Всего", String(progress.total)],
    ["Готово", String(progress.completed)],
    ["Ошибки", String(progress.failed)],
    ["В процессе", String(progress.in_progress)],
    ["Источник", progress.source],
  ].forEach(([k, v]) => {
    dl.appendChild(el("dt", null, k));
    dl.appendChild(el("dd", null, v));
  });
}

function renderStatusCards(services) {
  const root = document.getElementById("status-cards");
  root.replaceChildren();
  Object.entries(services).forEach(([name, info]) => {
    const card = el("div", "card status-card");
    card.appendChild(el("div", "name", SERVICE_LABELS[name] || name));
    if (info.latency_ms != null) {
      card.appendChild(el("div", "latency", `${info.latency_ms} мс`));
    }
    if (info.url) {
      const u = el("a", "latency tunnel-card-url", info.url);
      u.href = info.url;
      u.target = "_blank";
      u.rel = "noopener";
      card.appendChild(u);
    }
    card.appendChild(statusBadge(info.ok, info.source === "stub"));
    if (!info.ok && info.launch_hint) {
      const hint = el("div", "launch-hint", `Запустить: ${info.launch_hint}`);
      card.appendChild(hint);
    }
    root.appendChild(card);
  });
}

function renderGpu(gpuData) {
  const root = document.getElementById("gpu-gauge");
  root.replaceChildren();
  const gpus = gpuData.gpus || [];
  if (!gpus.length) {
    root.appendChild(el("p", "muted", gpuData.reason || "GPU не обнаружен (заглушка)"));
    return;
  }
  gpus.forEach((g) => {
    const row = el("div", "gauge-row");
    const util = g.utilization_pct ?? 0;
    const memPct =
      g.memory_total_mb && g.memory_used_mb
        ? Math.round((g.memory_used_mb / g.memory_total_mb) * 100)
        : 0;
    row.appendChild(el("label", null, `${g.name} — загрузка ${util}%`));
    const bar = el("div", "gauge-bar");
    const fill = el("div", "gauge-fill");
    fill.style.width = `${Math.min(util, 100)}%`;
    bar.appendChild(fill);
    row.appendChild(bar);
    row.appendChild(
      el("label", null, `VRAM: ${g.memory_used_mb ?? "?"} / ${g.memory_total_mb ?? "?"} МБ (${memPct}%)`)
    );
    root.appendChild(row);
  });
}

function renderSummary(status, metrics, jobs, progress) {
  const dl = document.getElementById("summary-stats");
  dl.replaceChildren();
  const items = [
    ["Общий статус", STATUS_LABELS[status.status] || status.status],
    ["Экспорт (готово)", `${progress.completed}/${progress.total}`],
    ["Заданий в буфере", String(status.active_jobs)],
    ["Записей jobs API", String(jobs.total)],
    ["Источник GPU", metrics.gpu.source || "—"],
  ];
  if (metrics.memory.total_mb != null) {
    items.push(["Память", `${metrics.memory.used_mb} / ${metrics.memory.total_mb} МБ`]);
  }
  items.forEach(([k, v]) => {
    dl.appendChild(el("dt", null, k));
    dl.appendChild(el("dd", null, v));
  });
}

function renderExports(exportsData) {
  const meta = document.getElementById("exports-meta");
  meta.replaceChildren();
  [
    ["JSON заданий", String(exportsData.job_count)],
    ["Файлов в списке", String(exportsData.files.length)],
  ].forEach(([k, v]) => {
    meta.appendChild(el("dt", null, k));
    meta.appendChild(el("dd", null, v));
  });

  const list = document.getElementById("exports-list");
  list.replaceChildren();
  if (exportsData.addin_zip_url) {
    const li = el("li");
    const a = el("a");
    a.href = `${apiBase()}${exportsData.addin_zip_url}`;
    a.textContent = "matnorm-addin.zip (надстройка Excel)";
    a.target = "_blank";
    li.appendChild(a);
    list.appendChild(li);
  }
  exportsData.files.forEach((f) => {
    const li = el("li");
    const a = el("a");
    a.href = `${apiBase()}${f.download_url}`;
    a.textContent = `${f.label} (${formatBytes(f.size_bytes)})`;
    a.target = "_blank";
    li.appendChild(a);
    list.appendChild(li);
  });
  if (!exportsData.files.length && !exportsData.addin_zip_url) {
    list.appendChild(el("li", "muted", "Нет готовых файлов. Запустите scripts/export-and-analyze.sh"));
  }
}

function renderRag(ragOverview) {
  document.getElementById("rag-description").textContent = ragOverview.description || "";
  const dl = document.getElementById("rag-stats");
  dl.replaceChildren();
  const health = ragOverview.health || {};
  const version = ragOverview.version || {};
  const items = [
    ["Статус RAG", health.ok ? "доступен" : "недоступен"],
    ["Embed backend", health.embed_backend || version.embed_backend || "—"],
    ["Версия", version.version || "—"],
    ["Хранилище", version.backend || "—"],
    ["Чанков в индексе", version.chunk_count != null ? String(version.chunk_count) : "—"],
  ];
  items.forEach(([k, v]) => {
    dl.appendChild(el("dt", null, k));
    dl.appendChild(el("dd", null, v));
  });
}

async function runRagSearch() {
  const query = document.getElementById("rag-query").value.trim();
  const out = document.getElementById("rag-results");
  if (!query) {
    out.textContent = "Введите запрос.";
    return;
  }
  out.textContent = "Поиск…";
  try {
    const data = await fetchJson("/api/rag/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, top_k: 5 }),
    });
    out.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    out.textContent = `Ошибка: ${err.message}`;
  }
}

function renderJobs(jobs) {
  const tbody = document.getElementById("jobs-tbody");
  tbody.replaceChildren();
  if (!jobs.jobs.length) {
    const tr = el("tr");
    const td = el("td", "muted", "Нет заданий в журнале. Запустите POST /api/jobs или scripts/export-and-analyze.sh");
    td.colSpan = 8;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  jobs.jobs.forEach((j) => {
    const tr = el("tr");
    const dc = j.data_completeness || {};
    const unavailable = [
      dc.has_drawing && !dc.vision_available ? "vision" : null,
      dc.has_model3d && !dc.geometry_available ? "geom" : null,
      j.vision_available === false ? "vision" : null,
      j.geometry_available === false ? "geom" : null,
    ].filter(Boolean);
    const stubs = [...new Set(unavailable)].join(", ") || "—";
    const completeness = `чертёж:${dc.has_drawing ? "✓" : "—"} 3D:${dc.has_model3d ? "✓" : "—"}`;
    [
      j.job_id?.slice(0, 8) + "…",
      j.input_hash,
      j.mode,
      completeness,
      j.status,
      stubs,
      String(j.rows_count ?? "—"),
      j.finished_at?.replace("T", " ").slice(0, 19) || "—",
    ].forEach((cell, i) => {
      const td = el("td", i < 2 ? "mono" : null, cell);
      if (i === 0) td.title = j.job_id;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

// ---------- Провайдеры ИИ ----------

let presetsCache = {};

function fillPresetSelect(presets) {
  presetsCache = presets || {};
  const sel = document.getElementById("prov-preset");
  const current = sel.value;
  sel.replaceChildren(el("option", null, "— вручную —"));
  sel.options[0].value = "";
  Object.keys(presetsCache).forEach((key) => {
    const opt = el("option", null, `${key} (${presetsCache[key].kind})`);
    opt.value = key;
    sel.appendChild(opt);
  });
  sel.value = current;
}

function applyPreset() {
  const key = document.getElementById("prov-preset").value;
  const preset = presetsCache[key];
  if (!preset) return;
  document.getElementById("prov-kind").value = preset.kind;
  document.getElementById("prov-base-url").value = preset.base_url;
  if (!document.getElementById("prov-name").value) {
    document.getElementById("prov-name").value = key;
  }
}

async function testProvider(id, btn) {
  btn.disabled = true;
  btn.textContent = "Проверка…";
  try {
    const res = await fetchJson(`/api/admin/providers/${id}/test`, { method: "POST" });
    const mode = res.checked === "network" ? "сеть" : "валидация";
    const lat = res.latency_ms != null ? `, ${res.latency_ms} мс` : "";
    alert(`${res.ok ? "✓" : "✗"} [${mode}${lat}] ${res.detail}`);
  } catch (err) {
    alert(`Ошибка проверки: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.textContent = "Проверить";
  }
}

async function deleteProvider(id, name) {
  if (!confirm(`Удалить провайдера «${name}» (вместе с ключом)?`)) return;
  try {
    await fetchJson(`/api/admin/providers/${id}`, { method: "DELETE" });
    await refreshProviders();
  } catch (err) {
    alert(`Ошибка удаления: ${err.message}`);
  }
}

function renderProviders(data) {
  fillPresetSelect(data.presets);
  document.getElementById("providers-egress").textContent = data.allow_external
    ? "⚠ ALLOW_EXTERNAL_PROVIDERS=1: разрешены исходящие вызовы внешних API для неконфиденциальных задач."
    : "Исходящие вызовы внешних API выключены (SEC-001). Внешние провайдеры сохраняются, но не участвуют в маршрутизации до включения ALLOW_EXTERNAL_PROVIDERS=1.";

  const tbody = document.getElementById("providers-tbody");
  tbody.replaceChildren();
  if (!data.providers.length) {
    const tr = el("tr");
    const td = el("td", "muted", "Провайдеры не настроены. Используется локальный Ollama из .env.");
    td.colSpan = 8;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  data.providers.forEach((p) => {
    const tr = el("tr");
    [
      p.name,
      p.kind,
      p.base_url,
      p.model,
      p.has_api_key ? p.api_key_masked : "—",
      String(p.priority),
      p.enabled ? "включён" : "выключен",
    ].forEach((cell, i) => tr.appendChild(el("td", i === 2 ? "mono" : null, cell)));
    const actions = el("td");
    const testBtn = el("button", "small", "Проверить");
    testBtn.type = "button";
    testBtn.addEventListener("click", () => testProvider(p.id, testBtn));
    const delBtn = el("button", "small danger", "Удалить");
    delBtn.type = "button";
    delBtn.addEventListener("click", () => deleteProvider(p.id, p.name));
    actions.appendChild(testBtn);
    actions.appendChild(delBtn);
    tr.appendChild(actions);
    tbody.appendChild(tr);
  });
}

async function refreshProviders() {
  try {
    renderProviders(await fetchJson("/api/admin/providers"));
  } catch (err) {
    const tbody = document.getElementById("providers-tbody");
    tbody.replaceChildren();
    const tr = el("tr");
    const td = el("td", "muted", `Ошибка: ${err.message}`);
    td.colSpan = 8;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}

async function submitProviderForm(event) {
  event.preventDefault();
  const msg = document.getElementById("provider-form-msg");
  msg.textContent = "Сохранение…";
  const payload = {
    name: document.getElementById("prov-name").value.trim(),
    preset: document.getElementById("prov-preset").value || null,
    kind: document.getElementById("prov-kind").value,
    base_url: document.getElementById("prov-base-url").value.trim() || null,
    model: document.getElementById("prov-model").value.trim(),
    api_key: document.getElementById("prov-api-key").value || null,
    priority: Number(document.getElementById("prov-priority").value) || 100,
  };
  try {
    await fetchJson("/api/admin/providers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    msg.textContent = "✓ Провайдер добавлен";
    document.getElementById("provider-form").reset();
    await refreshProviders();
  } catch (err) {
    msg.textContent = `Ошибка: ${err.message}`;
  }
}

// ---------- Подключения клиентов ----------

function renderClients(data) {
  const tbody = document.getElementById("clients-tbody");
  tbody.replaceChildren();
  if (!data.clients.length) {
    const tr = el("tr");
    const td = el("td", "muted", "Подключений пока нет. Откройте надстройку Excel с другого ПК.");
    td.colSpan = 6;
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }
  const serverIps = new Set(data.server_ips || []);
  const fmt = (iso) => (iso ? iso.replace("T", " ").slice(0, 19) : "—");
  data.clients.forEach((c) => {
    const external = !serverIps.has(c.ip) && c.ip !== "testclient";
    const tr = el("tr", external ? "client-external" : null);
    [
      external ? `${c.ip} ●` : c.ip,
      fmt(c.first_seen),
      fmt(c.last_seen),
      String(c.requests),
      c.last_endpoint || "—",
      c.user_agent || "—",
    ].forEach((cell, i) => tr.appendChild(el("td", i === 0 ? "mono" : null, cell)));
    if (external) tr.title = "Внешний клиент (не серверный IP) — например, ПК с Excel";
    tbody.appendChild(tr);
  });
}

async function refreshClients() {
  try {
    renderClients(await fetchJson("/api/admin/clients"));
  } catch (err) {
    const tbody = document.getElementById("clients-tbody");
    tbody.replaceChildren();
    const tr = el("tr");
    const td = el("td", "muted", `Ошибка: ${err.message}`);
    td.colSpan = 6;
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}

function renderServicesDetail(data) {
  const root = document.getElementById("services-detail");
  root.replaceChildren();
  Object.entries(data.services).forEach(([name, info]) => {
    const card = el("div", "card service-detail");
    card.appendChild(el("h2", null, SERVICE_LABELS[name] || name));
    card.appendChild(statusBadge(info.ok, info.source === "stub"));
    const pre = el("pre");
    pre.textContent = JSON.stringify(info, null, 2);
    card.appendChild(pre);
  });
}

function renderSystem(servicesPayload, metrics) {
  const sys = document.getElementById("system-info");
  sys.replaceChildren();
  const s = servicesPayload.system || {};
  Object.entries({
    "Сервис": s.service,
    "Версия backend": s.version,
    "Модель inference": s.inference_model,
    "INFERENCE_URL": s.inference_url,
    "RAG URL": s.rag_url,
    "Add-in URL": s.addin_url,
    "Tunnel URL": s.tunnel_url,
    "rules.json (хеш)": s.rules_version,
  }).forEach(([k, v]) => {
    sys.appendChild(el("dt", null, k));
    sys.appendChild(el("dd", null, v ?? "—"));
  });

  const host = document.getElementById("host-metrics");
  host.replaceChildren();
  const m = metrics.memory || {};
  const c = metrics.cpu_load || {};
  Object.entries({
    "Память (исп.)": m.used_mb != null ? `${m.used_mb} МБ` : "—",
    "Память (всего)": m.total_mb != null ? `${m.total_mb} МБ` : "—",
    "Load 1m": c.load_1m,
    "Load 5m": c.load_5m,
    "Load 15m": c.load_15m,
  }).forEach(([k, v]) => {
    host.appendChild(el("dt", null, k));
    host.appendChild(el("dd", null, String(v ?? "—")));
  });
}

async function refreshAll() {
  const updated = document.getElementById("last-updated");
  const barTime = document.getElementById("status-bar-time");
  updated.textContent = "Обновление…";
  try {
    const [status, metrics, jobs, services, progress, exportsData, ragOverview] =
      await Promise.all([
        fetchJson("/api/admin/status"),
        fetchJson("/api/admin/metrics"),
        fetchJson("/api/admin/jobs"),
        fetchJson("/api/admin/services"),
        fetchJson("/api/admin/progress"),
        fetchJson("/api/admin/exports"),
        fetchJson("/api/admin/rag/overview"),
      ]);
    renderStatusBar(status);
    renderProgress(progress);
    renderStatusCards(status.services);
    renderGpu(metrics.gpu);
    renderSummary(status, metrics, jobs, progress);
    renderExports(exportsData);
    renderRag(ragOverview);
    renderJobs(jobs);
    renderServicesDetail(services);
    renderSystem(services, metrics);
    await Promise.all([refreshProviders(), refreshClients()]);
    const ts = new Date().toLocaleTimeString("ru-RU");
    updated.textContent = `Обновлено: ${ts}`;
    barTime.textContent = `Обновлено: ${ts}`;
  } catch (err) {
    updated.textContent = `Ошибка: ${err.message}`;
    barTime.textContent = `Ошибка: ${err.message}`;
  }
}

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    const section = btn.dataset.section;
    document.getElementById(section).classList.add("active");
    document.getElementById("page-title").textContent = SECTION_TITLES[section];
  });
});

document.getElementById("btn-refresh").addEventListener("click", refreshAll);
document.getElementById("provider-form").addEventListener("submit", submitProviderForm);
document.getElementById("prov-preset").addEventListener("change", applyPreset);
document.getElementById("api-url").addEventListener("change", refreshAll);
document.getElementById("btn-rag-search").addEventListener("click", runRagSearch);
document.getElementById("rag-query").addEventListener("keydown", (e) => {
  if (e.key === "Enter") runRagSearch();
});
document.getElementById("login-form").addEventListener("submit", submitLogin);
document.getElementById("btn-logout").addEventListener("click", logout);

if (authToken()) {
  refreshAll();
} else {
  showLogin("");
}
setInterval(() => {
  if (authToken()) refreshAll();
}, 30000);
