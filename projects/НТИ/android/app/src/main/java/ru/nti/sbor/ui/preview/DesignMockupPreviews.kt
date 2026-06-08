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

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import ru.nti.sbor.ui.demo.DemoSignoffApp

/** Превью для согласования — делегируют в ui/demo. */

@Preview(name = "01 Главный — светлая 360", group = "signoff", widthDp = 360, heightDp = 780, showBackground = true)
@Composable
fun SignoffHomeLight() = DemoSignoffApp(demoIndex = 1)

@Preview(name = "02 Главный — тёмная 360", group = "signoff", widthDp = 360, heightDp = 780, showBackground = true)
@Composable
fun SignoffHomeDark() = DemoSignoffApp(demoIndex = 2)

@Preview(name = "03 Форма записи — светлая", group = "signoff", widthDp = 360, heightDp = 780, showBackground = true)
@Composable
fun SignoffRecordForm() = DemoSignoffApp(demoIndex = 3)

@Preview(name = "04 Настройки — светлая", group = "signoff", widthDp = 360, heightDp = 780, showBackground = true)
@Composable
fun SignoffSettings() = DemoSignoffApp(demoIndex = 4)

@Preview(name = "05 Главный — шрифт 200%", group = "signoff", widthDp = 360, heightDp = 780, fontScale = 2f, showBackground = true)
@Composable
fun SignoffHomeLargeFont() = DemoSignoffApp(demoIndex = 1)
