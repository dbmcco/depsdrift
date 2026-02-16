from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from depsdrift.git_tools import WorkingChanges
from depsdrift.globmatch import match_any
from depsdrift.specs import DepsdriftSpec


@dataclass(frozen=True)
class Finding:
    kind: str
    severity: str
    summary: str
    details: dict[str, Any] | None = None


def compute_deps_drift(
    *,
    task_id: str,
    task_title: str,
    description: str,
    spec: DepsdriftSpec,
    git_root: str | None,
    changes: WorkingChanges | None,
) -> dict[str, Any]:
    findings: list[Finding] = []

    changed_files: list[str] = []
    if changes:
        changed_files = [
            p
            for p in changes.changed_files
            if not (p.startswith(".workgraph/") or p.startswith(".git/") or match_any(p, spec.ignore))
        ]

    telemetry: dict[str, Any] = {
        "files_changed": len(changed_files),
    }

    if spec.schema != 1:
        findings.append(
            Finding(
                kind="unsupported_schema",
                severity="warn",
                summary=f"Unsupported depsdrift schema: {spec.schema} (expected 1)",
            )
        )

    if not spec.manifests or not spec.locks:
        findings.append(
            Finding(
                kind="invalid_deps_config",
                severity="warn",
                summary="depsdrift manifests[] or locks[] are empty; nothing to keep in sync",
            )
        )

    manifest_changed = [p for p in changed_files if spec.manifests and match_any(p, spec.manifests)]
    lock_changed = [p for p in changed_files if spec.locks and match_any(p, spec.locks)]
    telemetry["manifest_files_changed"] = len(manifest_changed)
    telemetry["lock_files_changed"] = len(lock_changed)

    if spec.require_lock_update_when_manifest_changes and manifest_changed and not lock_changed and spec.locks:
        findings.append(
            Finding(
                kind="lock_not_updated",
                severity="warn",
                summary="Dependency manifest changed but no lockfile changed",
                details={
                    "manifests": spec.manifests,
                    "locks": spec.locks,
                    "changed_manifests": manifest_changed[:50],
                },
            )
        )

    score = "green"
    if any(f.severity == "warn" for f in findings):
        score = "yellow"
    if any(f.severity == "error" for f in findings):
        score = "red"

    recommendations: list[dict[str, Any]] = []
    for f in findings:
        if f.kind == "lock_not_updated":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Update the lockfile(s) for this dependency change",
                    "rationale": "Lock drift causes non-reproducible builds and surprise dependency upgrades in CI/deploy.",
                }
            )
        elif f.kind == "invalid_deps_config":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Populate depsdrift manifests[] and locks[]",
                    "rationale": "Depsdrift needs explicit manifest/lock paths to keep in sync.",
                }
            )
        elif f.kind == "unsupported_schema":
            recommendations.append(
                {
                    "priority": "high",
                    "action": "Set depsdrift schema = 1",
                    "rationale": "Only schema v1 is currently supported.",
                }
            )

    seen_actions: set[str] = set()
    recommendations = [r for r in recommendations if not (r["action"] in seen_actions or seen_actions.add(r["action"]))]  # type: ignore[arg-type]

    return {
        "task_id": task_id,
        "task_title": task_title,
        "git_root": git_root,
        "score": score,
        "spec": asdict(spec),
        "telemetry": telemetry,
        "findings": [asdict(f) for f in findings],
        "recommendations": recommendations,
    }

