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

package ru.nti.sbor.ui.preview

import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import ru.nti.sbor.data.settings.ThemeMode
import ru.nti.sbor.ui.theme.NtiSborTheme

/** Прототип экранов для согласования дизайна (раздел 8 ТЗ). */
@Preview(name = "Главный — светлая", widthDp = 360, heightDp = 640)
@Composable
fun PreviewHomeLight() {
    NtiSborTheme(themeMode = ThemeMode.LIGHT) {
        Surface {
            Text("Главный: список, сводка, поиск, FAB «Добавить»")
        }
    }
}

@Preview(name = "Главный — тёмная", widthDp = 360, heightDp = 640)
@Composable
fun PreviewHomeDark() {
    NtiSborTheme(themeMode = ThemeMode.DARK) {
        Surface {
            Text("Главный (тёмная тема)")
        }
    }
}

@Preview(name = "Форма записи", widthDp = 360, heightDp = 800)
@Composable
fun PreviewRecordForm() {
    NtiSborTheme(themeMode = ThemeMode.LIGHT) {
        Surface {
            Text("Форма: операция, изделие, значение, единица, дата, исполнитель")
        }
    }
}

@Preview(name = "Настройки", widthDp = 360, heightDp = 800)
@Composable
fun PreviewSettings() {
    NtiSborTheme(themeMode = ThemeMode.LIGHT) {
        Surface {
            Text("Настройки: профиль, тема, сервер, экспорт, очистка")
        }
    }
}
