---
name: impact-work-sdlc
description: Run a project from a plain-language business brief to accepted, merged work - business grill and Gate 0, technical design and Gate A, plan and Gate B, build, pre-check-in security gate, independent review, browser UAT against the agreed scenarios, owner acceptance, merge - with park and resume at any stop. Use for /impact-work-sdlc, "run the SDLC", "start a new project the full way", or "resume my SDLC run". Not for quick fixes, pure investigations, or PR babysitting.
metadata:
  display-name: Impact Work SDLC
---

# Impact Work SDLC

A conductor, not a methodology. It calls owner skills at the right moment, in the right order, and adds what none of them provide: a business brief the owner approves first (Gate 0), named stops where only the owner decides, model routing by tier, a pre-check-in gate, browser UAT tied to the brief, and park/resume.

"The owner" is the person running the project. The display name lives only in this file's frontmatter `metadata.display-name` and the H1; rename by changing those, the folder, and `name`.

## Owners (call by name, never restate)

| Owner | Does |
|---|---|
| `superpowers:brainstorming` | Sizing, open discovery, approaches, design sections, written design, hard no-build-before-Gate-A rule |
| `grill-me` | Closed one-at-a-time questions, each with a recommended answer (business grill, then technical grill per section) |
| PStack (`pstack:poteto-mode` playbooks, `how`, `architect`, `arena`, `interrogate`, `thermo-nuclear-review`, `create-verification-skill`, `show-me-your-work`) | Plan, build with subagents, reviews, Arena, verification driver, trail, resume records |
| `impeccable` (UI work only) | Product context, visual direction, craft rules, detector, critique/audit/finish review |
| Playwright (project dev dependency) | Scripted browser UAT, desktop and phone |
| lavish-axi | Review boards for stops that need a document (loopback only by default) |

## Start every run

1. Run `scripts/preflight.sh [--ui]` from this skill folder. A missing required owner stops the run with the printed install command. Never substitute an owner inline.
2. If the owner said "resume", or `docs/sdlc/checkpoint.md` exists in the project: read [references/lifecycle.md](references/lifecycle.md) section "Resume" and run `scripts/sdlc_state.py check --project <dir>` before anything else.
3. Otherwise state size (quick / small / project) and `ui: yes|no` in one line. The owner may override. Ambiguous size takes the heavier one; size only ratchets up.
4. Quick: do it, say what was done, pause only before irreversible actions. No store, no gates. Stop reading here.
5. Small or project: `scripts/sdlc_state.py init ...` (see lifecycle.md), then follow the phase map.

## Phase map

| # | Phase | Owner | Stop | Read first |
|---|---|---|---|---|
| 0 | Enter, preflight, resume check | conductor | - | [lifecycle.md](references/lifecycle.md), [routing.md](references/routing.md) (tier check) |
| 1 | Size and `ui` flag | brainstorming | - | - |
| 2 | Discover (open questions, owner's own words) | brainstorming (+ impeccable init if UI) | - | [interaction.md](references/interaction.md) |
| 3 | Business grill, then business brief | grill-me, conductor | - | [business.md](references/business.md) |
| 3P | Optional prototype and narrated video | conductor, impeccable | park point | business.md "Prototype" |
| G0 | **Gate 0: approve the brief** | conductor | **S0** | [stops.md](references/stops.md) |
| 3S | Stack choice (new project, no scaffold) | see stack.md | **S3** | [stack.md](references/stack.md) |
| 4A | Design Arena (only if entry criteria hold) | PStack arena | - | [arena.md](references/arena.md) |
| 4 | Approaches / visual direction | brainstorming / impeccable | S6 / S4, S5 | [ui.md](references/ui.md) if UI |
| 5 | Design sections, technical grill per section | brainstorming + grill-me | S7 | interaction.md |
| 6 / 6A | Written design (in the store `docs/`, not brainstorming's default spec path; C2), builder check, optional Critique Arena | brainstorming, PStack | - | arena.md, [handoffs.md](references/handoffs.md) |
| GA | **Gate A: design checked against the brief** | conductor | **S1** | stops.md |
| 7 | Plan: units, tiers, scenario coverage, pre-check-in setup, UAT automation units | PStack | - | routing.md, [precheckin.md](references/precheckin.md) |
| GB | **Gate B: plan, cost, installs** (project only) | conductor | **S2** | stops.md |
| 8 | Build units, fast checks per commit | PStack | S10, S12-S14 as they arise | routing.md, ui.md |
| 8G | Pre-check-in gate | `scripts/precheckin.py` + AI reviews | S17 | precheckin.md |
| 8R | Independent review (different model, T2+) | PStack, impeccable for UI | - | routing.md |
| 8U | Browser UAT of the Gate 0 scenarios | Playwright | - | [uat.md](references/uat.md) |
| S16 | **Owner acceptance** | conductor | **S16** | uat.md, stops.md |
| S8 | **Merge** (gate re-run on the merge result) | conductor | **S8** | stops.md |
| 9 | Close: audit trail, routing summary | PStack show-me-your-work | - | lifecycle.md |

Small runs: short brief and Gate 0 in chat, one-section design, Gate A, the matching PStack playbook, no Gate B, short UAT, acceptance asked together with merge. Arena never runs for small.

## Rules that hold in every phase

- **Stop only when** the answer changes what gets built, cannot be undone, reaches people or systems outside the project, or spends beyond what was agreed. Everything else: decide, log, continue. The full stop list (S0-S17) and how each is asked are in [stops.md](references/stops.md).
- **One question per message**, evidence first, a recommendation, and what a yes starts. "Park" is always a valid answer.
- **No defaults on stops.** If the owner is away, work up to the next stop, post the question, hold. Independent approved work may continue.
- **Nothing technical before Gate 0; nothing built before Gate A; no build before Gate B** (project size).
- **Every owner answer is durable before the next message** (grill ledger, decision log). Every gate binds to a SHA-256 of the approved artifact via `scripts/sdlc_state.py approve`; a changed artifact makes the gate stale and only the delta is re-asked.
- **Agents never edit the brief, a criterion, or a scenario** to make something pass, and never waive a blocking check.
- **Cheaper work never approves itself.** Reviews are by a different model at T2 or above; failures move up a tier, at most twice.
- **No outward action without the owner's go**: no push, deploy, publish, share, message, or remote. Boards stay on loopback.

## References (read only when the phase needs them)

- [lifecycle.md](references/lifecycle.md) - states, store layout, `sdlc_state.py` usage, checkpoint cadence, park, resume. Phase 0 and any resume.
- [interaction.md](references/interaction.md) - question styles, grill ledger, stopping rule, reopen rule, relay mode. Phases 2-6.
- [business.md](references/business.md) - brief format, Gate 0, decision log, prototype and video, share pack, stakeholder feedback. Phases 3-G0 and any brief change.
- [stops.md](references/stops.md) - S0-S17, away rule, boards and fallback. Before every stop.
- [stack.md](references/stack.md) - S3 stack-choice method. New projects only.
- [arena.md](references/arena.md) - 4A/6A entry criteria, seats, independence, synthesis. Project size only.
- [routing.md](references/routing.md) - tiers T0-T3, unit rules, escalation, fallback, routing ledger. Phase 0, Gate B, phase 8.
- [ui.md](references/ui.md) - the Impeccable lane. Only when `ui: yes`.
- [precheckin.md](references/precheckin.md) - checks, setup, findings, waivers. Phase 7 (setup) and 8G.
- [uat.md](references/uat.md) - browser UAT, evidence, misses, S16. Phase 7 (automation units) and 8U.
- [handoffs.md](references/handoffs.md) - per-runtime owner names, precedence table, versions seen. At phase transitions and on owner upgrades.

Templates are in `assets/`; copy, never edit them in place.
