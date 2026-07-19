# DevOps Domain

The target deployment is Docker on a university-managed server. Separate
frontend/backend build stages and a production PostgreSQL service are expected.
Telegram requires the Mini App URL to use HTTPS.

Secrets such as the bot token, database credentials, and signing material must
come from the server environment or secret manager and never from images,
source control, browser bundles, or CI logs. Containers run as non-root users,
use pinned dependencies, expose health checks, and write persistent database
data outside ephemeral layers.

CI must enforce `docs/testing.md`, scan dependencies and code, build production
artifacts and Docker images, and require approval before production deployment.
Operations require structured redacted logs, readiness/liveness checks,
database backups, restore verification, and a rollback runbook.
