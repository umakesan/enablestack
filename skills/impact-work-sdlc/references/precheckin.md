# Pre-check-in gate

Read at phase 7 (setup units) and at 8G.

## Where it runs

| Moment | What | How |
|---|---|---|
| Every commit (under ~30 s) | Staged secrets, format, lint | `.git/hooks/pre-commit` -> `scripts/precheckin --fast` |
| Before push and review, per unit | Every deterministic check on the whole change | `scripts/precheckin` (also the `pre-push` hook) |
| Before merge | Full set on the merge result, plus AI security review and independent review | conductor; CI runs the same script when the project has CI |

Order: `Build -> tests -> pre-check-in gate -> review -> UAT -> S16 -> S8 merge`.

## Setup (a Gate B plan unit, T1)

1. Copy `<skill>/scripts/precheckin.py` to `<project>/scripts/precheckin` and `<skill>/assets/precheckin.toml` to the project root. Fill in the project's own format, lint, typecheck, test and build commands. `none: <reason>` marks one not applicable; empty means NOT RUN.
2. `python3 scripts/precheckin --install-hooks`. (Projects already using the pre-commit framework or lefthook: call the script from that instead.)
3. Gate B lists exactly what will be installed in the project, and separately any **machine installs** (for example `brew install gitleaks osv-scanner semgrep`) - those change the machine and need the owner's go.
4. First run on an old codebase: existing findings outside the change become a baseline the owner reviews once at Gate B; only new findings block. The baseline never grows silently.

## Checks

| Check | Tool (fallback) | Blocks? |
|---|---|---|
| Secrets | gitleaks (`protect --staged` per commit, `detect` on the branch); built-in high-confidence patterns always run | Block. gitleaks missing = NOT RUN (blocking gap) |
| Vulnerable dependencies | osv-scanner (`npm audit` / `pip-audit`) | Block high/critical with a fix; warn otherwise |
| Static analysis | semgrep `p/default` (CodeQL when on GitHub with scanning) | Block errors in changed code; warn others. Missing = NOT RUN |
| Licences | lockfile licences vs `[licenses]` allow/deny | Block denied; warn unknown |
| Format, lint, type check | project tools | Block (format auto-fixed first) |
| Tests, build | project commands | Block |
| UI slop (UI only) | `impeccable detect` | Block immediate-tier rules |
| AI security review | PStack `thermo-nuclear-review` subagent on the diff; Claude Code `/security-review` as second opinion when available | High findings fixed or disproved with evidence |
| AI correctness review | the independent review (routing.md); `/code-review` when available | escalation ladder |
| Maintainability (project, optional) | `thermo-nuclear-code-quality-review` | Warn |

Deterministic tools decide pass or fail. AI reviews find what tools cannot; their findings go through the review rules, never a silent pass. **A missing tool is "not run", never a pass.**

## Findings

- Deterministic block: back to the unit's writer on the escalation ladder; after two escalations, S14.
- False positive: suppressed in the tool's own config with a written reason (`.gitleaksignore`, `nosemgrep: <reason>`, audit allow-list with expiry); every suppression is listed at merge. Suppressing a **blocking** finding needs S17.
- AI finding: fixed, or disproved with evidence (a test, a trace, a `blast-radius` proof). An unresolved high finding keeps the gate closed.
- A fix that changes scope (new dependency, schema change, different auth model): S10.
- Secret found: never committed or pushed; the hook blocks it and the run never prints the full value. A secret already in history stops the run: rotation is the owner's (S13); rewriting history is S9.

## Waivers (S17)

- Only when a blocking finding would be accepted unfixed or a required check cannot run.
- Board: the finding, evidence, why it cannot be fixed now, the risk, an expiry date. Question: "Waive this until <date>, or fix it now?" Recommend fixing unless the evidence shows a false positive or an unfixable upstream issue.
- Record in `precheckin.toml` `[[waivers]]` with `check`, `reason`, the owner's exact `words`, `by`, `expires`; plus `sdlc_state.py approve --gate S17:<check> --artifact precheckin.toml`; plus a decision log entry when the risk is a business call.
- **Never** a silent pass, an agent self-waiver, or a waiver without expiry. The runner ignores waivers without words, owner, or a future expiry.

Warnings never stop the run; they are listed in the merge ask and close audit.

## Tiers

Scanners T0/script. Fixing findings: the unit's tier, up the ladder. AI security review T2, T3 for risky units, different model from the writer. `/security-review`, `/code-review`, false-positive triage T2.
