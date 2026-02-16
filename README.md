# depsdrift

`depsdrift` is a Speedrift-suite sidecar that detects **dependency lock drift** without hard-blocking development.

It is designed to be orchestrated by `driftdriver` (via `./.workgraph/drifts`).

## Ecosystem Map

This project is part of the Speedrift suite for Workgraph-first drift control.

- Spine: [Workgraph](https://graphwork.github.io/)
- Orchestrator: [driftdriver](https://github.com/dbmcco/driftdriver)
- Baseline lane: [coredrift](https://github.com/dbmcco/coredrift)
- Optional lanes: [specdrift](https://github.com/dbmcco/specdrift), [datadrift](https://github.com/dbmcco/datadrift), [depsdrift](https://github.com/dbmcco/depsdrift), [uxdrift](https://github.com/dbmcco/uxdrift), [therapydrift](https://github.com/dbmcco/therapydrift), [yagnidrift](https://github.com/dbmcco/yagnidrift), [redrift](https://github.com/dbmcco/redrift)

## Task Spec Format

Add a per-task fenced TOML block:

````md
```depsdrift
schema = 1

manifests = [
  "package.json",
  "pyproject.toml",
  "requirements.txt",
]
locks = [
  "package-lock.json",
  "pnpm-lock.yaml",
  "uv.lock",
  "poetry.lock",
]

require_lock_update_when_manifest_changes = true
ignore = []
```
````

Semantics:
- If any `manifests` file changes and **no** `locks` file changes, `depsdrift` emits an advisory finding.

## Workgraph Integration

From a Workgraph repo:

```bash
./.workgraph/drifts check --task <id> --write-log --create-followups
```

Standalone:

```bash
depsdrift --dir . wg check --task <id> --write-log --create-followups
```

Exit codes:
- `0`: clean
- `3`: findings exist (advisory)
