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

using System.Windows.Forms;

namespace KdCatalog;

public sealed class FirstRunWizard : Form
{
    public AppConfig Result { get; }

    private readonly ComboBox _mode = new() { Dock = DockStyle.Top, DropDownStyle = ComboBoxStyle.DropDownList };
    private readonly TextBox _serverUrl = new() { Dock = DockStyle.Top };
    private readonly TextBox _catalogUnc = new() { Dock = DockStyle.Top };

    public FirstRunWizard(AppConfig current)
    {
        Text = "Первый запуск KdCatalog";
        Width = 480;
        Height = 280;
        Result = current;
        _mode.Items.AddRange(new object[] { "client", "server" });
        _mode.SelectedItem = string.IsNullOrWhiteSpace(current.Mode) ? "client" : current.Mode;
        _serverUrl.Text = current.ServerUrl;
        _catalogUnc.Text = current.CatalogUnc;
        Controls.Add(new Button { Text = "Сохранить", Dock = DockStyle.Bottom, DialogResult = DialogResult.OK });
        Controls.Add(_catalogUnc);
        Controls.Add(new Label
        {
            Text = "UNC каталога (только режим server; для client оставьте пустым)",
            Dock = DockStyle.Top,
            AutoSize = true,
        });
        Controls.Add(_serverUrl);
        Controls.Add(new Label { Text = "Адрес сервера", Dock = DockStyle.Top });
        Controls.Add(_mode);
        Controls.Add(new Label { Text = "Режим", Dock = DockStyle.Top });
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        if (DialogResult == DialogResult.OK)
        {
            Result.Mode = _mode.SelectedItem?.ToString() ?? "client";
            Result.ServerUrl = _serverUrl.Text;
            Result.CatalogUnc = _catalogUnc.Text;
            Result.Save();
        }
        base.OnFormClosing(e);
    }
}
