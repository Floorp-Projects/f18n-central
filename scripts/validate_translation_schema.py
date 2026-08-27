#!/usr/bin/env python3
"""Validate that translated JSON files contain every source-locale key."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any


JsonObject = dict[str, Any]


def read_json(path: Path) -> JsonObject:
    if path.is_symlink():
        raise ValueError(f"JSON file must not be a symbolic link: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON file {path}: {error}") from error

    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def leaf_paths(value: Any, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    if isinstance(value, dict):
        paths: set[tuple[str, ...]] = set()
        for key, child in value.items():
            paths.update(leaf_paths(child, (*prefix, key)))
        return paths
    return {prefix}


def path_within(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"translation target escapes repository: {relative_path}")
    return candidate


def compare_translation(source: Path, translation: Path) -> list[str]:
    errors: list[str] = []
    try:
        source_keys = leaf_paths(read_json(source))
        translation_keys = leaf_paths(read_json(translation))
    except ValueError as error:
        return [str(error)]

    for key_path in sorted(source_keys - translation_keys):
        errors.append(
            f"{translation}: missing translation key {'.'.join(key_path)}"
        )
    return errors


def validate_file_target(root: Path, target: JsonObject) -> tuple[int, list[str]]:
    base = path_within(root, str(target["f18n_path"]))
    source = base / str(target["source_file"])
    if not source.is_file():
        return 0, [f"source file does not exist: {source}"]

    translations = sorted(path for path in base.glob("*.json") if path != source)
    if not translations:
        return 0, [f"no translated files found for source: {source}"]

    errors: list[str] = []
    for translation in translations:
        errors.extend(compare_translation(source, translation))
    return len(translations), errors


def validate_directory_target(
    root: Path,
    target: JsonObject,
    allowed_partial_locales: set[str],
) -> tuple[int, list[str]]:
    base = path_within(root, str(target["f18n_path"]))
    source_locale = str(target["source_locale"])
    source_directory = base / source_locale
    source_files = sorted(source_directory.glob("*.json"))
    if not source_files:
        return 0, [f"no source JSON files found in: {source_directory}"]

    locale_directories = sorted(
        path
        for path in base.iterdir()
        if path.is_dir()
        and path.name != source_locale
        and path.name not in allowed_partial_locales
    )
    if not locale_directories:
        return 0, [f"no translated locale directories found in: {base}"]

    checked = 0
    errors: list[str] = []
    for locale_directory in locale_directories:
        for source in source_files:
            translation = locale_directory / source.name
            if not translation.is_file():
                errors.append(f"translation file does not exist: {translation}")
                continue
            checked += 1
            errors.extend(compare_translation(source, translation))
    return checked, errors


def validate_repository(
    repository: Path,
    manifest: Path,
    allowed_partial_locales: set[str] | None = None,
) -> tuple[int, list[str]]:
    root = repository.resolve()
    partial_locales = allowed_partial_locales or set()
    manifest_value = read_json(manifest.resolve())
    targets = manifest_value.get("targets")
    if not isinstance(targets, list):
        return 0, [f"translation target manifest must contain a targets array: {manifest}"]

    checked = 0
    errors: list[str] = []
    for target in targets:
        if not isinstance(target, dict):
            errors.append("translation target must be an object")
            continue
        try:
            target_type = target.get("type", "file")
            if target_type == "directory":
                target_checked, target_errors = validate_directory_target(
                    root,
                    target,
                    partial_locales,
                )
            elif target_type == "file":
                target_checked, target_errors = validate_file_target(root, target)
            else:
                target_checked, target_errors = 0, [
                    f"unsupported translation target type: {target_type}"
                ]
        except (KeyError, OSError, ValueError) as error:
            target_checked, target_errors = 0, [str(error)]

        checked += target_checked
        errors.extend(target_errors)

    return checked, errors


def validate_changed_files(
    repository: Path,
    manifest: Path,
    changed_files: list[str],
) -> list[str]:
    root = repository.resolve()
    manifest_value = read_json(manifest.resolve())
    targets = manifest_value.get("targets")
    if not isinstance(targets, list):
        return [f"translation target manifest must contain a targets array: {manifest}"]

    errors: list[str] = []
    for changed_file in changed_files:
        relative = PurePosixPath(changed_file)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"changed file escapes repository: {changed_file}")
            continue
        if relative.suffix != ".json":
            errors.append(f"Crowdin may only change JSON files: {changed_file}")
            continue

        matches_translation_target = False
        for target in targets:
            if not isinstance(target, dict):
                continue
            try:
                target_root = PurePosixPath(str(target["f18n_path"]).strip("/"))
                target_relative = relative.relative_to(target_root)
            except (KeyError, ValueError):
                continue

            target_type = target.get("type", "file")
            if target_type == "directory":
                source_locale = str(target.get("source_locale", ""))
                matches_translation_target = (
                    len(target_relative.parts) == 2
                    and target_relative.parts[0] != source_locale
                )
            elif target_type == "file":
                source_file = str(target.get("source_file", ""))
                matches_translation_target = (
                    len(target_relative.parts) == 1
                    and target_relative.name != source_file
                )

            if matches_translation_target:
                break

        if not matches_translation_target:
            errors.append(
                f"Crowdin changed a source or non-translation file: {changed_file}"
            )
            continue

        candidate = root.joinpath(*relative.parts)
        if not candidate.is_file() or candidate.is_symlink():
            errors.append(f"changed translation must be a regular file: {changed_file}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository",
        type=Path,
        default=Path.cwd(),
        help="Path to the f18n-central checkout",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to Floorp's translation-targets.json",
    )
    parser.add_argument(
        "--allow-partial-locale",
        action="append",
        default=[],
        help="Locale directory that intentionally relies on fallback translations",
    )
    parser.add_argument(
        "--changed-files",
        type=Path,
        help="Optional newline-delimited list of files changed by Crowdin",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        checked, errors = validate_repository(
            args.repository,
            args.manifest,
            set(args.allow_partial_locale),
        )
        if args.changed_files:
            changed_files = [
                line.strip()
                for line in args.changed_files.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            errors.extend(
                validate_changed_files(
                    args.repository,
                    args.manifest,
                    changed_files,
                )
            )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(
            f"Translation schema validation failed with {len(errors)} error(s).",
            file=sys.stderr,
        )
        return 1

    print(f"Translation schema validation passed for {checked} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
