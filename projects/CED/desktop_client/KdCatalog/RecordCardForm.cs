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

public sealed class RecordCardForm : Form
{
    public RecordCardForm(ApiClient api, CatalogRowDto row)
    {
        Text = $"Карточка: {row.DocNumber}";
        Width = 800;
        Height = 600;
        var tabs = new TabControl { Dock = DockStyle.Fill };
        var meta = new TabPage("Метаданные");
        meta.Controls.Add(new Label { Dock = DockStyle.Fill, Text = $"{row.Name}\n{row.DocNumber}\nСтатус: {row.Status}" });
        var history = new TabPage("История");
        history.Controls.Add(new TextBox { Dock = DockStyle.Fill, Multiline = true, ReadOnly = true });
        tabs.TabPages.Add(meta);
        tabs.TabPages.Add(history);
        Controls.Add(tabs);
        Shown += async (_, _) =>
        {
            var revisions = await api.GetHistoryAsync(row.Id);
            if (history.Controls[0] is TextBox box)
            {
                box.Text = string.Join(Environment.NewLine, revisions.Select(r => $"{r.Action} @ {r.Timestamp}"));
            }
        };
    }
}
