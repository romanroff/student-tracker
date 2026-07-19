# Frontend Domain

The target `frontend/` is a React and TypeScript Telegram Mini App. It consumes
only the versioned FastAPI contract, passes Telegram `initData` for server-side
validation, and contains no trusted authorization logic or secrets.

Use typed API boundaries and explicit loading, empty, validation, forbidden,
offline, and unexpected-error states. Meet keyboard, focus, label, contrast,
and responsive mobile requirements from `docs/contracts/ui.md`. Validate logic
with Vitest/Testing Library and primary workflows with Playwright.
