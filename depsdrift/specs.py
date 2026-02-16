from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from typing import Any

FENCE_INFO = "depsdrift"

_FENCE_RE = re.compile(
    r"```(?P<info>depsdrift)\s*\n(?P<body>.*?)\n```",
    re.DOTALL,
)


def extract_depsdrift_spec(description: str) -> str | None:
    m = _FENCE_RE.search(description or "")
    if not m:
        return None
    return m.group("body").strip()


def parse_depsdrift_spec(text: str) -> dict[str, Any]:
    data = tomllib.loads(text)
    if not isinstance(data, dict):
        raise ValueError("depsdrift block must parse to a TOML table/object.")
    return data


@dataclass(frozen=True)
class DepsdriftSpec:
    schema: int
    manifests: list[str]
    locks: list[str]
    require_lock_update_when_manifest_changes: bool
    ignore: list[str]

    @staticmethod
    def from_raw(raw: dict[str, Any]) -> "DepsdriftSpec":
        schema = int(raw.get("schema", 1))

        manifests_raw = raw.get("manifests", [])
        locks_raw = raw.get("locks", [])

        manifests = [str(x) for x in (manifests_raw or [])] if isinstance(manifests_raw, list) else []
        locks = [str(x) for x in (locks_raw or [])] if isinstance(locks_raw, list) else []

        require = bool(raw.get("require_lock_update_when_manifest_changes", True))

        ignore_raw = raw.get("ignore", [])
        ignore = [str(x) for x in (ignore_raw or [])] if isinstance(ignore_raw, list) else []

        return DepsdriftSpec(
            schema=schema,
            manifests=manifests,
            locks=locks,
            require_lock_update_when_manifest_changes=require,
            ignore=ignore,
        )

