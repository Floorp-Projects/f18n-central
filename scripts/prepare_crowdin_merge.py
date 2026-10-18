#!/usr/bin/env python3
"""Build the translation candidate from immutable base and head commits."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


def git(repository: Path, *arguments: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repository), *arguments], text=True
    ).strip()


def prepare_merge(
    repository: Path, base_sha: str, head_sha: str, changed_files: Path
) -> None:
    for sha in (base_sha, head_sha):
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError(f"Expected a full commit SHA, got: {sha}")
        git(repository, "rev-parse", "--verify", f"{sha}^{{commit}}")

    if git(repository, "status", "--porcelain"):
        raise ValueError("Candidate checkout must be clean before preparing a merge")

    merge_base = git(repository, "merge-base", base_sha, head_sha)
    changes = subprocess.check_output(
        [
            "git", "-C", str(repository), "diff", "--name-status", "-z",
            "--no-renames", merge_base, head_sha,
        ]
    ).decode("utf-8").split("\0")
    filenames: list[str] = []
    for status, filename in zip(changes[0:-1:2], changes[1:-1:2]):
        if status not in {"A", "M"} or not filename.endswith(".json"):
            raise ValueError(f"Unexpected Crowdin change: {status}\t{filename}")
        if "\n" in filename or "\r" in filename:
            raise ValueError("Translation filenames must not contain line breaks")
        filenames.append(filename)

    # Never trust refs/pull/<number>/merge: GitHub can leave it pointing to an
    # older, clean merge after the current PR head develops conflicts.
    git(repository, "checkout", "--detach", base_sha)
    result = subprocess.run(
        [
            "git", "-C", str(repository),
            "-c", "user.name=github-actions[bot]",
            "-c", "user.email=github-actions[bot]@users.noreply.github.com",
            "merge", "--no-commit", "--no-ff", head_sha,
        ],
        text=True, capture_output=True,
    )
    if result.returncode:
        conflicts = git(repository, "diff", "--name-only", "--diff-filter=U")
        raise ValueError(
            f"Cannot merge Crowdin {head_sha} into main {base_sha}.\n"
            f"Conflicting files:\n{conflicts or '(see Git output below)'}\n"
            "Resolve these files on the crowdin branch without discarding "
            "translations, then rerun publication.\n"
            f"{result.stdout}{result.stderr}"
        )

    changed_files.write_text(
        "".join(f"{filename}\n" for filename in filenames), encoding="utf-8"
    )
    print(f"Prepared candidate: main={base_sha}, crowdin={head_sha}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--changed-files", type=Path, required=True)
    args = parser.parse_args()
    try:
        prepare_merge(
            args.repository, args.base_sha, args.head_sha, args.changed_files
        )
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
