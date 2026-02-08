#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class ScanError(Exception):
    pass


@dataclass(frozen=True)
class Finding:
    severity: str  # HIGH | MEDIUM | LOW
    file: str
    rule: str
    message: str


_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "prompt-injection-bypass",
        re.compile(
            r"(?i)(ignore (all )?(previous|prior) (instructions|rules)|"
            r"override (the )?(system|developer) (prompt|message)|"
            r"you are now (system|developer)|"
            r"act as (the )?(system|developer))"
        ),
    ),
    ("exfiltration-language", re.compile(r"(?i)(exfiltrate|steal|leak|send (it|them) to|upload to|webhook)")),
]

_SENSITIVE_HANDLING_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "secrets-in-plaintext",
        re.compile(r"(?i)(save|store).*(api key|token|secret|password|private key|cvc|credit card).*\b(plain\s*text|plaintext)"),
    ),
    (
        "print-secrets",
        re.compile(r"(?i)(print|echo|output|show).*(api key|token|secret|password|private key|cvc|credit card)"),
    ),
]

_MALWARE_LIKE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("pipe-to-shell", re.compile(r"(?i)(curl|wget).*(\|\s*)\s*(sh|bash)\b")),
    ("rm-rf", re.compile(r"(?i)\brm\s+-rf\b")),
    ("sudo", re.compile(r"(?i)\bsudo\b")),
    ("ssh-private-key", re.compile(r"(?i)(id_rsa|id_ed25519|~/.ssh)")),
    ("aws-credentials", re.compile(r"(?i)(~/.aws/credentials|aws_secret_access_key)")),
    ("dotenv", re.compile(r"(?i)\b\.env\b")),
]

_NETWORK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("network-curl", re.compile(r"(?i)\bcurl\b")),
    ("network-wget", re.compile(r"(?i)\bwget\b")),
    ("network-nc", re.compile(r"(?i)\b(nc|netcat)\b")),
]

_URL_RE = re.compile(r"https?://([A-Za-z0-9.-]+)(?::\d+)?")
_NETWORK_LINE_HINT = re.compile(r"(?i)\b(curl|wget|npm\s+install|npx\s+|pip\s+install|git\s+clone)\b")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # noqa: BLE001
        raise ScanError(f"Failed to read {path}: {e}") from e


def _iter_candidate_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        # Scan text-ish files. (Binary files are skipped by extension.)
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".bz2", ".xz", ".bin"}:
            continue
        yield p


def scan_skill_dir(*, root: Path, allowlist_domains: set[str]) -> list[Finding]:
    if not root.exists() or not root.is_dir():
        raise ScanError(f"Not a directory: {root}")

    findings: list[Finding] = []
    for p in _iter_candidate_files(root):
        text = _read_text(p)
        rel = p.relative_to(root).as_posix()

        lines = text.splitlines() or [text]

        is_script_like = p.suffix.lower() in {".sh", ".bash", ".zsh", ".py", ".js", ".ts"}

        # URLs to non-allowlisted domains are HIGH.
        for line in lines:
            for m in _URL_RE.finditer(line):
                domain = m.group(1).lower().strip().strip(". ")
                if domain in allowlist_domains:
                    continue
                # Heuristic severity: docs links in .md are LOW unless paired with a network command.
                severity = "HIGH" if is_script_like else "LOW"
                if _NETWORK_LINE_HINT.search(line):
                    severity = "HIGH"
                findings.append(
                    Finding(
                        severity=severity,
                        file=rel,
                        rule="url-domain-not-allowlisted",
                        message=f"Found URL domain '{domain}' not in allowlist",
                    )
                )

        for rule, pat in _INJECTION_PATTERNS:
            if pat.search(text):
                findings.append(
                    Finding(
                        severity="HIGH",
                        file=rel,
                        rule=rule,
                        message="Contains prompt-injection / bypass language",
                    )
                )

        for rule, pat in _SENSITIVE_HANDLING_PATTERNS:
            if pat.search(text):
                findings.append(
                    Finding(
                        severity="HIGH",
                        file=rel,
                        rule=rule,
                        message="Appears to instruct unsafe secret handling",
                    )
                )

        for rule, pat in _MALWARE_LIKE_PATTERNS:
            if pat.search(text):
                findings.append(
                    Finding(
                        severity="HIGH",
                        file=rel,
                        rule=rule,
                        message="Contains potentially dangerous command / credential targeting pattern",
                    )
                )

        for rule, pat in _NETWORK_PATTERNS:
            if pat.search(text):
                findings.append(
                    Finding(
                        severity="MEDIUM",
                        file=rel,
                        rule=rule,
                        message="Contains network-capable command reference",
                    )
                )

    # Deduplicate exact duplicates
    uniq: dict[tuple[str, str, str], Finding] = {}
    for f in findings:
        uniq[(f.severity, f.file, f.rule)] = f
    out = list(uniq.values())
    out.sort(key=lambda f: (f.severity, f.file, f.rule))
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Static scan of an Agent Skill directory for common security issues.")
    ap.add_argument("--root", required=True, help="Path to the skill directory")
    ap.add_argument(
        "--allowlist-domain",
        action="append",
        default=[],
        help="Allowed domain (repeatable). URLs outside are HIGH severity.",
    )
    ap.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )
    ap.add_argument(
        "--fail-on",
        choices=["HIGH", "MEDIUM", "LOW", "NONE"],
        default="HIGH",
        help="Exit non-zero if findings at/above this severity exist",
    )
    args = ap.parse_args(argv)

    allowlist = {d.lower() for d in args.allowlist_domain}
    if not allowlist:
        raise SystemExit("ERROR: at least one --allowlist-domain is required")

    try:
        findings = scan_skill_dir(root=Path(args.root), allowlist_domains=allowlist)
    except ScanError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps([f.__dict__ for f in findings], indent=2, sort_keys=True))
    else:
        if not findings:
            print("OK")
        else:
            for f in findings:
                print(f"{f.severity}: {f.file}: {f.rule}: {f.message}")

    if args.fail_on == "NONE":
        return 0

    order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    threshold = order.get(args.fail_on, 3)
    worst = 0
    for f in findings:
        worst = max(worst, order.get(f.severity, 0))

    return 2 if worst >= threshold else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
