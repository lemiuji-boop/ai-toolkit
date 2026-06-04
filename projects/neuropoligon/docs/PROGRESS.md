# Прогресс разработки Нейрополигон

## Этап 0 — Инициализация
- Gate A: `./gradlew projects` — OK
- Gate B: N/A
- Gate C: KMP + Compose + Koin + SQLDelight — OK
- Gate D: `.cursorrules` — OK

## Этап 1 — Контент
- Gate A: compile Android/Desktop — OK
- Gate B: `ContentParseTest` — OK
- Gate C: треки из JSON, UI списков — OK

## Этап 2 — Foundations
- Gate B: `TokenizerTest`, `SpacedRepetitionTest` — OK
- Gate C: BPE + embeddings офлайн — OK

## Этап 3 — AI Gateway
- Gate C: Ktor + secure storage + capabilities (DeepSeek off Web) — OK

## Этап 4 — Sandboxes
- Gate C: все SandboxType в `SandboxRuntime` — OK

## Этап 5 — Глоссарий
- Gate C: `glossary.json` + `GlossaryMarkdown` — OK

## Этап 6 — Прогресс
- Gate C: SQLDelight + SM-2 + ChallengeEvaluator — OK

## Этап 7 — Уровни сложности
- Gate C: онбординг + `ContentEngine` combine level — OK

## Этап 8 — Auth
- Gate C: гостевой режим + локальная сессия — OK

## Этап 9–10 — Контент + Builder
- Gate C: доп. треки + `CodeRecipeBlock` — OK

## Этап 11 — UI polish
- Gate C: навигация, AdaptiveContent, skip onboarding — OK

## Этап 12 — iOS
- Gate A: iosMain actuals; сборка framework — только macOS (см. `iosApp/README.md`)

## Этап 13 — Релиз
- См. `docs/BUG_AUDIT.md`
