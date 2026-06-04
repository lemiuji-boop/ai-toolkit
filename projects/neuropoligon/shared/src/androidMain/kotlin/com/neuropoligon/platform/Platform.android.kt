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

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.core.content.ContextCompat
import org.koin.java.KoinJavaComponent.getKoin

public actual fun isWebPlatform(): Boolean = false

public actual fun createSecureStorage(): SecureStorage = AndroidSecureStorage(
    getKoin().get<Context>(),
)

public actual fun openUrl(url: String) {
    val context = getKoin().get<Context>()
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    ContextCompat.startActivity(context, intent, null)
}

public actual fun copyToClipboard(text: String) {
    val context = getKoin().get<Context>()
    val manager = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    manager.setPrimaryClip(ClipData.newPlainText("neuropoligon", text))
}

private class AndroidSecureStorage(
    private val context: Context,
) : SecureStorage {
    private val prefs = context.getSharedPreferences("neuropoligon_secure", Context.MODE_PRIVATE)

    override suspend fun get(key: String): String? = prefs.getString(key, null)

    override suspend fun set(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    override suspend fun remove(key: String) {
        prefs.edit().remove(key).apply()
    }
}
