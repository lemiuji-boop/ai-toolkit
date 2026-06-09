let lastRows = [];

const HEADERS = ["№","Обозначение","Наименование","Материал","Вид заготовки",
  "Кол-во на с/к","Мд, кг","Мз, кг","КИМ","Норма на деталь, кг","Норма на программу, кг","Замечания"];

function backendUrl(){ return (document.getElementById("backend").value || "").replace(/\/$/,""); }
function setStatus(t, ok){ const s=document.getElementById("status"); s.textContent=t; s.className="status"+(ok?" ok":""); }

Office.onReady(() => {
  const saved = window.localStorage.getItem("matnorm_backend");
  if (saved) document.getElementById("backend").value = saved;

  document.getElementById("saveBackend").onclick = async () => {
    window.localStorage.setItem("matnorm_backend", backendUrl());
    try {
      const r = await fetch(backendUrl()+"/health");
      setStatus(r.ok ? "Подключено к сервису" : "Сервис не отвечает", r.ok);
    } catch { setStatus("Нет связи с сервисом (проверьте HTTPS/сеть)", false); }
  };

  document.getElementById("run").onclick = runJob;
  document.getElementById("write").onclick = writeTable;
  document.getElementById("check").onclick = normControl;
});

async function runJob(){
  const draw = document.getElementById("drawing").files[0];
  const m3d  = document.getElementById("model3d").files[0];
  if(!draw){ setStatus("Выберите чертёж", false); return; }
  const fd = new FormData();
  fd.append("drawing", draw);
  if(m3d) fd.append("model3d", m3d);
  setStatus("Обработка…");
  try{
    const r = await fetch(backendUrl()+"/api/jobs", {method:"POST", body:fd});
    const data = await r.json();
    lastRows = data.rows;
    setStatus(`Готово. Источник распознавания: ${data.extract.source}, геометрия: ${data.geometry.source}`, true);
    renderFlags(data.verify.flags.concat(...lastRows.map(x=>x.flags)));
    document.getElementById("write").disabled = false;
    document.getElementById("check").disabled = false;
  }catch(e){ setStatus("Ошибка запроса к сервису", false); }
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
    // подсветить проблемные строки в листе
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
