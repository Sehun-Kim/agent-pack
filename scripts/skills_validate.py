#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


class ValidationError(Exception):
    pass


@dataclass(frozen=True)
class SourcesManifest:
    version: int
    allowlist_domains: set[str]
    sources: list[dict]


@dataclass(frozen=True)
class LockManifest:
    version: int
    skills: list[dict]


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise ValidationError(f"File not found: {path}") from e
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {path}: {e}") from e


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError(f"Invalid url (expected scheme+host): {url!r}")
    return parsed.netloc.lower()


def _parse_manifest(obj: dict, *, label: str) -> SourcesManifest:
    if not isinstance(obj, dict):
        raise ValidationError(f"{label}: expected object")

    version = obj.get("version")
    if version != 1:
        raise ValidationError(f"{label}: unsupported version: {version!r} (expected 1)")

    policy = obj.get("policy")
    if not isinstance(policy, dict):
        raise ValidationError(f"{label}: policy must be an object")

    mode = policy.get("mode")
    if mode != "allowlist":
        raise ValidationError(f"{label}: policy.mode must be 'allowlist' (got {mode!r})")

    allowlist = policy.get("allowlistDomains")
    if not isinstance(allowlist, list) or not all(isinstance(x, str) for x in allowlist):
        raise ValidationError(f"{label}: policy.allowlistDomains must be a list of strings")

    sources = obj.get("sources")
    if not isinstance(sources, list) or not all(isinstance(x, dict) for x in sources):
        raise ValidationError(f"{label}: sources must be a list of objects")

    return SourcesManifest(
        version=version,
        allowlist_domains={d.lower() for d in allowlist},
        sources=sources,
    )


def _parse_lock(obj: dict, *, label: str) -> LockManifest:
    if not isinstance(obj, dict):
        raise ValidationError(f"{label}: expected object")

    version = obj.get("version")
    if version != 1:
        raise ValidationError(f"{label}: unsupported version: {version!r} (expected 1)")

    skills = obj.get("skills")
    if not isinstance(skills, list) or not all(isinstance(x, dict) for x in skills):
        raise ValidationError(f"{label}: skills must be a list of objects")

    return LockManifest(version=version, skills=skills)


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _source_ids(manifest: SourcesManifest) -> set[str]:
    ids: set[str] = set()
    for idx, src in enumerate(manifest.sources):
        src_id = src.get("id")
        if not isinstance(src_id, str) or not src_id.strip():
            raise ValidationError(f"sources[{idx}].id must be a non-empty string")
        if src_id in ids:
            raise ValidationError(f"duplicate source id: {src_id!r}")
        ids.add(src_id)
    return ids


def _source_domain_by_id(manifest: SourcesManifest) -> dict[str, str]:
    by_id: dict[str, str] = {}
    for idx, src in enumerate(manifest.sources):
        src_id = src.get("id")
        url = src.get("url")
        if not isinstance(src_id, str) or not src_id.strip():
            raise ValidationError(f"sources[{idx}].id must be a non-empty string")
        if not isinstance(url, str) or not url.strip():
            raise ValidationError(f"sources[{idx}].url must be a non-empty string")
        by_id[src_id] = _domain_from_url(url)
    return by_id


def _validate_lock(
    *,
    lock: LockManifest,
    label: str,
    allowed_source_ids: set[str],
    allowed_source_domains: set[str],
    source_domain_by_id: dict[str, str],
) -> None:
    seen_names: set[str] = set()
    for idx, item in enumerate(lock.skills):
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValidationError(f"{label}.skills[{idx}].name must be a non-empty string")
        if name in seen_names:
            raise ValidationError(f"{label}.skills[{idx}].name duplicates existing entry: {name!r}")
        seen_names.add(name)

        source_id = item.get("sourceId")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ValidationError(f"{label}.skills[{idx}].sourceId must be a non-empty string")
        if source_id not in allowed_source_ids:
            raise ValidationError(
                f"{label}.skills[{idx}].sourceId {source_id!r} is not defined in sources (global or project)"
            )

        src_domain = source_domain_by_id.get(source_id)
        if not src_domain:
            raise ValidationError(
                f"{label}.skills[{idx}].sourceId {source_id!r} does not have a resolvable source domain"
            )
        if src_domain not in allowed_source_domains:
            raise ValidationError(
                f"{label}.skills[{idx}].sourceId domain '{src_domain}' is not in the global allowlistDomains"
            )

        ref = item.get("ref")
        if not isinstance(ref, str) or not ref.strip():
            raise ValidationError(f"{label}.skills[{idx}].ref must be a non-empty string")
        if "@" not in ref:
            raise ValidationError(
                f"{label}.skills[{idx}].ref must be pinned in the form 'owner/repo@<40-hex-commit>' (got {ref!r})"
            )
        repo_part, commit_part = ref.rsplit("@", 1)
        if not repo_part or "/" not in repo_part:
            raise ValidationError(
                f"{label}.skills[{idx}].ref must look like 'owner/repo@<commit>' (got {ref!r})"
            )
        if not _GIT_COMMIT_RE.fullmatch(commit_part.lower()):
            raise ValidationError(
                f"{label}.skills[{idx}].ref must be pinned to a 40-hex git commit (got {commit_part!r})"
            )

        sha256 = item.get("sha256")
        if not isinstance(sha256, str) or not sha256.strip():
            raise ValidationError(f"{label}.skills[{idx}].sha256 is required and must be a hex string")
        if not _SHA256_RE.fullmatch(sha256.lower()):
            raise ValidationError(
                f"{label}.skills[{idx}].sha256 must be 64 lowercase hex chars (got {sha256!r})"
            )


def validate(
    *,
    global_path: Path,
    project_path: Path,
    global_lock_path: Optional[Path],
    project_lock_path: Optional[Path],
    require_lock: bool,
) -> None:
    global_obj = _load_json(global_path)
    project_obj = _load_json(project_path)

    global_m = _parse_manifest(global_obj, label="global")
    project_m = _parse_manifest(project_obj, label="project")

    # Option A: project cannot expand trust
    missing = project_m.allowlist_domains - global_m.allowlist_domains
    if missing:
        raise ValidationError(
            "project.allowlistDomains must be a subset of global.allowlistDomains. "
            f"Not allowed: {sorted(missing)}"
        )

    # Every project source url must be globally allowed
    for idx, src in enumerate(project_m.sources):
        url = src.get("url")
        if not isinstance(url, str):
            raise ValidationError(f"project.sources[{idx}].url must be a string")
        domain = _domain_from_url(url)
        if domain not in global_m.allowlist_domains:
            raise ValidationError(
                f"project.sources[{idx}].url domain '{domain}' is not in global.allowlistDomains"
            )

    if require_lock and (global_lock_path is None and project_lock_path is None):
        raise ValidationError(
            "Lock validation required, but no lock file was provided. "
            "Pass --project-lock (and optionally --global-lock)."
        )

    allowed_source_domains = set(global_m.allowlist_domains)
    combined_source_ids = _source_ids(global_m) | _source_ids(project_m)
    domain_by_id = _source_domain_by_id(global_m)
    domain_by_id.update(_source_domain_by_id(project_m))

    if global_lock_path is not None:
        global_lock_obj = _load_json(global_lock_path)
        global_lock = _parse_lock(global_lock_obj, label="global-lock")
        _validate_lock(
            lock=global_lock,
            label="global-lock",
            allowed_source_ids=combined_source_ids,
            allowed_source_domains=allowed_source_domains,
            source_domain_by_id=domain_by_id,
        )

    if project_lock_path is not None:
        project_lock_obj = _load_json(project_lock_path)
        project_lock = _parse_lock(project_lock_obj, label="project-lock")
        _validate_lock(
            lock=project_lock,
            label="project-lock",
            allowed_source_ids=combined_source_ids,
            allowed_source_domains=allowed_source_domains,
            source_domain_by_id=domain_by_id,
        )


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Validate project external-skill sources against global policy.")
    p.add_argument("--global", dest="global_path", required=True, help="Path to global.sources.json")
    p.add_argument("--project", dest="project_path", required=True, help="Path to project skill-sources.json")
    p.add_argument("--global-lock", dest="global_lock_path", help="Path to global skills lock json")
    p.add_argument("--project-lock", dest="project_lock_path", help="Path to project skills lock json")
    p.add_argument(
        "--require-lock",
        action="store_true",
        help="Fail validation if no lock file is provided (recommended for secure setups).",
    )
    args = p.parse_args(argv)

    try:
        validate(
            global_path=Path(args.global_path),
            project_path=Path(args.project_path),
            global_lock_path=Path(args.global_lock_path) if args.global_lock_path else None,
            project_lock_path=Path(args.project_lock_path) if args.project_lock_path else None,
            require_lock=bool(args.require_lock),
        )
    except ValidationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
