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

package com.neuropoligon

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.neuropoligon.di.initKoin
import com.neuropoligon.presentation.navigation.NeuropoligonNavHost
import com.neuropoligon.presentation.theme.NeuropoligonTheme
import org.koin.compose.KoinContext

/**
 * Корневая точка UI приложения.
 */
@Composable
public fun App() {
    KoinContext {
        NeuropoligonTheme {
            Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                NeuropoligonNavHost()
            }
        }
    }
}

public fun initApp() {
    // Koin инициализируется в точке входа платформы (MainActivity, main).
}
