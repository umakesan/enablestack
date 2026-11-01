#!/usr/bin/env python3
"""Run state for the SDLC conductor: gate hashes, checkpoint, in-flight steps, resume check.

state.json in the run store is the machine record; sdlc.md (store) and
docs/sdlc/checkpoint.md (project) are rendered from it. Standard library only.

Exit codes: 0 ok, 2 usage or structural error, 3 stale gate, 4 interrupted in-flight step.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"
CHECKPOINT_REL = Path("docs/sdlc/checkpoint.md")
DECISIONS_REL = Path("docs/business/decisions.md")
GATE_NAMES = {
    "S0": "Gate 0 - business brief",
    "S1": "Gate A - design",
    "S2": "Gate B - plan",
    "S3": "Stack choice",
    "S4": "Visual direction",
    "S5": "Comp pick",
    "S6": "Approach pick",
    "S7": "Design section",
    "S8": "Merge",
    "S16": "UAT acceptance",
    "S17": "Waiver",
}


def now():
    return dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


def die(msg, code=2) -> NoReturn:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def store_root():
    return Path(os.environ.get("SDLC_STORE_ROOT", Path.home() / ".claude" / "orchestrate"))


def normalized_hash(path):
    """SHA-256 over text with CRLF->LF, trailing spaces and trailing blank lines removed."""
    data = Path(path).read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(data).hexdigest()
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def resolve_artifact(project, artifact):
    p = Path(os.path.expanduser(artifact))
    return p if p.is_absolute() else Path(project) / p


def git(project, *args):
    r = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def find_store(project):
    cp = Path(project) / CHECKPOINT_REL
    if not cp.exists():
        die(f"no checkpoint at {cp}; run `init` first or pass the right --project")
    m = re.search(r"^Store: (.+)$", cp.read_text(), re.MULTILINE)
    if not m:
        die(f"{cp} has no 'Store:' line; checkpoint is corrupt - stop and report, never reconstruct")
    store = Path(os.path.expanduser(m.group(1).strip()))
    if not (store / "state.json").exists():
        die(f"store {store} has no state.json; checkpoint points at a missing store")
    return store


def load(project):
    store = find_store(project)
    return store, json.loads((store / "state.json").read_text())


def save(store, state, project):
    (store / "state.json").write_text(json.dumps(state, indent=2) + "\n")
    render(store, state, project)


def gate_lines(state):
    out = []
    for gid, g in state["gates"].items():
        name = GATE_NAMES.get(gid.split(":")[0], gid)
        out.append(
            f"- {gid} {name}: {g['artifact']} - sha256 {g['sha256'][:12]} - approved {g['date']} "
            f"by {g['by']} via {g['channel']}: \"{g['words']}\""
        )
    return "\n".join(out) or "- (none approved yet)"


def render(store, state, project):
    project = Path(project)
    inflight = state.get("inflight", {})
    units = state.get("units", {})
    parked = state.get("parked")
    branch = git(project, "rev-parse", "--abbrev-ref", "HEAD") or "(not a git repo)"
    head = git(project, "log", "-1", "--format=%h %s") or "(no commits)"
    fields = {
        "TITLE": state["title"],
        "STATUS": f"Parked: {parked['at']} by {parked['by']} (\"{parked['reason']}\")" if parked else f"Active (last saved {now()})",
        "PHASE": state["phase"],
        "NEXT": state.get("next") or "(see phase map)",
        "SIZE": state["size"],
        "UI": state["ui"],
        "STORE": str(store),
        "GATES": gate_lines(state),
        "MADE": "\n".join(f"- {k}: {v}" for k, v in state.get("made", {}).items()) or "- (nothing yet)",
        "QUESTION": state.get("open_question") or "(none)",
        "DECISIONS": last_decision(project),
        "UNITS": "\n".join(f"- {u}: {d['status']}" + (f" ({d['commit']})" if d.get("commit") else "") for u, d in units.items()) or "- none yet",
        "INFLIGHT": "\n".join(f"- {k}: started {v['started']} - {v.get('detail', '')}" for k, v in inflight.items()) or "- none",
        "GIT": f"branch {branch}; last commit {head}",
        "VERSIONS": ", ".join(f"{k} {v}" for k, v in state.get("versions", {}).items()) or "(not recorded)",
        "HISTORY": "\n".join(f"- {h}" for h in state.get("history", [])[-8:]) or "- (none)",
    }
    tpl = (ASSETS / "checkpoint.md").read_text()
    for k, v in fields.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    cp = project / CHECKPOINT_REL
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(tpl)
    (store / "sdlc.md").write_text(
        f"# SDLC run state - {state['title']}\n\nGenerated from state.json; do not edit.\n\n"
        f"- Project: {project}\n- Phase: {state['phase']}\n- Size: {state['size']} - UI: {state['ui']}\n\n"
        f"## Gates\n{fields['GATES']}\n\n## In flight\n{fields['INFLIGHT']}\n\n## Units\n{fields['UNITS']}\n"
    )


def last_decision(project):
    p = Path(project) / DECISIONS_REL
    if not p.exists():
        return "- (no decision log yet)"
    ids = re.findall(r"^## (BD-\d+)", p.read_text(), re.MULTILINE)
    return f"- {len(ids)} entries, last {ids[-1]} ({DECISIONS_REL})" if ids else "- (empty)"


def log(state, line):
    state.setdefault("history", []).append(f"{now()} {line}")


def preflight_versions():
    r = subprocess.run([str(SKILL_DIR / "scripts" / "preflight.sh"), "--versions"], capture_output=True, text=True)
    out = {}
    for ln in r.stdout.splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            out[k] = v
    return out


def cmd_init(a):
    project = Path(a.project).resolve()
    if (project / CHECKPOINT_REL).exists():
        die(f"{project / CHECKPOINT_REL} already exists; this is a resume, run `check`")
    store = (Path(a.store_root).expanduser() if a.store_root else store_root()) / a.slug
    store.mkdir(parents=True, exist_ok=True)
    for sub in ("boards", "uat", "prototype", "arena"):
        (store / sub).mkdir(exist_ok=True)
    if not (store / "routing.tsv").exists():
        (store / "routing.tsv").write_text((ASSETS / "routing-ledger-header.tsv").read_text())
    if not (store / "grill.md").exists():
        (store / "grill.md").write_text((ASSETS / "grill-ledger.md").read_text())
    state = {
        "slug": a.slug, "title": a.title, "project": str(project), "size": a.size, "ui": a.ui,
        "phase": "sized", "gates": {}, "inflight": {}, "units": {}, "made": {},
        "versions": preflight_versions(), "created": now(),
    }
    log(state, f"init size={a.size} ui={a.ui}")
    save(store, state, project)
    print(f"store: {store}\ncheckpoint: {project / CHECKPOINT_REL}")


def cmd_phase(a):
    store, state = load(a.project)
    state["phase"] = a.state
    if a.next is not None:
        state["next"] = a.next
    if a.question is not None:
        state["open_question"] = a.question or None
    log(state, f"phase -> {a.state}")
    save(store, state, a.project)
    print(f"phase: {a.state}")


def cmd_approve(a):
    store, state = load(a.project)
    path = resolve_artifact(a.project, a.artifact)
    if not path.exists():
        die(f"artifact {path} does not exist")
    if not a.words.strip():
        die("approval needs the approver's exact words")
    if a.by.strip().lower() in ("agent", "assistant", "claude", "my call"):
        die("an agent cannot approve a stop; record the owner's words")
    prev = state["gates"].get(a.gate)
    state["gates"][a.gate] = {
        "artifact": a.artifact, "sha256": normalized_hash(path), "words": a.words.strip(),
        "by": a.by, "channel": a.channel, "date": now(),
    }
    if prev:
        state["gates"][a.gate]["supersedes"] = prev["sha256"]
    if state.get("open_question"):
        state["open_question"] = None
    log(state, f"approve {a.gate} {a.artifact} by {a.by}")
    save(store, state, a.project)
    print(f"{a.gate} approved: sha256 {state['gates'][a.gate]['sha256']}")


def verify_gates(project, state):
    stale = []
    for gid, g in state["gates"].items():
        path = resolve_artifact(project, g["artifact"])
        if not path.exists():
            stale.append((gid, g["artifact"], "missing"))
        elif normalized_hash(path) != g["sha256"]:
            stale.append((gid, g["artifact"], "changed"))
    return stale


def cmd_verify(a):
    _, state = load(a.project)
    stale = verify_gates(a.project, state)
    for gid in state["gates"]:
        hit = next((s for s in stale if s[0] == gid), None)
        print(f"{gid}: {'STALE (' + hit[2] + ')' if hit else 'ok'} {state['gates'][gid]['artifact']}")
    sys.exit(3 if stale else 0)


def cmd_inflight(a):
    store, state = load(a.project)
    if a.action == "begin":
        state["inflight"][a.step] = {"started": now(), "detail": a.detail or ""}
        log(state, f"in-flight begin {a.step}")
    else:
        if a.step not in state["inflight"]:
            die(f"no in-flight step {a.step}")
        del state["inflight"][a.step]
        log(state, f"in-flight end {a.step} outcome={a.outcome}")
    save(store, state, a.project)


def cmd_unit(a):
    store, state = load(a.project)
    state["units"][a.id] = {"status": a.status, "commit": a.commit}
    state["inflight"].pop(a.id, None)
    log(state, f"unit {a.id} {a.status} {a.commit or ''}".strip())
    save(store, state, a.project)


def cmd_made(a):
    store, state = load(a.project)
    path = resolve_artifact(a.project, a.path)
    digest = normalized_hash(path)[:12] if path.exists() else "missing"
    state["made"][a.label] = f"{a.path} - sha256 {digest}"
    save(store, state, a.project)


def cmd_park(a):
    store, state = load(a.project)
    state["parked"] = {"at": now(), "by": a.by, "reason": a.reason}
    if a.next:
        state["next"] = a.next
    log(state, f"parked by {a.by}: {a.reason}")
    save(store, state, a.project)
    print(f"parked; commit {CHECKPOINT_REL} locally (never push)")


def cmd_resume(a):
    store, state = load(a.project)
    was = state.pop("parked", None)
    log(state, "resumed" + (f" (parked {was['at']})" if was else " (after interruption)"))
    save(store, state, a.project)


def cmd_decide(a):
    project = Path(a.project)
    p = project / DECISIONS_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    text = p.read_text() if p.exists() else "# Business decision log\n\nAppend-only. A change adds a new entry that supersedes the old one.\n"
    n = len(re.findall(r"^## BD-\d+", text, re.MULTILINE)) + 1
    entry = (ASSETS / "decision-entry.md").read_text()
    words = f" - \"{a.words}\"" if a.words else ""
    for k, v in {
        "ID": f"BD-{n:03d}", "DATE": dt.date.today().isoformat(), "TITLE": a.title, "DECISION": a.decision,
        "OPTIONS": a.options or "(n/a)", "BY": f"{a.by}{words}", "WHERE": a.where or "(n/a)",
        "WHY": a.why or "(n/a)", "AFFECTS": a.affects or "(n/a)", "STATUS": a.status,
    }.items():
        entry = entry.replace("{{" + k + "}}", v)
    p.write_text(text.rstrip("\n") + "\n\n" + entry.strip("\n") + "\n")
    print(f"BD-{n:03d}")


def cmd_route(a):
    store, _ = load(a.project)
    row = [now(), a.phase, a.unit, a.tier, a.rule, a.runtime, a.mechanism, a.model, a.effort,
           a.catalog, str(a.attempt), a.outcome, a.reviewer or "-", a.escalated_from or "-"]
    with open(store / "routing.tsv", "a") as f:
        f.write("\t".join(x.replace("\t", " ") for x in row) + "\n")


def cmd_hash(a):
    print(normalized_hash(resolve_artifact(a.project, a.artifact)))


def pending_routes(store):
    rows = (store / "routing.tsv").read_text().splitlines()[1:] if (store / "routing.tsv").exists() else []
    return [r.split("\t")[2] for r in rows if len(r.split("\t")) > 11 and r.split("\t")[11] == "pending"]


def cmd_check(a):
    project = Path(a.project).resolve()
    store, state = load(project)
    code = 0
    print(f"Run: {state['title']} ({state['slug']})  store: {store}")
    print(f"Phase: {state['phase']}  size: {state['size']}  ui: {state['ui']}")
    if state.get("parked"):
        p = state["parked"]
        print(f"Parked: {p['at']} by {p['by']}: {p['reason']}")
    stale = verify_gates(project, state)
    for gid, g in state["gates"].items():
        hit = next((s for s in stale if s[0] == gid), None)
        print(f"Gate {gid}: {'STALE (' + hit[2] + ') - treat as new input, re-ask the delta' if hit else 'ok'} [{g['artifact']}]")
    if stale:
        code = 3
    if state["inflight"]:
        for k, v in state["inflight"].items():
            print(f"INTERRUPTED: {k} started {v['started']} ({v.get('detail', '')}) - save partial work on a side branch, redo")
        code = code or 4
    dirty = git(project, "status", "--porcelain")
    if dirty:
        print("Git: uncommitted changes present:\n  " + dirty.replace("\n", "\n  "))
    cur = preflight_versions()
    for k, v in cur.items():
        old = state.get("versions", {}).get(k)
        if old and old != v:
            print(f"Moved while parked: {k} {old} -> {v}")
    for unit in pending_routes(store):
        print(f"Routing row still pending: {unit} - close it (pass, gate-miss, dropout) before close")
    print(f"Open question: {state.get('open_question') or '(none)'}")
    print(f"Next: {state.get('next') or '(see phase map)'}")
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def p(name, fn, **kw):
        s = sub.add_parser(name, **kw)
        s.add_argument("--project", required=True)
        s.set_defaults(fn=fn)
        return s

    s = p("init", cmd_init)
    s.add_argument("--slug", required=True)
    s.add_argument("--title", required=True)
    s.add_argument("--size", choices=["small", "project"], required=True)
    s.add_argument("--ui", choices=["yes", "no"], required=True)
    s.add_argument("--store-root")
    s = p("phase", cmd_phase)
    s.add_argument("state")
    s.add_argument("--next")
    s.add_argument("--question", help="the open stop question; empty string clears it")
    s = p("approve", cmd_approve)
    s.add_argument("--gate", required=True, help="S0, S1, S2, S3..., S7:<n> for sections")
    s.add_argument("--artifact", required=True)
    s.add_argument("--words", required=True)
    s.add_argument("--by", required=True)
    s.add_argument("--channel", default="chat", choices=["chat", "lavish", "relay"])
    p("verify", cmd_verify)
    s = p("inflight", cmd_inflight)
    s.add_argument("action", choices=["begin", "end"])
    s.add_argument("--step", required=True)
    s.add_argument("--detail")
    s.add_argument("--outcome", default="done")
    s = p("unit", cmd_unit)
    s.add_argument("--id", required=True)
    s.add_argument("--status", required=True, choices=["planned", "done", "failed", "redo"])
    s.add_argument("--commit")
    s = p("made", cmd_made)
    s.add_argument("--label", required=True)
    s.add_argument("--path", required=True)
    s = p("park", cmd_park)
    s.add_argument("--by", required=True)
    s.add_argument("--reason", required=True)
    s.add_argument("--next")
    p("resume", cmd_resume)
    s = p("decide", cmd_decide)
    for f in ("title", "decision", "by"):
        s.add_argument("--" + f, required=True)
    for f in ("options", "words", "where", "why", "affects"):
        s.add_argument("--" + f)
    s.add_argument("--status", default="active")
    s = p("route", cmd_route)
    for f in ("phase", "unit", "tier", "rule", "runtime", "mechanism", "model", "effort", "outcome"):
        s.add_argument("--" + f, required=True)
    s.add_argument("--catalog", default="live")
    s.add_argument("--attempt", type=int, default=1)
    s.add_argument("--reviewer")
    s.add_argument("--escalated-from")
    s = p("hash", cmd_hash)
    s.add_argument("--artifact", required=True)
    p("check", cmd_check)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
