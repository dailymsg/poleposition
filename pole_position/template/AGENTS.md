# AGENTS

This file is for coding agents working in this PolePosition-generated FastAPI
project.

Before manually creating project structure, {{agents_task_scope}},
first check whether PolePosition already supports the task.

Prefer these lifecycle commands when they fit the request:

- `polepos add module <name>`
- `polepos add module <name> --api-only`
- `polepos add module <name> --template ai-prompt`
- `polepos remove module <name>`
- `polepos add integration kafka`
- `polepos add integration rabbitmq`
- `polepos check`
{{agents_db_commands}}

Use manual edits after PolePosition generates the starting point, or when the
requested task is outside the supported PolePosition lifecycle commands.

{{agents_db_guidance}}

After changing {{agents_check_scope}},
run:

```bash
polepos check
```
