#!/usr/bin/env python3
"""Pre-check-in gate runner. Copy into a project as scripts/precheckin and configure precheckin.toml.

  scripts/precheckin                 full gate (before push, review, and merge)
  scripts/precheckin --fast          per-commit subset: staged secrets, format, lint
  scripts/precheckin --install-hooks write .git/hooks/pre-commit (--fast) and pre-push (full)
  scripts/precheckin --json FILE     also write the results as JSON

Deterministic tools decide. A missing tool is NOT RUN, never a pass, and blocks unless the
owner waived that check (with an expiry) in precheckin.toml. Exit 0 pass, 1 blocked.
Python 3.11+ standard library only.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path.cwd()
PASS, WARN, BLOCK, NOTRUN, NA, WAIVED = "pass", "warn", "BLOCK", "NOT RUN", "n/a", "waived"
SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("private key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Slack token", re.compile(r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe live key", re.compile(r"\bsk_live_[A-Za-z0-9]{20,}\b")),
]


def sh(cmd):
    r = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def tail(text, n=6):
    return "\n".join(text.splitlines()[-n:])


def mask(s):
    return s[:4] + "..." + s[-2:] if len(s) > 8 else "***"


def builtin_secret_scan(fast):
    """Pattern scan of staged diff (fast) or tracked files (full). Never prints a full secret."""
    if fast:
        _, text = sh("git diff --cached -U0 --no-color")
        sources = [("staged diff", text)]
    else:
        _, files = sh("git ls-files")
        sources = []
        for f in files.splitlines():
            p = ROOT / f
            if p.is_file() and p.stat().st_size < 1_000_000:
                try:
                    sources.append((f, p.read_text(errors="ignore")))
                except OSError:
                    pass
    hits = []
    for where, text in sources:
        for name, rx in SECRET_PATTERNS:
            for m in rx.finditer(text):
                hits.append(f"{name} in {where}: {mask(m.group(0))}")
    return hits


def check_secrets(fast):
    hits = builtin_secret_scan(fast)
    results = []
    if hits:
        results.append(("secrets (built-in patterns)", BLOCK, "; ".join(hits[:5])))
    else:
        results.append(("secrets (built-in patterns)", PASS, "no high-confidence patterns"))
    if shutil.which("gitleaks"):
        cmd = "gitleaks protect --staged --no-banner --redact" if fast else "gitleaks detect --source . --no-banner --redact"
        code, out = sh(cmd)
        results.append(("secrets (gitleaks)", PASS if code == 0 else BLOCK, tail(out, 3)))
    else:
        results.append(("secrets (gitleaks)", NOTRUN, "gitleaks missing: brew install gitleaks"))
    return results


def check_deps():
    if shutil.which("osv-scanner"):
        code, out = sh("osv-scanner scan source -r .")
        return [("dependencies (osv-scanner)", PASS if code == 0 else BLOCK, tail(out))]
    out = []
    if (ROOT / "package-lock.json").exists():
        code, text = sh("npm audit --json")
        try:
            vulns = json.loads(text).get("vulnerabilities", {})
        except json.JSONDecodeError:
            return [("dependencies (npm audit)", NOTRUN, "npm audit gave no JSON: " + tail(text, 2))]
        bad = [n for n, v in vulns.items() if v.get("severity") in ("high", "critical") and v.get("fixAvailable")]
        low = [n for n in vulns if n not in bad]
        status = BLOCK if bad else (WARN if low else PASS)
        detail = f"high/critical with fix: {bad}" if bad else (f"other findings: {low}" if low else "no known vulnerabilities")
        out.append(("dependencies (npm audit; osv-scanner missing)", status, detail))
    if (ROOT / "requirements.txt").exists():
        if shutil.which("pip-audit"):
            code, text = sh("pip-audit -r requirements.txt")
            out.append(("dependencies (pip-audit)", PASS if code == 0 else BLOCK, tail(text)))
        else:
            out.append(("dependencies (pip-audit)", NOTRUN, "pip-audit missing"))
    return out or [("dependencies", NOTRUN, "osv-scanner missing and no npm/pip lockfile: brew install osv-scanner")]


def check_sast():
    if not shutil.which("semgrep"):
        return [("static analysis (semgrep)", NOTRUN, "semgrep missing: brew install semgrep")]
    code, out = sh("semgrep scan --config p/default --error --metrics=off --quiet")
    return [("static analysis (semgrep)", PASS if code == 0 else BLOCK, tail(out))]


def check_licenses(cfg):
    lock = ROOT / "package-lock.json"
    if not lock.exists():
        return [("licences", NA if not (ROOT / "package.json").exists() else NOTRUN, "no package-lock.json")]
    lic = cfg.get("licenses", {})
    allow = set(lic.get("allow", []))
    deny = set(lic.get("deny", []))
    pkgs = json.loads(lock.read_text()).get("packages", {})
    denied, unknown = [], []
    for path, meta in pkgs.items():
        if not path or meta.get("dev"):
            continue
        name = path.split("node_modules/")[-1]
        val = meta.get("license")
        if not val:
            pj = ROOT / path / "package.json"
            if pj.exists():
                val = json.loads(pj.read_text()).get("license")
        val = val if isinstance(val, str) else None
        parts = set(re.split(r"\s+(?:OR|AND)\s+|[()]", val or "")) - {""}
        if parts & deny:
            denied.append(f"{name} ({val})")
        elif not parts or not parts <= allow:
            unknown.append(f"{name} ({val})")
    status = BLOCK if denied else (WARN if unknown else PASS)
    detail = f"disallowed: {denied}" if denied else (f"unknown: {unknown[:8]}" if unknown else "all production licences allowed")
    return [("licences", status, detail)]


def check_cmd(cfg, key, label, fix_key=None):
    cmd = cfg.get("project", {}).get(key, "")
    if cmd.startswith("none:"):
        return [(label, NA, cmd)]
    if not cmd:
        return [(label, NOTRUN, f"no '{key}' command in precheckin.toml")]
    if fix_key and cfg["project"].get(fix_key):
        sh(cfg["project"][fix_key])
    code, out = sh(cmd)
    return [(label, PASS if code == 0 else BLOCK, tail(out) if code else "ok")]


def apply_waivers(cfg, results):
    today = dt.date.today()
    waivers = cfg.get("waivers", [])
    out = []
    for name, status, detail in results:
        if status in (BLOCK, NOTRUN):
            for w in waivers:
                exp = dt.date.fromisoformat(str(w.get("expires", "1970-01-01")))
                if w.get("check") and w["check"] in name and w.get("words") and w.get("by") and exp >= today:
                    status, detail = WAIVED, f"{detail} | waived until {exp} by {w['by']}: \"{w['words']}\""
                    break
        out.append((name, status, detail))
    return out


def install_hooks():
    # Resolve the repository's own hooks dir; ignore config injected through the environment
    # (a supervising wrapper's core.hooksPath), which is not ours to write into.
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
           and k not in ("GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS")}
    r = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-path", "hooks"],
                       cwd=ROOT, env=env, capture_output=True, text=True, check=True)
    hooks = Path(r.stdout.strip())
    hooks.mkdir(parents=True, exist_ok=True)
    for hook, flag in (("pre-commit", " --fast"), ("pre-push", "")):
        p = hooks / hook
        p.write_text(f"#!/bin/sh\nexec python3 scripts/precheckin{flag}\n")
        p.chmod(0o755)
        print(f"installed {p}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--install-hooks", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    if a.install_hooks:
        install_hooks()
        return
    cfg_path = ROOT / "precheckin.toml"
    if not cfg_path.exists():
        print("precheckin.toml missing: the gate is NOT RUN (blocking). Copy the template from the skill's assets.")
        sys.exit(1)
    cfg = tomllib.loads(cfg_path.read_text())
    results = check_secrets(a.fast)
    results += check_cmd(cfg, "format", "format", "format_fix")
    results += check_cmd(cfg, "lint", "lint")
    if not a.fast:
        results += check_deps() + check_sast() + check_licenses(cfg)
        results += check_cmd(cfg, "typecheck", "type check")
        results += check_cmd(cfg, "test", "tests")
        results += check_cmd(cfg, "build", "build")
        if cfg.get("project", {}).get("ui_detect"):
            results += check_cmd(cfg, "ui_detect", "UI slop (impeccable detect)")
    results = apply_waivers(cfg, results)
    width = max(len(r[0]) for r in results)
    print(f"Pre-check-in gate ({'fast' if a.fast else 'full'}) - {dt.datetime.now():%Y-%m-%d %H:%M}")
    for name, status, detail in results:
        first = (detail.splitlines() or [""])[0]
        print(f"  {name.ljust(width)}  {status:8}  {first[:160]}")
    blocked = [r for r in results if r[1] in (BLOCK, NOTRUN)]
    if a.json:
        Path(a.json).write_text(json.dumps([dict(check=n, status=s, detail=d) for n, s, d in results], indent=2))
    print("RESULT: " + ("BLOCKED - fix, or ask the owner for a waiver (S17)" if blocked else "PASS"))
    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
