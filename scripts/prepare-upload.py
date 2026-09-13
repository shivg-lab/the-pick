"""Audit the current Git file set and package it without exposing matched secrets."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
SENSITIVE_NAME = re.compile(r"api.?key|secret|token|password|passwd|private.?key", re.I)
PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "AWS access key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "Google API key": re.compile(rb"\bAIza[A-Za-z0-9_-]{35}\b"),
    "Slack token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "API token": re.compile(rb"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}\b"),
    "credential in URL": re.compile(rb"https?://[^\s/:\"'<>]+:[^\s/@\"'<>]+@"),
    "literal credential": re.compile(
        rb"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        rb"[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_+/=.-]{20,}[\"']"),
}


def git(*args, **kwargs):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=True, **kwargs).stdout


def env_pairs(path):
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        yield key.strip(), value.strip().strip("\"'")


def main():
    paths = sorted(set(p.decode() for p in git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p))
    if not paths:
        raise ValueError("No upload files found. Initialize Git in the project first.")
    # --no-index also identifies ignored files that might have been force-added.
    ignored = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "--no-index", "--stdin", "-z"],
        input=b"\0".join(p.encode() for p in paths)+b"\0", capture_output=True)
    if ignored.returncode not in (0, 1):
        raise ValueError("Could not verify ignore rules.")
    findings = [{"file": p.decode(), "reason": "ignored file was explicitly tracked"}
                for p in ignored.stdout.split(b"\0") if p]
    # Read credentials only in memory; never include their names or values in output.
    known = set()
    for folder in (ROOT, ROOT / "frontend", ROOT / "backend"):
        for env in folder.glob(".env*"):
            if not env.is_file() or env.name == ".env.example":
                continue
            for key, value in env_pairs(env):
                if SENSITIVE_NAME.search(key) and len(value) >= 8:
                    known.add(value.encode())
                    known.add(quote(value, safe="").encode())
    total = 0
    for name in paths:
        path = ROOT / name
        if path.is_symlink() or not path.is_file():
            findings.append({"file": name, "reason": "symlink or non-file requires review"})
            continue
        if path.stat().st_size >= 100_000_000:
            findings.append({"file": name, "reason": "file exceeds upload size budget"})
        data = path.read_bytes()
        total += len(data)
        for secret in known:
            if secret in data:
                findings.append({"file": name, "reason": "matches a local credential"})
                break
        # Binary assets are checked against known credentials above; text also gets pattern checks.
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            match = pattern.search(data)
            if match:
                findings.append({"file": name, "line": data[:match.start()].count(b"\n")+1, "reason": label})
        if path.name == ".env.example":
            for key, value in env_pairs(path):
                if SENSITIVE_NAME.search(key) and value:
                    findings.append({"file": name, "reason": "credential field in public template is not blank"})
    required = {".env.example", "README.md", "backend/uv.lock", "frontend/package-lock.json",
                "docs/diagrams/the-pick-architecture.png", "docs/demo-video-v4/the-pick-demo.mp4"}
    for missing in sorted(required - set(paths)):
        findings.append({"file": missing, "reason": "required upload asset missing"})
    if findings:
        print(json.dumps({"passed": False, "findings": findings}, indent=2))
        return 1
    OUT.mkdir(exist_ok=True)
    destination = OUT / "Team-10-Project.zip"
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for name in paths:
            archive.write(ROOT / name, f"Team-10-Project/{name}")
    with ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive integrity check failed.")
        assert len(archive.namelist()) == len(paths)
    report = {
        "passed": True, "files": len(paths), "uncompressed_bytes": total,
        "archive": destination.name, "archive_bytes": destination.stat().st_size,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "checks": ["Git ignore rules including tracked files", "known local credentials",
                   "common secret patterns", "blank public credential template", "archive integrity"],
        "scope": "Current upload files only; not Git history. Pattern checks cannot prove absence of every possible secret.",
    }
    (OUT / "upload-audit.json").write_text(json.dumps(report, indent=2)+"\n")
    (OUT / "upload-manifest.txt").write_text("\n".join(paths)+"\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
