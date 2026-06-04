# iOS (фаза B)

На Linux-сборке iOS-таргеты отключены (`kotlin.native.ignoreDisabledTargets=true`). На macOS:

```bash
./gradlew :shared:linkReleaseFrameworkIosSimulatorArm64
```

Скопируйте `shared/build/bin/iosSimulatorArm64/releaseFramework/Shared.framework` в Xcode-проект `iosApp` и подключите как Embedded Framework.

## Известное ограничение

Если Canvas-визуализация эмбеддингов тормозит на устройстве — в уроке показывается список соседей (fallback уже в `SandboxResultView`).

## Actual-реализации

- `iosMain`: Keychain secure storage, Ktor Darwin, SQLDelight Native driver.
