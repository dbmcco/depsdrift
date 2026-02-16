import unittest

from depsdrift.drift import compute_deps_drift
from depsdrift.git_tools import WorkingChanges
from depsdrift.specs import DepsdriftSpec


class DepsdriftTests(unittest.TestCase):
    def test_lock_not_updated(self) -> None:
        spec = DepsdriftSpec(
            schema=1,
            manifests=["package.json"],
            locks=["package-lock.json"],
            require_lock_update_when_manifest_changes=True,
            ignore=[],
        )

        report = compute_deps_drift(
            task_id="t1",
            task_title="T1",
            description="",
            spec=spec,
            git_root="/tmp",
            changes=WorkingChanges(changed_files=["package.json"]),
        )
        kinds = {f["kind"] for f in report["findings"]}
        self.assertIn("lock_not_updated", kinds)
        self.assertEqual(report["score"], "yellow")

    def test_lock_updated(self) -> None:
        spec = DepsdriftSpec(
            schema=1,
            manifests=["package.json"],
            locks=["package-lock.json"],
            require_lock_update_when_manifest_changes=True,
            ignore=[],
        )

        report = compute_deps_drift(
            task_id="t1",
            task_title="T1",
            description="",
            spec=spec,
            git_root="/tmp",
            changes=WorkingChanges(changed_files=["package.json", "package-lock.json"]),
        )
        kinds = {f["kind"] for f in report["findings"]}
        self.assertNotIn("lock_not_updated", kinds)


if __name__ == "__main__":
    unittest.main()

