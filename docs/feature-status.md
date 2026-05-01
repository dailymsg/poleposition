# Feature Status

This file describes the current maturity of PolePosition features.

The goal is not to label features as simply "done" or "not done".
Instead, it clarifies whether a feature is:

- stable enough for normal use
- a strong foundation but still growing
- intentionally partial

## Status Levels

- `Stable foundation`: good default, broadly usable, expected to stay
- `Growing`: useful and real, but likely to evolve
- `Partial by design`: intentionally scoped down for now

## Current Status

| Area | Status | Notes |
|---|---|---|
| `polepos start` | Stable foundation | Core product entrypoint; generated project shape is now a major part of the product contract. |
| Template rendering | Stable foundation | Placeholder replacement and template packaging are in good shape. |
| Generated FastAPI structure | Stable foundation | `auth`, `bootstrap`, `api`, `db`, `domain`, `integrations`, `modules` layout is now part of the product identity. |
| `polepos add module` with `standard` | Growing | Strong differentiator; works well, but still depends on managed marker blocks. |
| `polepos add module` with `ai-prompt` | Growing | Good provider-agnostic foundation; adapters are scaffold-level, not full provider integrations yet. |
| `polepos db ...` commands | Stable foundation | Good migration lifecycle wrapper around Alembic. |
| Alembic migration support | Stable foundation | Generated projects are migration-first. |
| Docker and PostgreSQL workflow | Growing | Good local runtime story; Docker e2e exists as opt-in smoke coverage. |
| Auth foundation | Partial by design | Strong route-boundary pattern; not yet a complete login/user management system. |
| JSON logging support | Stable foundation | Works as a runtime format choice; deeper request-context enrichment can still improve. |
| CORS support | Stable foundation | Settings-driven and production-aware. |
| Example scenarios | Growing | Good for onboarding and product understanding; should expand over time. |

## Important Clarifications

### `add module`

This is one of the most important product surfaces.

It is already useful, but it still assumes PolePosition-managed markers remain in place.
That means it is powerful, but not fully free-form.

### Auth foundation

The current auth layer solves:

- public vs protected endpoint boundaries
- current user resolution
- simple role-gated authorization

It does not yet solve:

- login
- password storage
- refresh tokens
- database-backed users
- advanced permission systems

### AI prompt modules

The current `ai-prompt` template is intentionally provider-agnostic.
That is a strength, but it also means provider adapters are not yet full out-of-the-box integrations.

This is best understood as:

- a solid module architecture
- a useful orchestration pattern
- a starting point for real provider integration

## Recommended Interpretation For Contributors

When deciding how to change the repo:

- preserve `Stable foundation` areas carefully
- improve `Growing` areas without overcomplicating them
- avoid presenting `Partial by design` areas as complete systems

That balance is important for keeping product messaging honest while still building a strong platform.
