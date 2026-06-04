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

import java.awt.Toolkit
import java.awt.datatransfer.StringSelection
import java.net.URI
import java.util.prefs.Preferences

public actual fun isWebPlatform(): Boolean = false

public actual fun createSecureStorage(): SecureStorage = JvmSecureStorage()

public actual fun openUrl(url: String) {
    val desktop = java.awt.Desktop.getDesktop()
    if (desktop.isSupported(java.awt.Desktop.Action.BROWSE)) {
        desktop.browse(URI(url))
    }
}

public actual fun copyToClipboard(text: String) {
    val selection = StringSelection(text)
    Toolkit.getDefaultToolkit().systemClipboard.setContents(selection, selection)
}

private class JvmSecureStorage : SecureStorage {
    private val prefs = Preferences.userRoot().node("com.neuropoligon.secure")

    override suspend fun get(key: String): String? = prefs.get(key, null)

    override suspend fun set(key: String, value: String) {
        prefs.put(key, value)
        prefs.flush()
    }

    override suspend fun remove(key: String) {
        prefs.remove(key)
        prefs.flush()
    }
}
