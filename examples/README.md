# Examples

This directory contains concrete usage scenarios for PolePosition.

These examples are useful when you want to understand not only what the CLI generates, but how a generated project should be adapted for a real use case.

## Available Examples

### Auth Foundation

Path:

```text
examples/auth-foundation/README.md
```

Focus:

- public versus protected endpoints
- JWT-based current user resolution
- role-gated route example
- local token generation for testing

Use this when you want to understand how the generated auth layer is supposed to be used before a full login system exists.

### HTML Swap

Path:

```text
examples/html-swap/README.md
```

Focus:

- `polepos add module html --api-only`
- reshaping a generated module into a transformation-focused endpoint
- PostgreSQL-backed swap history
- `POST /api/v1/html/swap`

Use this when you want to see how a non-generic business use case can still fit the PolePosition structure.

## Why These Examples Matter

The template shows the default generated state.
The examples show the next step:

- what to keep
- what to rewrite
- what the real endpoint contract should look like
- how the generated project supports the use case

That makes examples especially useful for:

- onboarding
- architecture review
- agent understanding
- product direction discussions
