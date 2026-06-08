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

import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.ksp)
}

fun resolveApiBaseUrl(): String {
    val localFile = rootProject.file("local.properties")
    if (localFile.exists()) {
        val props = Properties()
        localFile.inputStream().use { props.load(it) }
        val fromLocal = props.getProperty("ntiApiBaseUrl")?.trim().orEmpty()
        if (fromLocal.isNotEmpty()) {
            return if (fromLocal.endsWith("/")) fromLocal else "$fromLocal/"
        }
    }
    val fromGradle = (project.findProperty("ntiApiBaseUrl") as String?)?.trim().orEmpty()
    if (fromGradle.isNotEmpty()) {
        return if (fromGradle.endsWith("/")) fromGradle else "$fromGradle/"
    }
    return "http://10.0.2.2:8010/"
}

val apiBaseUrl: String = resolveApiBaseUrl()

android {
    namespace = "ru.nti.sbor"
    compileSdk = 35

    defaultConfig {
        applicationId = "ru.nti.sbor"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables.useSupportLibrary = true
        buildConfigField("int", "DEMO_INDEX", "0")
        buildConfigField("Boolean", "CERT_PINNING_ENABLED", "false")
        buildConfigField("String", "API_BASE_URL", "\"$apiBaseUrl\"")
    }

    // 4 демо-сборки для согласования макетов (параллельная установка на одном устройстве)
    flavorDimensions += "demo"
    productFlavors {
        create("v1") {
            dimension = "demo"
            applicationIdSuffix = ".demo1"
            versionCode = 121
            versionName = "1.2.1"
            resValue("string", "app_name", "НТИ.Сбор 1")
            buildConfigField("int", "DEMO_INDEX", "1")
        }
        create("v2") {
            dimension = "demo"
            applicationIdSuffix = ".demo2"
            versionCode = 122
            versionName = "1.2.2"
            resValue("string", "app_name", "НТИ.Сбор 2")
            buildConfigField("int", "DEMO_INDEX", "2")
        }
        create("v3") {
            dimension = "demo"
            applicationIdSuffix = ".demo3"
            versionCode = 123
            versionName = "1.2.3"
            resValue("string", "app_name", "НТИ.Сбор 3")
            buildConfigField("int", "DEMO_INDEX", "3")
        }
        create("v4") {
            dimension = "demo"
            applicationIdSuffix = ".demo4"
            versionCode = 124
            versionName = "1.2.4"
            resValue("string", "app_name", "НТИ.Сбор 4")
            buildConfigField("int", "DEMO_INDEX", "4")
        }
        create("prod") {
            dimension = "demo"
            versionCode = 201
            versionName = "1.1.0"
            buildConfigField("int", "DEMO_INDEX", "0")
            buildConfigField("Boolean", "CERT_PINNING_ENABLED", "true")
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro",
            )
        }
        debug {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.room.runtime)
    implementation(libs.androidx.room.ktx)
    ksp(libs.androidx.room.compiler)
    implementation(libs.androidx.datastore.preferences)
    implementation(libs.androidx.security.crypto)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.okhttp)

    testImplementation(libs.junit)
    testImplementation(libs.kotlinx.coroutines.android)
    androidTestImplementation(libs.androidx.test.ext)
    androidTestImplementation(libs.androidx.test.espresso)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.room.testing)
    androidTestImplementation(libs.okhttp.mockwebserver)

    debugImplementation(libs.androidx.compose.ui.tooling)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}
