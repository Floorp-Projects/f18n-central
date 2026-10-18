from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from prepare_crowdin_merge import git, prepare_merge


class PrepareCrowdinMergeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        git(self.repository, "init", "--initial-branch=main")
        git(self.repository, "config", "user.name", "Test")
        git(self.repository, "config", "user.email", "test@example.com")
        self.commit_file("settings/ja-JP.json", {"title": "設定"})
        self.original = git(self.repository, "rev-parse", "HEAD")
        git(self.repository, "branch", "crowdin")
        self.changed_files = self.root / "changed-files.txt"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def commit_file(self, filename: str, value: object) -> str:
        path = self.repository / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
        git(self.repository, "add", filename)
        git(self.repository, "commit", "-m", filename)
        return git(self.repository, "rev-parse", "HEAD")

    def test_candidate_uses_current_commits_instead_of_stale_merge_ref(self) -> None:
        git(self.repository, "update-ref", "refs/pull/94/merge", self.original)
        base = self.commit_file("settings/en-US.json", {"title": "Settings"})
        git(self.repository, "checkout", "crowdin")
        head = self.commit_file("settings/ja-JP.json", {"title": "最新の設定"})

        prepare_merge(self.repository, base, head, self.changed_files)

        self.assertEqual(
            json.loads((self.repository / "settings/ja-JP.json").read_text()),
            {"title": "最新の設定"},
        )
        self.assertTrue((self.repository / "settings/en-US.json").is_file())
        self.assertEqual(self.changed_files.read_text(), "settings/ja-JP.json\n")
        self.assertEqual(git(self.repository, "rev-parse", "main"), base)
        self.assertEqual(git(self.repository, "rev-parse", "crowdin"), head)
        self.assertEqual(git(self.repository, "rev-parse", "MERGE_HEAD"), head)

    def test_conflict_reports_file_without_reusing_old_successful_merge(self) -> None:
        git(self.repository, "update-ref", "refs/pull/94/merge", self.original)
        base = self.commit_file("settings/ja-JP.json", {"title": "main の変更"})
        git(self.repository, "checkout", "crowdin")
        head = self.commit_file("settings/ja-JP.json", {"title": "Crowdin の変更"})

        with self.assertRaisesRegex(ValueError, "Conflicting files:\nsettings/ja-JP.json"):
            prepare_merge(self.repository, base, head, self.changed_files)

        self.assertFalse(self.changed_files.exists())
        self.assertEqual(git(self.repository, "rev-parse", "main"), base)
        self.assertEqual(git(self.repository, "rev-parse", "crowdin"), head)

    def test_rejects_removed_translation(self) -> None:
        git(self.repository, "checkout", "crowdin")
        git(self.repository, "rm", "settings/ja-JP.json")
        git(self.repository, "commit", "-m", "Remove translation")
        head = git(self.repository, "rev-parse", "HEAD")

        with self.assertRaisesRegex(ValueError, "Unexpected Crowdin change: D"):
            prepare_merge(self.repository, self.original, head, self.changed_files)

    def test_rejects_non_json_change(self) -> None:
        git(self.repository, "checkout", "crowdin")
        head = self.commit_file("untrusted.py", "print('untrusted')")

        with self.assertRaisesRegex(ValueError, "Unexpected Crowdin change"):
            prepare_merge(self.repository, self.original, head, self.changed_files)

    def test_rejects_file_type_change(self) -> None:
        git(self.repository, "checkout", "crowdin")
        path = self.repository / "settings/ja-JP.json"
        path.unlink()
        path.symlink_to("en-US.json")
        git(self.repository, "add", "settings/ja-JP.json")
        git(self.repository, "commit", "-m", "Replace translation with symlink")
        head = git(self.repository, "rev-parse", "HEAD")

        with self.assertRaisesRegex(ValueError, "Unexpected Crowdin change: T"):
            prepare_merge(self.repository, self.original, head, self.changed_files)

    def test_merge_commit_preserves_crowdin_ancestry_for_next_publication(self) -> None:
        git(self.repository, "checkout", "crowdin")
        head = self.commit_file("settings/ja-JP.json", {"title": "最新の設定"})
        git(self.repository, "checkout", "main")
        git(self.repository, "merge", "--no-ff", "crowdin", "-m", "Publish")
        base = self.commit_file("settings/en-US.json", {"title": "Settings"})
        git(self.repository, "checkout", "crowdin")
        head = self.commit_file("settings/ja-JP.json", {"title": "次回の設定"})

        prepare_merge(self.repository, base, head, self.changed_files)

        self.assertEqual(self.changed_files.read_text(), "settings/ja-JP.json\n")
        self.assertEqual(
            json.loads((self.repository / "settings/ja-JP.json").read_text()),
            {"title": "次回の設定"},
        )

    def test_rejects_dirty_checkout(self) -> None:
        (self.repository / "settings/ja-JP.json").write_text("uncommitted")
        with self.assertRaisesRegex(ValueError, "must be clean"):
            prepare_merge(self.repository, self.original, self.original, self.changed_files)

    def test_requires_full_commit_sha(self) -> None:
        with self.assertRaisesRegex(ValueError, "full commit SHA"):
            prepare_merge(self.repository, "main", self.original, self.changed_files)


if __name__ == "__main__":
    unittest.main()
