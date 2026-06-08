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

using System.Drawing;
using System.Windows.Forms;

namespace KdCatalog;

public sealed class MainForm : Form
{
    private readonly AppConfig _config = AppConfig.Load();
    private readonly ApiClient _apiClient = new();
    private readonly PortableHost? _host;
    private readonly DataGridView _catalogGrid = new();
    private readonly Panel _toolbar = new();
    private readonly Panel _bottomPanel = new();
    private readonly Label _selectedLabel = new();
    private readonly Label _aiInsightLabel = new();
    private CatalogRowDto? _selected;

    public MainForm()
    {
        Text = "CD & AI Catalog";
        Width = 1400;
        Height = 900;
        KeyPreview = true;
        InitializeToolbar();
        InitializeGrid();
        InitializeBottomPanels();
        ApplyRoleVisibility();
        KeyDown += OnKeyDown;

        if (_config.Mode == "server")
        {
            _host = new PortableHost();
            _host.StartServer(_config.CatalogUnc);
        }
        _apiClient.Configure(_config.ServerUrl);
    }

    private void InitializeToolbar()
    {
        _toolbar.Dock = DockStyle.Top;
        _toolbar.Height = 48;
        _toolbar.Padding = new Padding(8);
        AddButton("Поиск", (_, _) => ShowSearch());
        AddButton("Настройки", (_, _) => ShowSettings());
        AddButton("Авторизация", (_, _) => ShowLogin());
        AddButton("Пользователи", "btnUsers", (_, _) => new UsersForm(_apiClient).ShowDialog());
        AddButton("ИИ-провайдеры", "btnAiProviders", (_, _) => new ProvidersForm(_apiClient).ShowDialog());
        AddButton("Экспорт в Excel", (_, _) => _ = _apiClient.ExportCatalogAsync());
        AddButton("Разбор INBOX", "btnInbox", (_, _) => _ = _apiClient.ProcessInboxAsync());
        AddButton("Вид", (_, _) => ShowViewSettings());
        Controls.Add(_toolbar);
    }

    private void AddButton(string text, EventHandler onClick) => AddButton(text, null, onClick);

    private void AddButton(string text, string? name, EventHandler onClick)
    {
        var btn = new Button { Text = text, AutoSize = true, Margin = new Padding(4) };
        if (!string.IsNullOrEmpty(name)) btn.Name = name;
        btn.Click += onClick;
        _toolbar.Controls.Add(btn);
    }

    private void InitializeGrid()
    {
        var tablePanel = new Panel { Dock = DockStyle.Fill };
        _catalogGrid.Dock = DockStyle.Fill;
        _catalogGrid.ReadOnly = true;
        _catalogGrid.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
        _catalogGrid.Columns.Add("doc_number", "Обозначение");
        _catalogGrid.Columns.Add("name", "Наименование");
        _catalogGrid.Columns.Add("product_number", "Изделие");
        _catalogGrid.Columns.Add("ai_status", "Статус ИИ");
        _catalogGrid.Columns.Add("status", "Статус");
        _catalogGrid.SelectionChanged += (_, _) => OnSelectionChanged();
        _catalogGrid.CellDoubleClick += (_, _) => OpenRecordCard();
        tablePanel.Controls.Add(_catalogGrid);
        Controls.Add(tablePanel);
    }

    private void InitializeBottomPanels()
    {
        _bottomPanel.Dock = DockStyle.Bottom;
        _bottomPanel.Height = 140;
        var split = new SplitContainer { Dock = DockStyle.Fill, Orientation = Orientation.Vertical };
        var left = new GroupBox { Text = "Модуль КД", Dock = DockStyle.Fill, Padding = new Padding(8) };
        _selectedLabel.Dock = DockStyle.Top;
        _selectedLabel.Height = 24;
        var openBtn = new Button { Text = "Открыть файл", Width = 120 };
        openBtn.Click += async (_, _) => await OpenPdfPreviewAsync();
        var analyzeBtn = new Button { Text = "Анализ ИИ", Width = 120, Left = 130 };
        analyzeBtn.Click += async (_, _) => await RunAiAnalyzeAsync();
        left.Controls.Add(analyzeBtn);
        left.Controls.Add(openBtn);
        left.Controls.Add(_selectedLabel);
        var right = new GroupBox { Text = "ИИ-помощник", Dock = DockStyle.Fill, Padding = new Padding(8) };
        _aiInsightLabel.Dock = DockStyle.Fill;
        right.Controls.Add(_aiInsightLabel);
        split.Panel1.Controls.Add(left);
        split.Panel2.Controls.Add(right);
        _bottomPanel.Controls.Add(split);
        Controls.Add(_bottomPanel);
    }

    private void OnSelectionChanged()
    {
        if (_catalogGrid.CurrentRow?.Index < 0) return;
        var idx = _catalogGrid.CurrentRow!.Index;
        if (idx >= _rows.Count) return;
        _selected = _rows[idx];
        _selectedLabel.Text = $"Selected: {_selected.Name}";
        _aiInsightLabel.Text = $"ИИ: {_selected.AiInsight ?? _selected.AiStatus?.Label ?? "—"}";
    }

    private List<CatalogRowDto> _rows = new();

    private async Task LoadCatalogAsync(string? docNumber = null, string? name = null)
    {
        _rows = (await _apiClient.GetCatalogAsync(docNumber, name)).ToList();
        _catalogGrid.Rows.Clear();
        foreach (var row in _rows)
        {
            _catalogGrid.Rows.Add(row.DocNumber, row.Name, row.ProductNumber, row.AiStatus?.Label ?? "—", row.Status);
        }
    }

    private void ApplyRoleVisibility()
    {
        SetVisible("btnUsers", _apiClient.CurrentRole is "admin" or "moderator");
        SetVisible("btnAiProviders", _apiClient.CurrentRole == "admin");
        SetVisible("btnInbox", _apiClient.CurrentRole is "admin" or "moderator");
    }

    private void SetVisible(string name, bool visible)
    {
        var control = _toolbar.Controls.Find(name, false).FirstOrDefault();
        if (control is not null) control.Visible = visible;
    }

    private async void ShowLogin()
    {
        var login = Microsoft.VisualBasic.Interaction.InputBox("Логин", "Авторизация");
        var password = Microsoft.VisualBasic.Interaction.InputBox("Пароль", "Авторизация");
        if (string.IsNullOrWhiteSpace(login)) return;
        await _apiClient.LoginAsync(login, password);
        ApplyRoleVisibility();
        await LoadCatalogAsync();
    }

    private void ShowSettings()
    {
        using var form = new Form { Text = "Настройки → Подключение", Width = 420, Height = 280 };
        var modeBox = new ComboBox { Dock = DockStyle.Top, Items = { "server", "client" }, Text = _config.Mode };
        var serverBox = new TextBox { Dock = DockStyle.Top, Text = _config.ServerUrl };
        var uncBox = new TextBox { Dock = DockStyle.Top, Text = _config.CatalogUnc };
        var saveBtn = new Button { Text = "Сохранить", Dock = DockStyle.Bottom };
        saveBtn.Click += (_, _) =>
        {
            _config.Mode = modeBox.Text;
            _config.ServerUrl = serverBox.Text;
            _config.CatalogUnc = uncBox.Text;
            _config.Save();
            _apiClient.Configure(_config.ServerUrl);
            form.Close();
        };
        form.Controls.AddRange(new Control[] { saveBtn, uncBox, serverBox, modeBox });
        form.ShowDialog();
    }

    private void ShowViewSettings()
    {
        using var form = new Form { Text = "Вид", Width = 320, Height = 200 };
        var theme = new ComboBox { Items = { "system", "light", "dark" }, Text = _config.Theme, Dock = DockStyle.Top };
        var save = new Button { Text = "Сохранить", Dock = DockStyle.Bottom };
        save.Click += (_, _) => { _config.Theme = theme.Text; _config.Save(); form.Close(); };
        form.Controls.AddRange(new Control[] { save, theme });
        form.ShowDialog();
    }

    private async void ShowSearch()
    {
        using var dlg = new SearchDialog();
        if (dlg.ShowDialog() != DialogResult.OK) return;
        await LoadCatalogAsync(dlg.DocNumber, dlg.Name);
    }

    private void OpenRecordCard()
    {
        if (_selected is null) return;
        new RecordCardForm(_apiClient, _selected).ShowDialog();
    }

    private async Task OpenPdfPreviewAsync()
    {
        if (_selected is null) return;
        var temp = Path.Combine(Path.GetTempPath(), $"ced_{_selected.Id}.pdf");
        await _apiClient.OpenDocumentFileAsync(_selected.Id, temp);
        new PdfPreviewForm(temp).ShowDialog();
    }

    private async Task RunAiAnalyzeAsync()
    {
        if (_selected is null) return;
        var text = await _apiClient.AnalyzeDocumentAsync(_selected.Id);
        _aiInsightLabel.Text = $"ИИ: {text}";
        await LoadCatalogAsync();
    }

    private void OnKeyDown(object? sender, KeyEventArgs e)
    {
        if (e.Control && e.KeyCode == Keys.F) ShowSearch();
        else if (e.KeyCode == Keys.F3) OpenRecordCard();
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing) _host?.Dispose();
        base.Dispose(disposing);
    }
}
