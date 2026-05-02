# Examples

Examples show the next step after project generation: what to keep, what to
rewrite, and how PolePosition's structure supports a real workflow.

## Available Examples

### Auth Foundation

Shows how the generated JWT authentication foundation protects routes before a
full login system exists.

Focus:

- public versus protected endpoints
- JWT-based current user resolution
- role-gated route examples
- local token generation for testing

Read the site guide: [Auth Foundation](auth-foundation.md)

Source scenario:
[examples/auth-foundation](https://github.com/erenertemden/poleposition/blob/main/examples/auth-foundation/README.md)

### HTML Swap

Shows how a generated module can be reshaped into a focused transformation
endpoint backed by PostgreSQL history.

Focus:

- `polepos add module html`
- rewriting a generated module for a real endpoint contract
- PostgreSQL-backed swap history
- `POST /api/v1/html/swap`

Read the site guide: [HTML Swap](html-swap.md)

Source scenario:
[examples/html-swap](https://github.com/erenertemden/poleposition/blob/main/examples/html-swap/README.md)
