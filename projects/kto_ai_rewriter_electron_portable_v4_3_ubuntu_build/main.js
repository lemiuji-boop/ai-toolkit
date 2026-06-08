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

const { app, BrowserWindow, Menu, shell, dialog, clipboard } = require('electron');
const path = require('path');
const fs = require('fs');

const PORT = process.env.PORT || '8787';
process.env.PORT = PORT;
process.env.HOST = process.env.HOST || '0.0.0.0';
process.env.ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

let mainWindow;
let serverApi;

function getDataDir() {
  return process.env.KTO_DATA_DIR || path.join(app.getPath('userData'), 'data');
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1500,
    height: 980,
    minWidth: 1100,
    minHeight: 760,
    title: 'ЖКТО AI-редактор вопросов',
    backgroundColor: '#f3f8fc',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  mainWindow.loadURL(`http://localhost:${PORT}`);

  const menu = Menu.buildFromTemplate([
    {
      label: 'Файл',
      submenu: [
        { label: 'Открыть гостевую ссылку', click: () => shell.openExternal(`http://localhost:${PORT}`) },
        { label: 'Скопировать локальную ссылку', click: () => clipboard.writeText(`http://localhost:${PORT}`) },
        { type: 'separator' },
        { label: 'Выход', role: 'quit' }
      ]
    },
    {
      label: 'Помощь',
      submenu: [
        { label: 'Показать папку данных', click: () => shell.openPath(getDataDir()) },
        { label: 'О приложении', click: () => dialog.showMessageBox(mainWindow, { type: 'info', title: 'ЖКТО AI-редактор', message: 'ЖКТО AI-редактор вопросов', detail: `Сервер: http://localhost:${PORT}\nГости заходят по IP-адресу ПК администратора.` }) }
      ]
    }
  ]);
  Menu.setApplicationMenu(menu);
}

const gotLock = app.requestSingleInstanceLock();
if (!gotLock) {
  app.quit();
} else {
app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});


app.whenReady().then(() => {
  const dataDir = getDataDir();
  fs.mkdirSync(dataDir, { recursive: true });
  process.env.KTO_DATA_DIR = dataDir;
  process.env.KTO_INDEX_FILE = path.join(__dirname, 'index.html');

  serverApi = require('./server');
  serverApi.startServer(() => createWindow());
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
}
