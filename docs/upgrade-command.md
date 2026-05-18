# Upgrade Reports

`polepos upgrade` gives a read-only view of an existing generated project after
the PolePosition CLI has been upgraded.

It does not rewrite application code. It reports enough context for a human or
coding agent to decide what to validate next.

## Basic Flow

Upgrade the CLI:

```bash
uv tool upgrade poleposition
```

Then run the report inside a generated project:

```bash
cd shop-api
polepos upgrade
```

The report includes:

- CLI version
- project root
- package name
- database mode from `.poleposition.toml`
- current `polepos check` status
- recorded module templates
- enabled generated integrations
- next-step commands

## Recommended Upgrade Checklist

```bash
polepos upgrade
polepos check --fix
polepos check
uv sync
uv run pytest
```

Use `polepos check --fix` only for safe managed marker restoration. It does not
replace missing generated files, install dependencies, create migrations, or
rewrite custom code.

## Reading the Report

If project check passes, the project still follows the known PolePosition
lifecycle contract.

If project check fails, read the listed `PPCHK` issues first. Common causes are:

- missing managed markers after a merge conflict
- generated module files removed manually
- stale router/model/test references after deleting a module directory
- integration dependency, setting, or `.env.example` drift
- auth workflow partially detached

Fix intentional drift manually, or use the matching lifecycle command such as
`polepos remove module <name>` when generated remnants need cleanup.

## What It Does Not Do

`polepos upgrade` does not:

- edit files
- install packages
- run migrations
- update generated app dependencies
- infer release-specific migrations
- contact package indexes or external services

Generated projects are normal application code. CLI upgrades add new commands
and better defaults for future scaffolds, but existing projects stay under the
team's control.
