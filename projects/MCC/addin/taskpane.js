let lastRows = [];
let catalogData = null;
let serverOnline = false;

const HEADERS = ["№","Обозначение","Наименование","Материал","Вид заготовки",
  "Кол-во на с/к","Мд, кг","Мз, кг","КИМ","Норма на деталь, кг","Норма на программу, кг","Замечания"];

function backendUrl(){ return (document.getElementById("backend").value || "").replace(/\/$/,""); }

function setStatus(t, ok){
  const s = document.getElementById("status");
  s.textContent = t;
  s.className = "status" + (ok === true ? " ok" : ok === false ? " err" : "");
}

function setConn(ok, label){
  serverOnline = !!ok;
  const dot = document.getElementById("connDot");
  const lbl = document.getElementById("connLabel");
  dot.className = "dot " + (ok ? "ok" : "err");
  lbl.textContent = label;
}

async function loadConfig(){
  try{
    const r = await fetch("config.json", {cache:"no-store"});
    if(!r.ok) return null;
    return await r.json();
  }catch{ return null; }
}

function chatMsg(text, who){
  const log = document.getElementById("chatLog");
  const d = document.createElement("div");
  d.className = "msg " + (who || "bot");
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}

function showPreview(obj){
  const box = document.getElementById("resultPreview");
  box.textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
  box.classList.add("show");
}

async function checkHealth(){
  const url = backendUrl();
  if(!url){ setConn(false, "Адрес не задан"); return false; }
  try{
    const r = await fetch(url + "/health", {cache:"no-store"});
    if(r.ok){
      setConn(true, "Сервер доступен");
      setStatus("Подключено к сервису", true);
      return true;
    }
    setConn(false, "Сервис не отвечает (" + r.status + ")");
    setStatus("Сервис не отвечает", false);
    return false;
  }catch{
    setConn(false, "Нет связи (HTTPS/CORS?)");
    setStatus("Нет связи с сервисом — проверьте tunnel и mixed content", false);
    return false;
  }
}

async function loadCatalog(){
  const box = document.getElementById("catalog");
  if(!serverOnline){
    box.textContent = "Сначала подключитесь к сервису.";
    return;
  }
  box.textContent = "Загрузка каталога…";
  try{
    const r = await fetch(backendUrl() + "/api/addin/catalog", {cache:"no-store"});
    if(!r.ok){ box.textContent = "Ошибка каталога: " + r.status; return; }
    catalogData = await r.json();
    renderCatalog(catalogData);
    chatMsg("Каталог: " + catalogData.total + " файлов (" + catalogData.job_count + " заданий)", "bot");
  }catch{
    box.textContent = "Не удалось загрузить каталог.";
  }
}

function renderCatalog(data){
  const box = document.getElementById("catalog");
  box.innerHTML = "";
  const groups = [
    ["reports", "Отчёты и сводки"],
    ["jobs", "Задания (расчёты)"],
    ["reference", "Эталонные xlsx"],
  ];
  groups.forEach(([key, title]) => {
    const items = (data.groups && data.groups[key]) || [];
    if(!items.length) return;
    const g = document.createElement("div");
    g.className = "cat-group";
    const h = document.createElement("h3");
    h.textContent = title + " (" + items.length + ")";
    g.appendChild(h);
    items.forEach(item => g.appendChild(catalogItemEl(item)));
    box.appendChild(g);
  });
  if(!box.children.length){
    box.textContent = "На сервере пока нет готовых выгрузок.";
  }
}

function catalogItemEl(item){
  const el = document.createElement("div");
  el.className = "cat-item";
  const title = document.createElement("div");
  title.textContent = item.label;
  el.appendChild(title);
  const meta = document.createElement("div");
  meta.className = "meta";
  const parts = [formatSize(item.size_bytes)];
  if(item.job_hash) parts.push("id: " + item.job_hash.slice(0,8) + "…");
  if(item.mode) parts.push("mode: " + item.mode);
  if(item.verify_ok !== undefined && item.verify_ok !== null){
    parts.push("verify: " + (item.verify_ok ? "ok" : "замечания"));
  }
  if(item.rows_count != null) parts.push("строк: " + item.rows_count);
  meta.textContent = parts.join(" · ");
  el.appendChild(meta);
  const actions = document.createElement("div");
  actions.className = "actions";
  const dl = document.createElement("button");
  dl.textContent = "Скачать";
  dl.onclick = () => downloadExport(item.path, item.label);
  actions.appendChild(dl);
  if(item.job_hash){
    const load = document.createElement("button");
    load.textContent = "В панель";
    load.className = "ghost";
    load.onclick = () => fetchJobToPane(item.job_hash);
    actions.appendChild(load);
    const sheet = document.createElement("button");
    sheet.textContent = "В лист";
    sheet.className = "ghost";
    sheet.onclick = () => fetchJobToSheet(item.job_hash);
    actions.appendChild(sheet);
  }
  el.appendChild(actions);
  return el;
}

function formatSize(bytes){
  if(bytes < 1024) return bytes + " B";
  if(bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / 1048576).toFixed(1) + " MB";
}

async function downloadExport(path, label){
  if(!serverOnline){ chatMsg("Сервер недоступен", "bot"); return; }
  chatMsg("Скачивание: " + (label || path), "user");
  try{
    const r = await fetch(backendUrl() + "/api/addin/download?path=" + encodeURIComponent(path));
    if(!r.ok){ chatMsg("Ошибка скачивания: " + r.status, "bot"); return; }
    const blob = await r.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = path.split("/").pop();
    a.click();
    URL.revokeObjectURL(a.href);
    if(path.endsWith(".json")){
      const text = await blob.text();
      try{ showPreview(JSON.parse(text)); }catch{ showPreview(text.slice(0, 2000)); }
    }
    chatMsg("Файл загружен: " + a.download, "bot");
  }catch{
    chatMsg("Ошибка скачивания", "bot");
  }
}

async function fetchJobToPane(jobHash){
  chatMsg("Загрузка расчёта " + jobHash.slice(0,8) + "…", "user");
  try{
    const r = await fetch(backendUrl() + "/api/addin/fetch-job", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({job_hash: jobHash}),
    });
    if(!r.ok){ chatMsg("Задание не найдено", "bot"); return; }
    const data = await r.json();
    applyJobData(data);
    chatMsg("Расчёт загружен: mode=" + data.mode + ", verify=" + (data.verify && data.verify.ok), "bot");
  }catch{
    chatMsg("Ошибка загрузки расчёта", "bot");
  }
}

async function fetchJobToSheet(jobHash){
  await fetchJobToPane(jobHash);
  if(lastRows.length) await writeTable();
}

function applyJobData(data){
  lastRows = (data.rows || []).map((r, i) => ({
    num: r.num || i + 1,
    designation: "",
    name: "",
    material: r.material,
    zagotovka: r.zagotovka,
    qty_per_set: r.qty_per_set,
    md_kg: r.md_kg,
    mz_kg: r.mz_kg,
    kim: r.kim,
    norm_per_part_kg: r.norm_per_part_kg,
    norm_program_kg: r.norm_program_kg,
    flags: r.flags || [],
  }));
  showPreview(data);
  renderFlags((data.verify && data.verify.flags) || []);
  document.getElementById("write").disabled = !lastRows.length;
  document.getElementById("check").disabled = !lastRows.length;
  setStatus("Данные расчёта в панели (" + lastRows.length + " строк)", true);
}

async function handleChatCommand(raw){
  const cmd = (raw || "").trim().toLowerCase();
  if(!cmd) return;
  chatMsg(raw, "user");
  if(cmd === "help" || cmd === "помощь"){
    chatMsg("команды: каталог, выгрузить расчёт, health", "bot");
    return;
  }
  if(cmd === "каталог" || cmd === "catalog"){
    await loadCatalog();
    return;
  }
  if(cmd === "health" || cmd === "статус"){
    await checkHealth();
    return;
  }
  if(cmd.includes("выгрузить") || cmd.includes("расчёт") || cmd.includes("расчет")){
    if(!catalogData || !catalogData.groups || !catalogData.groups.jobs.length){
      await loadCatalog();
    }
    const jobs = (catalogData && catalogData.groups && catalogData.groups.jobs) || [];
    if(!jobs.length){
      chatMsg("Нет готовых расчётов на сервере", "bot");
      return;
    }
    const latest = jobs[jobs.length - 1];
    await fetchJobToPane(latest.job_hash);
    return;
  }
  if(cmd.startsWith("job ") || cmd.startsWith("задание ")){
    const hash = cmd.split(/\s+/)[1];
    if(hash && /^[a-f0-9]{8,12}$/.test(hash)){
      const full = hash.length === 12 ? hash : findJobHash(hash);
      if(full) await fetchJobToPane(full);
      else chatMsg("Задание не найдено в каталоге", "bot");
      return;
    }
  }
  chatMsg("Неизвестная команда. Попробуйте: каталог, выгрузить расчёт, help", "bot");
}

function findJobHash(prefix){
  const jobs = (catalogData && catalogData.groups && catalogData.groups.jobs) || [];
  const hit = jobs.find(j => j.job_hash && j.job_hash.startsWith(prefix));
  return hit ? hit.job_hash : null;
}

Office.onReady(async () => {
  const cfg = await loadConfig();
  const saved = window.localStorage.getItem("matnorm_backend");
  const def = (cfg && (cfg.tunnelUrl || cfg.backendUrl)) ? (cfg.tunnelUrl || cfg.backendUrl) : "";
  document.getElementById("backend").value = saved || def;

  document.getElementById("saveBackend").onclick = async () => {
    window.localStorage.setItem("matnorm_backend", backendUrl());
    if(await checkHealth()) await loadCatalog();
  };

  document.getElementById("refreshCatalog").onclick = loadCatalog;
  document.getElementById("run").onclick = runJob;
  document.getElementById("write").onclick = writeTable;
  document.getElementById("check").onclick = normControl;

  document.getElementById("chatSend").onclick = () => {
    const inp = document.getElementById("chatInput");
    handleChatCommand(inp.value);
    inp.value = "";
  };
  document.getElementById("chatInput").addEventListener("keydown", (e) => {
    if(e.key === "Enter") document.getElementById("chatSend").click();
  });

  if(def){
    await checkHealth();
    if(serverOnline) await loadCatalog();
  }else{
    setConn(false, "Укажите адрес tunnel");
  }
});

async function pollJob(jobId){
  for(let i = 0; i < 120; i++){
    const r = await fetch(backendUrl()+"/api/jobs/"+jobId);
    const data = await r.json();
    if(data.stage) setStatus("Этап: "+data.stage);
    if(data.status === "done") return data.result;
    if(data.status === "error"){
      const code = data.error_code ? "["+data.error_code+"] " : "";
      throw new Error(code+(data.error || "ошибка задания"));
    }
    await new Promise(res => setTimeout(res, 400));
  }
  throw new Error("таймаут ожидания задания");
}

async function runJob(){
  const draw = document.getElementById("drawing").files[0];
  const m3d  = document.getElementById("model3d").files[0];
  if(!draw && !m3d){ setStatus("Выберите чертёж и/или 3D", false); return; }
  const fd = new FormData();
  if(draw) fd.append("drawing", draw);
  if(m3d) fd.append("model3d", m3d);
  setStatus("Постановка задания…");
  try{
    const r = await fetch(backendUrl()+"/api/jobs", {method:"POST", body:fd});
    if(r.status !== 202){
      setStatus("Сервер не принял задание ("+r.status+")", false);
      return;
    }
    const queued = await r.json();
    const data = await pollJob(queued.job_id);
    lastRows = data.rows;
    setStatus("Готово. Распознавание: "+data.extract.source+", геометрия: "+data.geometry.source, true);
    renderFlags(data.verify.flags.concat(...lastRows.map(x=>x.flags)));
    showPreview({mode: data.mode, verify: data.verify, rows_count: lastRows.length});
    document.getElementById("write").disabled = false;
    document.getElementById("check").disabled = false;
  }catch(e){ setStatus("Ошибка: "+(e.message || "запрос к сервису"), false); }
}

function rowValues(r){
  return [r.num, r.designation, r.name, r.material, r.zagotovka, r.qty_per_set,
    r.md_kg, r.mz_kg, r.kim, r.norm_per_part_kg, r.norm_program_kg, (r.flags||[]).join("; ")];
}

async function writeTable(){
  await Excel.run(async (ctx) => {
    const sheet = ctx.workbook.worksheets.getActiveWorksheet();
    const all = [HEADERS, ...lastRows.map(rowValues)];
    const range = sheet.getRangeByIndexes(0, 0, all.length, HEADERS.length);
    range.values = all;
    const head = sheet.getRangeByIndexes(0,0,1,HEADERS.length);
    head.format.fill.color = "#1F3864";
    head.format.font.color = "white";
    head.format.font.bold = true;
    sheet.getUsedRange().format.autofitColumns();
    await ctx.sync();
  });
  setStatus("Ведомость записана в лист", true);
  chatMsg("Ведомость записана в активный лист", "bot");
}

async function normControl(){
  try{
    const r = await fetch(backendUrl()+"/api/normcontrol", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({rows: lastRows})
    });
    const data = await r.json();
    lastRows = data.rows;
    renderFlags(data.flags);
    await Excel.run(async (ctx) => {
      const sheet = ctx.workbook.worksheets.getActiveWorksheet();
      lastRows.forEach((row, i) => {
        if(row.flags && row.flags.length){
          sheet.getRangeByIndexes(i+1, 0, 1, HEADERS.length).format.fill.color = "#FAEEDA";
        }
      });
      await ctx.sync();
    });
    setStatus(data.flags.length ? "Найдены замечания — см. список" : "Замечаний нет", data.flags.length===0);
  }catch(e){ setStatus("Ошибка нормоконтроля", false); }
}

function renderFlags(flags){
  const box = document.getElementById("flags");
  box.innerHTML = "";
  (flags||[]).forEach(f => { const d=document.createElement("div"); d.className="f"; d.textContent=f; box.appendChild(d); });
}
