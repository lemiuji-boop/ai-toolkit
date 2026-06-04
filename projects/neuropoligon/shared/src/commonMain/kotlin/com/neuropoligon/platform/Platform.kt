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

public data class PlatformInfo(val isWeb: Boolean = false)

public expect fun isWebPlatform(): Boolean

public interface SecureStorage {
    public suspend fun get(key: String): String?
    public suspend fun set(key: String, value: String)
    public suspend fun remove(key: String)
}

public expect fun createSecureStorage(): SecureStorage

public expect fun openUrl(url: String)

public expect fun copyToClipboard(text: String)
