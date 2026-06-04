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

package com.neuropoligon.platform

import kotlinx.browser.window
import org.w3c.dom.Storage

public actual fun isWebPlatform(): Boolean = true

public actual fun createSecureStorage(): SecureStorage = WebSecureStorage()

public actual fun openUrl(url: String) {
    window.open(url, "_blank")
}

public actual fun copyToClipboard(text: String) {
    window.navigator.clipboard?.writeText(text)
}

private class WebSecureStorage : SecureStorage {
    private val storage: Storage? = window.sessionStorage

    override suspend fun get(key: String): String? = storage?.getItem(key)

    override suspend fun set(key: String, value: String) {
        storage?.setItem(key, value)
    }

    override suspend fun remove(key: String) {
        storage?.removeItem(key)
    }
}
