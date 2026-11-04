# Testing Strategy

## TDD Cycle

Red → Green → Quality → Full Suite → Handoff

1. **Red**: Write a failing test that defines the expected behavior
2. **Green**: Write the minimum code to make the test pass
3. **Quality**: Run pyright + ruff (Python) or tsc + eslint (TypeScript)
4. **Full Suite**: Run all tests to check for regressions
5. **Handoff**: Mark task complete, update task.md

## Python Testing

### Framework
- pytest with markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- pytest-asyncio for async tests
- hypothesis for property-based testing (where applicable)

### Database Isolation
- Function-scoped `tmp_path` SQLite databases
- No shared state between tests
- Autouse fixture for database URL isolation

### Test Structure
```
tests/
├── conftest.py          # Shared fixtures, DB setup
├── unit/                # Pure logic tests (no IO)
│   ├── test_download.py
│   ├── test_transcript.py
│   └── test_tts.py
├── integration/         # Tests with real adapters (DB, yt-dlp)
│   ├── test_youtube_adapter.py
│   ├── test_kokoro_adapter.py
│   └── test_settings_repo.py
└── e2e/                 # Full API tests
    └── test_api_routes.py
```

## TypeScript Testing

### MCP + UI Unit Tests
- vitest with mocked fetch for MCP tools
- testing-library/react for component tests

### E2E Tests
- Playwright for full Electron app flows

## Quality Gates

Use the current D6 command registration in [commands.md](commands.md), with the receipt and durable evidence contract in [output-evidence-policy.md](output-evidence-policy.md). Select static checks, then affected behavioral/contract tests including shared fixtures/config, then one fresh full scoped gate on the final review state. Later stages remain not_run after blocking failure. Rerun when code/tests/config/environment/external inputs change; partial or cached checks cannot establish a full pass.

All Python/UI/MCP packages exist. Preserve function-scoped database isolation and current fixtures. Runtime GUI behavior requires Playwright against real Electron; build compiled outputs first and clear ELECTRON_RUN_AS_NODE. Keep `ui/scripts/playwright-with-outputfile.mjs` output conventions. An external launch failure requires the failed command, nonzero exit, decisive output and linked CI follow-up; a test must still be written and wired. No product tests are required solely because governance prose changes, unless product/shared product inputs are touched.

Coverage is advisory: core 80–90%, infrastructure/API/MCP 70%, UI 50–60%. Assertions written in Red are immutable in Green; fixture/setup corrections may repair incorrect setup without weakening expectations. API/MCP/UI boundaries enforce runtime schemas and source-backed invalid-input behavior. Validate mocks against real boundary schemas. Never use a shared receipts/artifact root as a test cleanup root.
