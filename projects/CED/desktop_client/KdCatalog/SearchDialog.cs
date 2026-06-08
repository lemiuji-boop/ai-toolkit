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

public sealed class SearchDialog : Form
{
    public string DocNumber => _docNumber.Text;
    public string Name => _name.Text;

    private readonly TextBox _docNumber = new() { Dock = DockStyle.Top };
    private readonly TextBox _name = new() { Dock = DockStyle.Top };

    public SearchDialog()
    {
        Text = "Поиск";
        Width = 400;
        Height = 200;
        Controls.Add(new Button { Text = "OK", Dock = DockStyle.Bottom, DialogResult = DialogResult.OK });
        Controls.Add(_name);
        Controls.Add(_docNumber);
        Controls.Add(new Label { Text = "Наименование", Dock = DockStyle.Top });
        Controls.Add(new Label { Text = "Обозначение", Dock = DockStyle.Top });
    }
}
