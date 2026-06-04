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

import kotlinx.coroutines.flow.Flow

public data class AuthUser(
    val id: String,
    val email: String,
)

public sealed class AuthState {
    public data object Guest : AuthState()
    public data class Authenticated(val user: AuthUser) : AuthState()
    public data class PendingVerification(val email: String) : AuthState()
}

public interface AuthService {
    public val currentUser: Flow<AuthState>
    public suspend fun signUpWithEmail(email: String, password: String): Result<Unit>
    public suspend fun signInWithEmail(email: String, password: String): Result<Unit>
    public suspend fun sendMagicLink(email: String): Result<Unit>
    public suspend fun verifyOtp(email: String, token: String): Result<Unit>
    public suspend fun signOut()
    public fun isConfigured(): Boolean
}
