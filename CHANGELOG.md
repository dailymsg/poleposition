# Changelog

Notable PolePosition changes are tracked here.

PolePosition follows Conventional Commits in repository history. This changelog
summarizes user-facing behavior, release readiness work, and known beta scope.

## Unreleased

### Added

- Added documentation pages for troubleshooting, configuration, integration
  guides, and release or upgrade notes.
- Added CI coverage reporting with `pytest-cov` and uploaded coverage XML
  artifacts.
- Documented CI, E2E, docs deploy, and coverage behavior in the README.

### Beta Release Checklist

- Confirm the Docker/PostgreSQL e2e workflow in an environment with Docker
  available.
- Keep documenting intentionally scoped surfaces such as auth foundations,
  provider-agnostic LLM adapters, and explicit messaging worker/runtime code.

## 0.0.27 - 2026-05-05

### Added

- Added GitHub Actions test CI for Python `3.10`, `3.11`, `3.12`, `3.13`, and
  `3.14`.
- Added docs strict build coverage in CI.
- Added a non-Docker e2e workflow for generated-project lifecycle smoke tests.
- Added generated `AGENTS.md` guidance so coding agents check PolePosition
  lifecycle commands before manually scaffolding modules, integrations, checks,
  or migrations.
- Expanded README positioning for teams coming from Spring Boot or ASP.NET Core.

### Changed

- Hardened TOML dependency patching for generated project `pyproject.toml`
  updates.
- Added preflight marker checks before integration patching so drift is reported
  before generated files are partially written.
- Tightened `polepos start` option parsing.
- Documented the repository commit message standard.
- Moved the package classifier to `Development Status :: 4 - Beta`.

### Notes

- The PolePosition CLI supports Python `>=3.10`.
- Generated FastAPI projects target Python `>=3.11`.
- Docker/PostgreSQL e2e coverage should be confirmed in a Docker-capable
  environment before publishing a beta release.
