# Handoffs, precedence, runtime names

Read at phase transitions and after any owner skill upgrade.

## Owner names per runtime

| Capability | Claude Code | Codex |
|---|---|---|
| Sizing, discovery, approaches, sections, written design, hard gate | `superpowers:brainstorming` | `brainstorming` (~/.codex/skills) |
| Grill | `grill-me` | `grill-me` |
| Playbooks (Feature, Bug fix, Refactoring, Prototype, Pause safely, Opening a PR, Shipping) | `pstack:poteto-mode` playbooks | PStack skills if installed for Codex; else run as `claude -p` workers |
| Plan | `pstack:how`, `pstack:architect`, poteto-mode `multi-phase-plan` playbook, `scripts/check-plan.mjs` | same via `claude -p` |
| Arena / critique | `pstack:arena`, `pstack:interrogate` | `spawn_agent` with `fork_turns: "none"` or `codex exec` seats |
| Security review | `pstack:thermo-nuclear-review` (+ `/security-review`) | via `claude -p` |
| Verification driver | `pstack:create-verification-skill`, `pstack:maintain-verification-skill` | via `claude -p` |
| Trail and audit | `pstack:show-me-your-work`; resume record `poteto-mode/scripts/resume.mjs begin|publish|read --project <dir>` | same |
| UI | `impeccable` | via `claude -p`, or frontend-design fallback (C10) |
| Stack evaluation | `tech-stack-eval` if installed, else stack.md rubric | same |
| ADR | mattpocock `domain-modeling` | same |

Do not also run brainstorming's or PStack's top-level router for the same request; playbook matching happens only at phase 7 (C6). Invoke this skill explicitly; auto-trigger hooks proved unreliable.

## Handoffs

| From | To | Hand over | Contract |
|---|---|---|---|
| discovery | business grill | discovery playback (owner's words vs "my guess") | grill opens nodes only for gaps or contradictions |
| business grill | Gate 0 | `docs/business/brief.md` | no technical phase before S0 |
| Gate 0 | design | approved brief + hash | every option and section names the BRs and scenarios it serves; a section serving none is cut or questioned |
| grill (5) | brainstorming (5) | closed nodes | present only sections whose nodes are closed |
| written design | Gate A | design path + hash | no implementation skill, scaffold or install before Gate A |
| Gate A | PStack plan | approved design, brief, grill ledger | deviations from approved intent go back to phase 5, never silently into the plan |
| plan | Gate B | plan path + `check-plan.mjs` output + per-unit tier and rule + scenario coverage | build starts only on the owner's explicit go |
| PStack build | conductor | trail rows, commits, verdicts | conductor updates state only |
| UAT | S16 | `uat-report.md` + evidence | the owner decides acceptance |

## Precedence

| # | Conflict | Resolution |
|---|---|---|
| C1 | Brainstorming says invoke `writing-plans` after approval; PStack owns planning | Plan with PStack (`multi-phase-plan` for project, the playbook's checkpoint for small). `writing-plans` is not used. |
| C2 | Brainstorming spec path vs PStack store | Store wins for design docs; business docs live in the project (`docs/business/`). Repo copy of the design is optional at Gate A. |
| C3 | PStack "never block on the human" vs brainstorming hard gate | Before Gate A the hard gate rules: read and explore only. After, PStack autonomy inside approved scope; Gate B, S8, S9 still stop. |
| C4 | Open questions without examples vs grill-me's recommended answer | Phase separation (interaction.md). |
| C5 | Grill "relentlessly" vs economy | Scoped per section, bounded by the stopping rule. |
| C6 | Brainstorming and PStack routers both auto-trigger | This skill claims the coordinating role; owners are called by name. |
| C7 | PStack arena picks the base itself | Arena stops at a recommendation; the owner picks (S6). |
| C8 | `architect` Phase B always arenas | Post-Gate-A `architect` reuses the 4A synthesis if any; otherwise one T2/T3 sketch unless entry criteria hold. |
| C9 | Codex `spawn_agent` inherits history | Seats use `fork_turns: "none"`. |
| C10-C13 | Impeccable vs frontend-design / brainstorming / hard gate / PStack review | ui.md |

## Versions seen

Recorded at `init` and compared on resume by `sdlc_state.py check` (from `preflight.sh --versions`). Built against: superpowers 7.0.0, PStack 0.9.92, Impeccable 4.8.0, grill-me (unversioned; tracked by content hash). After an owner upgrade, re-run the validation scenarios that touch it.
