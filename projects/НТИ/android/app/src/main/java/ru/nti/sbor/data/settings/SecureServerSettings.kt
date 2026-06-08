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

package ru.nti.sbor.data.settings

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/** Хранение URL, сессии и токена доступа (SEC-004). */
class SecureServerSettings(context: Context) {
    private val prefs = EncryptedSharedPreferences.create(
        context,
        "nti_secure_server",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    fun getServerUrl(): String = prefs.getString(KEY_URL, "") ?: ""

    fun getAccessToken(): String = prefs.getString(KEY_TOKEN, "") ?: ""

    /** @deprecated Используйте getAccessToken; оставлено для совместимости. */
    fun getToken(): String = getAccessToken()

    fun getUsername(): String = prefs.getString(KEY_USERNAME, "") ?: ""

    fun getDisplayName(): String = prefs.getString(KEY_DISPLAY_NAME, "") ?: ""

    fun isLoggedIn(): Boolean = getAccessToken().isNotBlank()

    /** Сохраняет URL API из сборки, если ещё не задан. */
    fun ensureServerUrl(url: String) {
        if (getServerUrl().isBlank()) {
            prefs.edit().putString(KEY_URL, url.trim()).apply()
        }
    }

    fun saveServerUrl(url: String) {
        prefs.edit().putString(KEY_URL, url.trim()).apply()
    }

    fun saveSession(
        serverUrl: String,
        accessToken: String,
        username: String,
        displayName: String,
    ) {
        prefs.edit()
            .putString(KEY_URL, serverUrl.trim())
            .putString(KEY_TOKEN, accessToken.trim())
            .putString(KEY_USERNAME, username.trim())
            .putString(KEY_DISPLAY_NAME, displayName.trim())
            .apply()
    }

    fun save(serverUrl: String, token: String) {
        saveSession(serverUrl, token, getUsername(), getDisplayName())
    }

    fun clear() {
        prefs.edit().clear().apply()
    }

    fun clearSession() {
        prefs.edit()
            .remove(KEY_TOKEN)
            .remove(KEY_USERNAME)
            .remove(KEY_DISPLAY_NAME)
            .apply()
    }

    fun bearerHeader(): String? {
        val token = getAccessToken()
        return if (token.isBlank()) null else "Bearer $token"
    }

    companion object {
        private const val KEY_URL = "server_url"
        private const val KEY_TOKEN = "access_token"
        private const val KEY_USERNAME = "username"
        private const val KEY_DISPLAY_NAME = "display_name"
    }
}
