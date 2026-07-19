# Behavior Contracts

User-visible Mini App and Telegram bot behavior is described in `features/*.feature` before
implementation. Scenarios use Given for authenticated identity and tenant-owned
state, When for one user action, and Then for observable UI/API/database
results. Security scenarios must include a second tenant and prove absence of
cross-tenant reads and writes.

Each scenario names its automated binding: backend pytest integration/contract
test, bot service/UI test, frontend component test, or Playwright end-to-end test. Manual acceptance
is supplementary and cannot replace deterministic authorization coverage.
