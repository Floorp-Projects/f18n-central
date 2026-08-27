from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_translation_schema import validate_changed_files, validate_repository


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class ValidateTranslationSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.repository = self.root / "f18n"
        self.repository.mkdir()
        self.manifest = self.root / "translation-targets.json"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_file_target_accepts_complete_translation(self) -> None:
        write_json(
            self.manifest,
            {
                "targets": [
                    {
                        "type": "file",
                        "source_file": "en-US.json",
                        "f18n_path": "settings/",
                    }
                ]
            },
        )
        write_json(
            self.repository / "settings/en-US.json",
            {"page": {"title": "Settings", "enabled": True}},
        )
        write_json(
            self.repository / "settings/ja-JP.json",
            {"page": {"title": "設定", "enabled": True}},
        )

        checked, errors = validate_repository(self.repository, self.manifest)

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_file_target_reports_missing_nested_key(self) -> None:
        write_json(
            self.manifest,
            {
                "targets": [
                    {
                        "type": "file",
                        "source_file": "en-US.json",
                        "f18n_path": "settings/",
                    }
                ]
            },
        )
        write_json(
            self.repository / "settings/en-US.json",
            {"page": {"title": "Settings", "description": "Configure Floorp"}},
        )
        write_json(
            self.repository / "settings/ja-JP.json",
            {"page": {"title": "設定"}},
        )

        checked, errors = validate_repository(self.repository, self.manifest)

        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("page.description", errors[0])

    def test_directory_target_requires_each_source_file(self) -> None:
        write_json(
            self.manifest,
            {
                "targets": [
                    {
                        "type": "directory",
                        "source_locale": "en-US",
                        "f18n_path": "main/",
                    }
                ]
            },
        )
        write_json(
            self.repository / "main/en-US/browser-chrome.json",
            {"menu": {"open": "Open"}},
        )
        (self.repository / "main/ja-JP").mkdir(parents=True)

        checked, errors = validate_repository(self.repository, self.manifest)

        self.assertEqual(checked, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("translation file does not exist", errors[0])

    def test_directory_target_allows_declared_partial_locale(self) -> None:
        write_json(
            self.manifest,
            {
                "targets": [
                    {
                        "type": "directory",
                        "source_locale": "en-US",
                        "f18n_path": "main/",
                    }
                ]
            },
        )
        write_json(
            self.repository / "main/en-US/browser-chrome.json",
            {"menu": {"open": "Open", "close": "Close"}},
        )
        write_json(
            self.repository / "main/ja-JP/browser-chrome.json",
            {"menu": {"open": "開く", "close": "閉じる"}},
        )
        write_json(
            self.repository / "main/ja-JP-x-kansai/browser-chrome.json",
            {"menu": {"open": "開くで"}},
        )

        checked, errors = validate_repository(
            self.repository,
            self.manifest,
            {"ja-JP-x-kansai"},
        )

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])

    def test_changed_files_reject_source_and_unmanaged_paths(self) -> None:
        write_json(
            self.manifest,
            {
                "targets": [
                    {
                        "type": "file",
                        "source_file": "en-US.json",
                        "f18n_path": "settings/",
                    }
                ]
            },
        )
        write_json(self.repository / "settings/en-US.json", {"title": "Settings"})
        write_json(self.repository / "settings/ja-JP.json", {"title": "設定"})
        write_json(self.repository / "unmanaged.json", {"title": "Ignored"})

        errors = validate_changed_files(
            self.repository,
            self.manifest,
            ["settings/ja-JP.json", "settings/en-US.json", "unmanaged.json"],
        )

        self.assertEqual(len(errors), 2)
        self.assertIn("settings/en-US.json", errors[0])
        self.assertIn("unmanaged.json", errors[1])


if __name__ == "__main__":
    unittest.main()
