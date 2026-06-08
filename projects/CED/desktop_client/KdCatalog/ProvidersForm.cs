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

using System.Text.Json.Serialization;

namespace KdCatalog;

public sealed class ProvidersForm : Form
{
    private readonly ApiClient _api;
    private readonly DataGridView _grid = new();
    private readonly TextBox _nameBox = new() { Dock = DockStyle.Top };
    private readonly ComboBox _typeBox = new() { Dock = DockStyle.Top, Items = { "local", "external" } };
    private readonly TextBox _urlBox = new() { Dock = DockStyle.Top };
    private readonly TextBox _modelBox = new() { Dock = DockStyle.Top };
    private readonly CheckBox _activeBox = new() { Text = "Активен", Dock = DockStyle.Top };
    private int? _editId;

    public ProvidersForm(ApiClient api)
    {
        _api = api;
        Text = "ИИ-провайдеры";
        Width = 720;
        Height = 520;

        _grid.Dock = DockStyle.Fill;
        _grid.ReadOnly = true;
        _grid.Columns.Add("name", "Имя");
        _grid.Columns.Add("provider_type", "Тип");
        _grid.Columns.Add("base_url", "URL");
        _grid.Columns.Add("model_name", "Модель");
        _grid.Columns.Add("is_active", "Активен");
        _grid.CellDoubleClick += (_, _) => LoadSelected();

        var panel = new Panel { Dock = DockStyle.Bottom, Height = 200, Padding = new Padding(8) };
        _nameBox.PlaceholderText = "Имя";
        _urlBox.PlaceholderText = "Base URL";
        _modelBox.PlaceholderText = "Модель";
        _typeBox.SelectedIndex = 0;
        var saveBtn = new Button { Text = "Сохранить", Dock = DockStyle.Bottom };
        saveBtn.Click += async (_, _) => await SaveAsync();
        panel.Controls.Add(saveBtn);
        panel.Controls.Add(_activeBox);
        panel.Controls.Add(_modelBox);
        panel.Controls.Add(_urlBox);
        panel.Controls.Add(_typeBox);
        panel.Controls.Add(_nameBox);

        Controls.Add(_grid);
        Controls.Add(panel);
        Load += async (_, _) => await ReloadAsync();
    }

    private async Task ReloadAsync()
    {
        _grid.Rows.Clear();
        foreach (var row in await _api.GetProvidersAsync())
        {
            _grid.Rows.Add(row.Name, row.ProviderType, row.BaseUrl, row.ModelName, row.IsActive ? "Да" : "Нет");
            _grid.Rows[^1].Tag = row.Id;
        }
    }

    private void LoadSelected()
    {
        if (_grid.CurrentRow?.Tag is not int id) return;
        _editId = id;
        _nameBox.Text = _grid.CurrentRow.Cells[0].Value?.ToString() ?? "";
        _typeBox.Text = _grid.CurrentRow.Cells[1].Value?.ToString() ?? "local";
        _urlBox.Text = _grid.CurrentRow.Cells[2].Value?.ToString() ?? "";
        _modelBox.Text = _grid.CurrentRow.Cells[3].Value?.ToString() ?? "";
        _activeBox.Checked = _grid.CurrentRow.Cells[4].Value?.ToString() == "Да";
    }

    private async Task SaveAsync()
    {
        var payload = new ProviderPayloadDto(
            _nameBox.Text,
            _typeBox.Text,
            _urlBox.Text,
            _modelBox.Text,
            _activeBox.Checked,
            null);
        if (_editId.HasValue)
            await _api.UpdateProviderAsync(_editId.Value, payload);
        else
            await _api.CreateProviderAsync(payload);
        _editId = null;
        await ReloadAsync();
    }
}

public sealed record ProviderPayloadDto(
    string Name,
    [property: JsonPropertyName("provider_type")] string ProviderType,
    [property: JsonPropertyName("base_url")] string BaseUrl,
    [property: JsonPropertyName("model_name")] string? ModelName,
    [property: JsonPropertyName("is_active")] bool IsActive,
    [property: JsonPropertyName("api_key")] string? ApiKey);

public sealed class ProviderRowDto
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    [JsonPropertyName("name")]
    public string Name { get; set; } = "";
    [JsonPropertyName("provider_type")]
    public string ProviderType { get; set; } = "";
    [JsonPropertyName("base_url")]
    public string BaseUrl { get; set; } = "";
    [JsonPropertyName("model_name")]
    public string? ModelName { get; set; }
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; }
}
