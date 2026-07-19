# Component Registry

Statuses: `canonical`, `supporting`, `fallback`, `experimental`, `legacy`,
`generated`, `test-only`, `unused`, or `unknown`.

| Component | Path | Status | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Telegram gradebook bot | `backend/app/bot_launcher.py` | canonical | Telegram teachers | Long polling and inline keyboard workflows |
| Bot application service | `backend/app/bot_service.py` | canonical | Telegram gradebook bot | Telegram-id tenant scope and atomic writes |
| Bot UI builders | `backend/app/bot_ui.py` | canonical | Telegram gradebook bot | Bounded callback data, paging, attendance drafts |
| FastAPI backend | `backend/app/` | canonical | Mini App frontend | Tenant-scoped versioned API |
| React frontend | `frontend/` | canonical | Telegram users | Responsive course and lesson register UI |
| Database migrations | `backend/migrations/` | canonical | PostgreSQL/SQLite | Alembic revision history |
| Python tests | `tests/backend/` | test-only | CI/developers | API, auth, validation, and tenant isolation |
| Behavior contracts | `features/` | test-only | Product and tests | Executable acceptance descriptions per slice |
| CI pipeline | `.github/workflows/quality.yml` | supporting | Contributors | Backend, frontend, migration, security, Docker gates |
