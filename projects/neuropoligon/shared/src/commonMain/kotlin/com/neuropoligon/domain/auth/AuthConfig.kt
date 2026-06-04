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

package com.neuropoligon.domain.auth

/** Заголовок клиента: мобильное приложение (админ-вход запрещён). */
public const val AUTH_CLIENT_HEADER: String = "X-Neuropoligon-Client"
public const val AUTH_CLIENT_ANDROID: String = "android"
public const val AUTH_CLIENT_WEB_ADMIN: String = "web-admin"

/**
 * URL backend авторизации. Для эмулятора Android: http://10.0.2.2:8080
 * Для устройства в LAN: http://IP_ПК:8080
 */
/** Эмулятор Android → хост ПК. На телефоне укажите http://IP_ПК:8080 в настройках. */
public const val DEFAULT_AUTH_API_BASE_URL: String = "http://10.0.2.2:8080"

public const val AUTH_API_BASE_URL_KEY: String = "auth_api_base_url"
