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

import platform.Foundation.NSUserDefaults
import platform.UIKit.UIPasteboard
import platform.UIKit.UIApplication
import platform.Foundation.NSURL

public actual fun isWebPlatform(): Boolean = false

public actual fun createSecureStorage(): SecureStorage = IosSecureStorage()

public actual fun openUrl(url: String) {
    val nsUrl = NSURL.URLWithString(url) ?: return
    UIApplication.sharedApplication.openURL(nsUrl)
}

public actual fun copyToClipboard(text: String) {
    UIPasteboard.generalPasteboard.string = text
}

private class IosSecureStorage : SecureStorage {
    private val defaults = NSUserDefaults.standardUserDefaults

    override suspend fun get(key: String): String? = defaults.stringForKey(key)

    override suspend fun set(key: String, value: String) {
        defaults.setObject(value, key)
    }

    override suspend fun remove(key: String) {
        defaults.removeObjectForKey(key)
    }
}
