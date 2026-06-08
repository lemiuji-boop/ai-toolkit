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

/*
  ЖКТО AI-редактор вопросов
  Сервер без учетных записей: гости работают сразу, админ открывает настройки API-ключей по паролю.

  Запуск:
    ADMIN_PASSWORD="ваш_пароль" PORT=8787 node server.js

  После запуска открыть:
    http://localhost:8787
*/

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');
const { URL } = require('url');

const PORT = Number(process.env.PORT || 8787);
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
const DATA_DIR = process.env.KTO_DATA_DIR || __dirname;
try { fs.mkdirSync(DATA_DIR, { recursive: true }); } catch {}
const DATA_FILE = path.join(DATA_DIR, 'server-data.json');
const INDEX_FILE = process.env.KTO_INDEX_FILE || path.join(__dirname, 'index.html');
const sessions = new Map();
const sseClients = new Set();

const DEFAULT_MAIN_PROMPT = `Ты инженер-технолог авиационного производства и специалист по оформлению журнала конструкторско-технологической отработки.

Задача: переформулировать исходный вопрос технологически правильным языком согласно логике ЕСКД и ЕСТД. Формулировка должна быть понятной, конструктивно-логичной, деловой и пригодной для внесения в столбец "3" журнала КТО.

Строго соблюдай структуру ответа:
Причина:

Предложение/Содержание:

Классификация вопроса:

Исполнитель:

Правила:
1. В разделе "Причина" кратко и точно сформулируй суть проблемы, несоответствия, неопределенности или производственного затруднения.
2. В разделе "Предложение/Содержание" подробно опиши проблему технически корректным языком и, если возможно, предложи способ устранения: уточнить КД, внести изменение, согласовать с КБ, выдать технологическое решение, скорректировать чертеж, уточнить размеры, крепеж, материал, покрытие, допуск, сборочную последовательность, маршрут или комплектность.
3. В разделе "Классификация вопроса" укажи только одно значение: "технологическая" или "конструктивная".
4. Если вопрос связан с чертежом, размерами, материалом, составом изделия, конструкцией, креплением, отверстиями, базированием, компоновкой, зазорами, допусками, массой или составом КД — классифицируй как "конструктивная".
5. Если вопрос связан со способом изготовления, сборкой, маршрутом, оснасткой, трудоемкостью, последовательностью операций, возможностью выполнения операции, доступом инструмента, контролем, технологическими переходами или производственным процессом — классифицируй как "технологическая".
6. В разделе "Исполнитель" напиши: "инженер-технолог <ФИО>". ФИО передается отдельно.
7. Не добавляй вводных фраз, пояснений, Markdown-заголовков, таблиц и списков вне заданного шаблона.
8. Не добавляй блоки "Составил", "Повторяемость", "Примечание".
9. Не выдумывай номера документов, извещений, чертежей и деталей, если их нет в исходном вопросе.
10. Сохраняй технический смысл исходного вопроса, но убирай разговорные, резкие и неполные формулировки.`;


const DEFAULT_PROVIDERS = [
  { id: 'openai', name: 'OpenAI', region: 'США', adapter: 'openai-compatible', baseUrl: 'https://api.openai.com/v1', model: 'gpt-5.5', apiKey: '', enabled: true },
  { id: 'anthropic', name: 'Anthropic Claude', region: 'США', adapter: 'anthropic', baseUrl: 'https://api.anthropic.com/v1', model: 'claude-sonnet-4-5', apiKey: '', enabled: true },
  { id: 'gemini', name: 'Google Gemini', region: 'США', adapter: 'gemini', baseUrl: 'https://generativelanguage.googleapis.com/v1beta', model: 'gemini-3-flash-preview', apiKey: '', enabled: true },
  { id: 'deepseek', name: 'DeepSeek', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://api.deepseek.com', model: 'deepseek-chat', apiKey: '', enabled: true },
  { id: 'qwen', name: 'Alibaba Qwen / DashScope', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1', model: 'qwen-plus', apiKey: '', enabled: true },
  { id: 'kimi', name: 'Moonshot Kimi', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://api.moonshot.ai/v1', model: 'kimi-latest', apiKey: '', enabled: true },
  { id: 'zhipu', name: 'Zhipu / BigModel / Z.AI', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://open.bigmodel.cn/api/paas/v4', model: 'glm-4.6', apiKey: '', enabled: true },
  { id: 'baidu', name: 'Baidu Qianfan', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://qianfan.baidubce.com/v2', model: 'ernie-4.5-turbo', apiKey: '', enabled: true },
  { id: 'minimax', name: 'MiniMax', region: 'Китай', adapter: 'openai-compatible', baseUrl: 'https://api.minimax.io/v1', model: 'MiniMax-M2', apiKey: '', enabled: true },
  { id: 'mistral', name: 'Mistral AI', region: 'ЕС', adapter: 'openai-compatible', baseUrl: 'https://api.mistral.ai/v1', model: 'mistral-large-latest', apiKey: '', enabled: true },
  { id: 'groq', name: 'Groq', region: 'США', adapter: 'openai-compatible', baseUrl: 'https://api.groq.com/openai/v1', model: 'llama-3.3-70b-versatile', apiKey: '', enabled: true },
  { id: 'openrouter', name: 'OpenRouter', region: 'агрегатор', adapter: 'openai-compatible', baseUrl: 'https://openrouter.ai/api/v1', model: 'anthropic/claude-sonnet-4.5', apiKey: '', enabled: true },
  { id: 'ollama', name: 'Ollama локально', region: 'локально', adapter: 'openai-compatible', baseUrl: 'http://localhost:11434/v1', model: 'qwen2.5-coder:7b', apiKey: 'local', enabled: true }
];

function defaultState() {
  return {
    mainPrompt: DEFAULT_MAIN_PROMPT,
    providers: DEFAULT_PROVIDERS,
    shared: {
      selectedProviderId: 'deepseek',
      defaultAuthor: 'Фамилия И.О.',
      extraRules: 'Соблюдать официальный деловой стиль. Не добавлять лишние блоки. Классификация только: технологическая или конструктивная.',
      rows: [
        { id: rid(), selected: true, source: 'Не указан способ крепления кронштейна после доработки панели. Просим уточнить.', author: 'Иванов И.И.', result: '', status: 'draft', error: '' },
        { id: rid(), selected: true, source: 'По чертежу размер отверстия не соответствует фактическому расположению закладной. Нужно исправить.', author: 'Петров П.П.', result: '', status: 'draft', error: '' }
      ],
      updatedAt: new Date().toISOString()
    },
    history: []
  };
}

let db = loadDb();

function rid() { return crypto.randomBytes(8).toString('hex'); }
function normalizeBaseUrl(url) { return String(url || '').trim().replace(/\/$/, ''); }
function loadDb() {
  try {
    if (fs.existsSync(DATA_FILE)) {
      const parsed = JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
      if (!Array.isArray(parsed.providers)) parsed.providers = DEFAULT_PROVIDERS;
      if (!parsed.shared) parsed.shared = defaultState().shared;
      if (!Array.isArray(parsed.history)) parsed.history = [];
      if (typeof parsed.mainPrompt !== 'string' || !parsed.mainPrompt.trim()) parsed.mainPrompt = DEFAULT_MAIN_PROMPT;
      return parsed;
    }
  } catch (error) {
    console.error('Cannot read server-data.json:', error);
  }
  const fresh = defaultState();
  saveDb(fresh);
  return fresh;
}
function saveDb(data = db) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf8');
}
function sanitizeProvider(p) {
  const { apiKey, ...rest } = p;
  return { ...rest, keySaved: Boolean(apiKey) };
}
function sanitizeProviders() { return db.providers.map(sanitizeProvider); }
function isAdmin(req) {
  const token = req.headers['x-admin-token'];
  const record = token && sessions.get(token);
  if (!record) return false;
  if (Date.now() - record.createdAt > 12 * 60 * 60 * 1000) {
    sessions.delete(token);
    return false;
  }
  return true;
}
function sendJson(res, code, data) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(data));
}
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let raw = '';
    req.on('data', chunk => {
      raw += chunk;
      if (raw.length > 15 * 1024 * 1024) {
        reject(new Error('Слишком большой запрос'));
        req.destroy();
      }
    });
    req.on('end', () => {
      if (!raw) return resolve({});
      try { resolve(JSON.parse(raw)); } catch (e) { reject(new Error('Некорректный JSON')); }
    });
  });
}
function broadcast(type, payload) {
  const message = `event: ${type}\ndata: ${JSON.stringify(payload)}\n\n`;
  for (const res of sseClients) {
    try { res.write(message); } catch { sseClients.delete(res); }
  }
}
function addHistory(entry) {
  db.history.unshift({ id: rid(), at: new Date().toISOString(), ...entry });
  db.history = db.history.slice(0, 200);
  saveDb();
  broadcast('history', db.history);
}
function buildSystemPrompt(mainPrompt = DEFAULT_MAIN_PROMPT, extraRules = '') {
  const basePrompt = String(mainPrompt || DEFAULT_MAIN_PROMPT).trim();
  const rules = String(extraRules || '').trim();
  return `${basePrompt}${rules ? `

Дополнительные правила пользователя:
${rules}` : ''}`;
}
function buildUserPrompt(question, author) {
  return `Исходный вопрос из журнала КТО:\n${question}\n\nФамилия и инициалы автора вопроса:\n${author || 'Фамилия И.О.'}\n\nПереформулируй вопрос по заданному шаблону.`;
}
async function callAiProvider(provider, question, author, mainPrompt, extraRules) {
  if (!provider) throw new Error('Провайдер не найден');
  if (!provider.enabled) throw new Error('Провайдер отключен администратором');
  if (!provider.apiKey && provider.id !== 'ollama') throw new Error('Для выбранного провайдера администратор не сохранил API-ключ');
  const systemPrompt = buildSystemPrompt(mainPrompt, extraRules);
  const userPrompt = buildUserPrompt(question, author);
  const temperature = 0.2;
  const maxTokens = 1400;

  if (provider.adapter === 'anthropic') {
    const r = await fetch(`${normalizeBaseUrl(provider.baseUrl)}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'x-api-key': provider.apiKey, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({ model: provider.model, max_tokens: maxTokens, temperature, system: systemPrompt, messages: [{ role: 'user', content: userPrompt }] })
    });
    if (!r.ok) throw new Error(`Anthropic ${r.status}: ${(await r.text()).slice(0, 700)}`);
    const data = await r.json();
    return data?.content?.map(x => x.text || '').join('\n').trim() || JSON.stringify(data);
  }

  if (provider.adapter === 'gemini') {
    const r = await fetch(`${normalizeBaseUrl(provider.baseUrl)}/models/${encodeURIComponent(provider.model)}:generateContent?key=${encodeURIComponent(provider.apiKey)}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemPrompt }] },
        contents: [{ role: 'user', parts: [{ text: userPrompt }] }],
        generationConfig: { temperature, maxOutputTokens: maxTokens }
      })
    });
    if (!r.ok) throw new Error(`Gemini ${r.status}: ${(await r.text()).slice(0, 700)}`);
    const data = await r.json();
    return data?.candidates?.[0]?.content?.parts?.map(x => x.text || '').join('\n').trim() || JSON.stringify(data);
  }

  const r = await fetch(`${normalizeBaseUrl(provider.baseUrl)}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${provider.apiKey || 'local'}`,
      ...(provider.id === 'openrouter' ? { 'HTTP-Referer': `http://localhost:${PORT}`, 'X-Title': 'KTO AI Rewriter' } : {})
    },
    body: JSON.stringify({
      model: provider.model,
      temperature,
      max_tokens: maxTokens,
      messages: [{ role: 'system', content: systemPrompt }, { role: 'user', content: userPrompt }]
    })
  });
  if (!r.ok) throw new Error(`OpenAI-compatible ${r.status}: ${(await r.text()).slice(0, 700)}`);
  const data = await r.json();
  return data?.choices?.[0]?.message?.content?.trim() || data?.output_text || JSON.stringify(data);
}


function getNetworkInfo(req) {
  const hostHeader = req && req.headers && req.headers.host ? String(req.headers.host).split(':')[0] : 'localhost';
  const urls = [];
  const add = (label, host) => {
    const url = `http://${host}:${PORT}`;
    if (!urls.some(x => x.url === url)) urls.push({ label, host, url });
  };
  add('Этот компьютер', 'localhost');
  if (hostHeader && hostHeader !== 'localhost' && hostHeader !== '127.0.0.1') add('Открытая ссылка', hostHeader);
  const nets = os.networkInterfaces();
  for (const [name, items] of Object.entries(nets)) {
    for (const ni of items || []) {
      if (ni.family !== 'IPv4' || ni.internal) continue;
      if (!ni.address || ni.address.startsWith('169.254.')) continue;
      if (/virtual|vmware|hyper-v|loopback|docker|wsl|vbox/i.test(name)) continue;
      add(name, ni.address);
    }
  }
  return { port: PORT, urls, primaryUrl: (urls.find(x => x.host !== 'localhost') || urls[0] || { url: `http://localhost:${PORT}` }).url };
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  try {
    if (url.pathname === '/api/events') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        Connection: 'keep-alive'
      });
      res.write(`event: hello\ndata: ${JSON.stringify({ ok: true })}\n\n`);
      res.write(`event: state\ndata: ${JSON.stringify(db.shared)}\n\n`);
      res.write(`event: providers\ndata: ${JSON.stringify(sanitizeProviders())}\n\n`);
      res.write(`event: history\ndata: ${JSON.stringify(db.history)}\n\n`);
      sseClients.add(res);
      req.on('close', () => sseClients.delete(res));
      return;
    }

    if (url.pathname === '/api/providers' && req.method === 'GET') return sendJson(res, 200, { providers: sanitizeProviders() });
    if (url.pathname === '/api/network-info' && req.method === 'GET') return sendJson(res, 200, getNetworkInfo(req));

    if (url.pathname === '/api/state' && req.method === 'GET') return sendJson(res, 200, db.shared);
    if (url.pathname === '/api/history' && req.method === 'GET') return sendJson(res, 200, { history: db.history });

    if (url.pathname === '/api/state' && req.method === 'POST') {
      const body = await parseBody(req);
      db.shared = { ...db.shared, ...body, updatedAt: new Date().toISOString() };
      saveDb();
      broadcast('state', db.shared);
      return sendJson(res, 200, { ok: true, state: db.shared });
    }

    if (url.pathname === '/api/history' && req.method === 'POST') {
      const body = await parseBody(req);
      addHistory(body);
      return sendJson(res, 200, { ok: true });
    }

    if (url.pathname === '/api/rewrite' && req.method === 'POST') {
      const body = await parseBody(req);
      const provider = db.providers.find(p => p.id === body.providerId) || db.providers[0];
      const text = await callAiProvider(provider, body.question, body.author, db.mainPrompt, body.extraRules || db.shared.extraRules);
      addHistory({ type: 'rewrite', providerId: provider.id, providerName: provider.name, question: body.question, author: body.author, result: text });
      return sendJson(res, 200, { text });
    }

    if (url.pathname === '/api/admin/login' && req.method === 'POST') {
      const body = await parseBody(req);
      if (body.password !== ADMIN_PASSWORD) return sendJson(res, 403, { error: 'Неверный пароль администратора' });
      const token = crypto.randomBytes(32).toString('hex');
      sessions.set(token, { createdAt: Date.now() });
      return sendJson(res, 200, { ok: true, token });
    }


    if (url.pathname === '/api/admin/prompt' && req.method === 'GET') {
      if (!isAdmin(req)) return sendJson(res, 403, { error: 'Требуется режим администратора' });
      return sendJson(res, 200, { mainPrompt: db.mainPrompt || DEFAULT_MAIN_PROMPT, defaultMainPrompt: DEFAULT_MAIN_PROMPT });
    }

    if (url.pathname === '/api/admin/prompt' && req.method === 'POST') {
      if (!isAdmin(req)) return sendJson(res, 403, { error: 'Требуется режим администратора' });
      const body = await parseBody(req);
      if (body.reset === true) {
        db.mainPrompt = DEFAULT_MAIN_PROMPT;
      } else if (typeof body.mainPrompt === 'string' && body.mainPrompt.trim()) {
        db.mainPrompt = body.mainPrompt.trim();
      } else {
        return sendJson(res, 400, { error: 'mainPrompt должен быть непустой строкой' });
      }
      saveDb();
      addHistory({ type: 'settings', providerName: 'Администратор', question: 'Изменен основной промпт редактора', result: 'Основной промпт сохранен на сервере.' });
      return sendJson(res, 200, { ok: true, mainPrompt: db.mainPrompt, defaultMainPrompt: DEFAULT_MAIN_PROMPT });
    }

    if (url.pathname === '/api/admin/providers' && req.method === 'GET') {
      if (!isAdmin(req)) return sendJson(res, 403, { error: 'Требуется режим администратора' });
      return sendJson(res, 200, { providers: db.providers });
    }

    if (url.pathname === '/api/admin/providers' && req.method === 'POST') {
      if (!isAdmin(req)) return sendJson(res, 403, { error: 'Требуется режим администратора' });
      const body = await parseBody(req);
      if (!Array.isArray(body.providers)) return sendJson(res, 400, { error: 'providers должен быть массивом' });
      db.providers = body.providers.map(p => ({
        id: p.id || rid(),
        name: p.name || 'Новый сервис',
        region: p.region || 'дополнительный',
        adapter: p.adapter || 'openai-compatible',
        baseUrl: p.baseUrl || '',
        model: p.model || '',
        apiKey: p.apiKey || '',
        enabled: p.enabled !== false
      }));
      saveDb();
      broadcast('providers', sanitizeProviders());
      return sendJson(res, 200, { ok: true, providers: db.providers });
    }

    if (req.method === 'GET' && (url.pathname === '/' || url.pathname === '/index.html')) {
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(fs.readFileSync(INDEX_FILE, 'utf8'));
      return;
    }

    sendJson(res, 404, { error: 'Not found' });
  } catch (error) {
    console.error(error);
    sendJson(res, 500, { error: error.message || 'Server error' });
  }
});

function startServer(callback) {
  const HOST = process.env.HOST || '0.0.0.0';
  if (server.listening) { if (callback) callback(); return server; }
  server.listen(PORT, HOST, () => {
    console.log(`ЖКТО AI-редактор запущен: http://localhost:${PORT}`);
    console.log(`Гостевая ссылка для локальной сети будет показана в приложении.`);
    console.log(`Пароль администратора по умолчанию: ${ADMIN_PASSWORD === 'admin123' ? 'admin123 (смените ADMIN_PASSWORD)' : 'задан через ADMIN_PASSWORD'}`);
    if (callback) callback();
  });
  return server;
}

if (require.main === module) startServer();

module.exports = { startServer, server, PORT, getNetworkInfo };
