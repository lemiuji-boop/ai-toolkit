# Sprint 06: LLM Router

Implement:

- LlmProvider interface;
- Ollama provider;
- OpenAI-compatible provider;
- mock provider for tests;
- model profiles by task;
- structured output validation;
- token usage log;
- fallback on provider failure;
- admin UI for providers.

Acceptance:

- admin can configure Ollama URL;
- system can call local model;
- invalid JSON is rejected and retried;
- token usage is logged.
