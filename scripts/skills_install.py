#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from skills_common import sha256_tree
from skills_scan import scan_skill_dir
from skills_validate import validate as validate_sources_and_locks


class InstallError(Exception):
    pass


@dataclass(frozen=True)
class SkillLock:
    name: str
    source_id: str
    ref: str  # owner/repo@<commit>
    sha256: str


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise InstallError(f"File not found: {path}") from e
    except json.JSONDecodeError as e:
        raise InstallError(f"Invalid JSON: {path}: {e}") from e


def _parse_lock(path: Path) -> list[SkillLock]:
    obj = _load_json(path)
    if obj.get("version") != 1:
        raise InstallError(f"Unsupported lock version: {obj.get('version')!r} (expected 1)")
    skills = obj.get("skills")
    if not isinstance(skills, list):
        raise InstallError("Lock: skills must be a list")

    out: list[SkillLock] = []
    for idx, it in enumerate(skills):
        if not isinstance(it, dict):
            raise InstallError(f"Lock.skills[{idx}] must be an object")
        name = it.get("name")
        source_id = it.get("sourceId")
        ref = it.get("ref")
        sha256 = it.get("sha256")
        if not isinstance(name, str) or not name.strip():
            raise InstallError(f"Lock.skills[{idx}].name must be a non-empty string")
        if not isinstance(source_id, str) or not source_id.strip():
            raise InstallError(f"Lock.skills[{idx}].sourceId must be a non-empty string")
        if not isinstance(ref, str) or not ref.strip():
            raise InstallError(f"Lock.skills[{idx}].ref must be a non-empty string")
        if not isinstance(sha256, str) or not sha256.strip():
            raise InstallError(f"Lock.skills[{idx}].sha256 must be a non-empty string")
        if not all(x.strip() for x in [name, source_id, ref, sha256]):
            raise InstallError(f"Lock.skills[{idx}] must contain non-empty name/sourceId/ref/sha256")
        out.append(SkillLock(name=name.strip(), source_id=source_id.strip(), ref=ref.strip(), sha256=sha256.strip()))
    return out


def _run_git(args: list[str], *, cwd: Path) -> str:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env["GCM_INTERACTIVE"] = "never"
    p = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
    )
    if p.returncode != 0:
        raise InstallError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def _ensure_repo(*, cache_root: Path, owner: str, repo: str) -> Path:
    repo_dir = cache_root / f"{owner}__{repo}"
    if repo_dir.exists() and not (repo_dir / ".git").exists():
        raise InstallError(f"Repo cache path exists but is not a git repo: {repo_dir}")

    if not repo_dir.exists():
        repo_dir.mkdir(parents=True, exist_ok=True)
        _run_git(["init"], cwd=repo_dir)
        _run_git(["remote", "add", "origin", f"https://github.com/{owner}/{repo}.git"], cwd=repo_dir)
    return repo_dir


def _fetch_commit(*, repo_dir: Path, commit: str) -> None:
    # Fetch just the commit we need.
    _run_git(["fetch", "--depth", "1", "origin", commit], cwd=repo_dir)


def _git_has_path(*, repo_dir: Path, commit: str, path: str) -> bool:
    p = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}:{path}"],
        cwd=str(repo_dir),
        text=True,
        capture_output=True,
    )
    return p.returncode == 0


def _resolve_skill_root(*, repo_dir: Path, commit: str, skill_name: str) -> str:
    candidates = [f"{skill_name}/SKILL.md", f"skills/{skill_name}/SKILL.md"]
    for c in candidates:
        if _git_has_path(repo_dir=repo_dir, commit=commit, path=c):
            return c[: -len("/SKILL.md")]
    raise InstallError(
        f"Skill '{skill_name}' not found at '{skill_name}/SKILL.md' or 'skills/{skill_name}/SKILL.md' in commit {commit}"
    )


def _git_list_files(*, repo_dir: Path, commit: str, root: str) -> list[str]:
    out = _run_git(["ls-tree", "-r", "--name-only", commit, root], cwd=repo_dir)
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return files


def _git_read_file(*, repo_dir: Path, commit: str, path: str) -> bytes:
    p = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=str(repo_dir),
        capture_output=True,
    )
    if p.returncode != 0:
        raise InstallError(f"git show failed for {commit}:{path}")
    return p.stdout


def _write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _install_skill(
    *,
    repo_cache_root: Path,
    dest_root: Path,
    allowlist_domains: set[str],
    lock: SkillLock,
) -> None:
    if "@" not in lock.ref:
        raise InstallError(f"Invalid ref (expected owner/repo@commit): {lock.ref!r}")
    repo_part, commit = lock.ref.rsplit("@", 1)
    if "/" not in repo_part:
        raise InstallError(f"Invalid ref (expected owner/repo@commit): {lock.ref!r}")
    owner, repo = repo_part.split("/", 1)
    owner = owner.strip()
    repo = repo.strip()
    commit = commit.strip().lower()
    if not owner or not repo or not commit:
        raise InstallError(f"Invalid ref (expected owner/repo@commit): {lock.ref!r}")

    repo_dir = _ensure_repo(cache_root=repo_cache_root, owner=owner, repo=repo)
    _fetch_commit(repo_dir=repo_dir, commit=commit)

    skill_root = _resolve_skill_root(repo_dir=repo_dir, commit=commit, skill_name=lock.name)
    files = _git_list_files(repo_dir=repo_dir, commit=commit, root=skill_root)
    if not files:
        raise InstallError(f"No files found under skill root '{skill_root}'")

    # Materialize to a temp dir so we can compute hash + scan.
    with tempfile.TemporaryDirectory() as td:
        td_root = Path(td) / lock.name
        for p in files:
            rel = Path(p).relative_to(skill_root)
            data = _git_read_file(repo_dir=repo_dir, commit=commit, path=p)
            _write_bytes(td_root / rel, data)

        computed = sha256_tree(td_root)
        expected = lock.sha256.lower()
        if computed != expected:
            raise InstallError(
                f"sha256 mismatch for skill {lock.name!r}: expected {expected}, got {computed}"
            )

        findings = scan_skill_dir(root=td_root, allowlist_domains=allowlist_domains)
        high = [f for f in findings if f.severity == "HIGH"]
        if high:
            msg = "\n".join(f"{f.severity}: {f.file}: {f.rule}: {f.message}" for f in high[:20])
            raise InstallError(
                f"Security scan failed for skill {lock.name!r} (HIGH findings).\n{msg}\n"
                "If you trust this skill, you must explicitly waive scanning (not supported by default policy)."
            )

        dest_dir = dest_root / lock.name
        if dest_dir.exists():
            try:
                existing = sha256_tree(dest_dir)
            except Exception:
                existing = None
            if existing == expected:
                print(f"SKIP  {lock.name} (already matches lock)")
                return

            ts = time.strftime("%Y%m%d%H%M%S")
            bak = dest_root / f"{lock.name}.bak.{ts}"
            dest_dir.rename(bak)
            print(f"UPDATE {lock.name} (backed up to {bak.name})")

        shutil.copytree(td_root, dest_dir, dirs_exist_ok=False)
        print(f"INSTALL {lock.name}")


def _load_allowlist_domains(global_sources_path: Path) -> set[str]:
    obj = _load_json(global_sources_path)
    policy = obj.get("policy")
    if not isinstance(policy, dict):
        raise InstallError("global.sources.json: policy must be an object")
    allowlist = policy.get("allowlistDomains")
    if not isinstance(allowlist, list) or not all(isinstance(x, str) for x in allowlist):
        raise InstallError("global.sources.json: policy.allowlistDomains must be a list of strings")
    return {d.lower() for d in allowlist}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Install external Agent Skills with strict pin+hash validation and basic security scanning."
    )
    ap.add_argument(
        "--global-sources",
        default=str(Path(__file__).resolve().parents[1] / "skill-sources" / "global.sources.json"),
        help="Path to global.sources.json (default: repo skill-sources/global.sources.json)",
    )
    ap.add_argument("--project-sources", required=True, help="Path to project .opencode/skill-sources.json")
    ap.add_argument("--project-lock", required=True, help="Path to project .opencode/skills.lock.json")
    ap.add_argument(
        "--dest",
        help="Destination dir to install skills into (default: <project-root>/.opencode/skills)",
    )
    ap.add_argument(
        "--project-root",
        help="Project root; used to default dest to .opencode/skills",
    )
    ap.add_argument(
        "--repo-cache",
        default=str(Path.home() / ".config" / "opencode" / "skill-repos"),
        help="Local git repo cache directory",
    )
    args = ap.parse_args(argv)

    if shutil.which("git") is None:
        print("ERROR: git is required to install external skills", file=sys.stderr)
        return 2

    global_sources_path = Path(args.global_sources)
    project_sources_path = Path(args.project_sources)
    project_lock_path = Path(args.project_lock)
    global_lock_path: Optional[Path] = None

    allowlist_domains = _load_allowlist_domains(global_sources_path)

    dest: Optional[Path]
    if args.dest:
        dest = Path(args.dest)
    elif args.project_root:
        dest = Path(args.project_root) / ".opencode" / "skills"
    else:
        raise SystemExit("ERROR: provide --dest or --project-root")

    repo_cache_root = Path(args.repo_cache)
    repo_cache_root.mkdir(parents=True, exist_ok=True)
    dest.mkdir(parents=True, exist_ok=True)

    # Enforce policy: sources + locks must validate, and lock is required.
    try:
        validate_sources_and_locks(
            global_path=global_sources_path,
            project_path=project_sources_path,
            global_lock_path=global_lock_path,
            project_lock_path=project_lock_path,
            require_lock=True,
        )
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        return 2

    try:
        locks = _parse_lock(project_lock_path)
        for lock in locks:
            _install_skill(
                repo_cache_root=repo_cache_root,
                dest_root=dest,
                allowlist_domains=allowlist_domains,
                lock=lock,
            )
    except InstallError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
