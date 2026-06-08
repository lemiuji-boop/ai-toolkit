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

public sealed class UsersForm : Form
{
    private readonly ApiClient _api;
    private readonly DataGridView _grid = new() { Dock = DockStyle.Fill, ReadOnly = true };

    public UsersForm(ApiClient api)
    {
        _api = api;
        Text = "Пользователи";
        Width = 700;
        Height = 400;
        Controls.Add(_grid);
        Load += async (_, _) => await ReloadAsync();
    }

    private async Task ReloadAsync()
    {
        var users = await _api.GetUsersAsync();
        _grid.Columns.Clear();
        _grid.Columns.Add("login", "Логин");
        _grid.Columns.Add("role", "Роль");
        _grid.Columns.Add("department", "Отдел");
        foreach (var user in users)
        {
            _grid.Rows.Add(user.Login, user.Role, user.Department ?? "");
        }
    }
}
