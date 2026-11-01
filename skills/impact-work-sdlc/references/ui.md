# UI lane (Impeccable)

Read only when `ui: yes`. A run with `ui: no` skips everything here.

## The `ui` call

`ui: yes` when the request or the files it touches include an interface someone sees: web pages, app screens, components, forms, dashboards, email templates, native screens, or their UX copy. `ui: no` for backend, CLI, data, infrastructure, docs. Mixed work is `ui: yes` scoped to the UI part. Stated with the size; the owner may override; it ratchets no -> yes only.

On `ui: no` runs, Impeccable's global hook may still print findings on UI-type files: treat them as out of scope, note them once at close, do not act on them.

## Phase map

| Phase | Impeccable step | Stop |
|---|---|---|
| 0 Enter | `impeccable context` once per session; report `CONTEXT_STALE`, do not fix it | - |
| 2 Discover | `impeccable init` if no PRODUCT.md; its interview is folded into discovery (one combined round) | - |
| 3 Business grill | Shape phase 1 purpose / people / outcome / states questions join the ledger | - |
| After Gate 0, 4 Approaches | New surface or replacement look: new-work concept-seed directions on Impeccable's decision page. Extending an established look: no roll. | **S4** |
| 5 Sections | One section "UI: direction, states, layout intent" written as the shape brief (3-5 bullets) | S7 |
| 5-6 comp-led only | `visualize`: three compositions | **S5** |
| 6 Written design | Direction contract recorded in the surface brief. DESIGN.md is **not** written yet. | Gate A |
| 7 Plan | Mark UI units; each names its Impeccable steps (craft floor, detector, finish review). T2 floor. | Gate B |
| 8 Build | Before any UI edit the worker loads Impeccable's craft floor (`reference/craft-floor.md` or as SKILL.md setup names it). The hook surfaces immediate-tier findings after each edit; on runtimes without the hook run `impeccable detect --json <changed targets>` (exit 2 = findings). | - |
| 8G Gate | Detector findings fixed, or ignored with a written reason in `.impeccable/config.json`. An ignore that would hide a brand-pinned value is S10. | - |
| 8R Review | Two independent reviews: PStack's different-model code review **and** Impeccable `critique` + `audit` (a11y, performance, responsive), then `impeccable-finish-reviewer`: `ship` passes; `fix`/`rebuild` loop under the escalation cap; `recapture` redoes evidence only. Both must pass; neither overrides the other. | S10 if a finding changes scope |
| Before UAT | `polish`, `harden`, `adapt`, `clarify` only where findings call for them, never as a sweep. Then `impeccable-documenter` writes DESIGN.md for a new look. | - |
| 9 Close | UI line: detector clean or ignores listed, finish disposition, DESIGN.md written or not needed, screenshot paths | - |

Commands such as `bolder`, `quieter`, `distill`, `colorize`, `typeset`, `layout`, `animate`, `delight`, `overdrive`, `onboard`, `optimize`, `extract` run only when the owner asks or a review finding names them. `live` and `generate` are S15: only with the owner present.

## One conversation

Impeccable's questions run inside brainstorming's flow and the grill ledger, one per message, under the stopping rule. Answers are written where Impeccable expects them (PRODUCT.md, surface brief) so it never re-asks.

## Precedence

| # | Conflict | Resolution |
|---|---|---|
| C10 | frontend-design and Impeccable both claim UI work | Impeccable when installed; frontend-design only as the named fallback (for example Codex-only), stated at Gate B and close. Never both on one surface. |
| C11 | Impeccable's interview vs brainstorming's flow | Brainstorming owns the conversation and gate; shape's "confirm and stop" is satisfied by the section approval. |
| C12 | Impeccable new-work builds right after direction lock | Before Gate A, only direction and comps (images and briefs). Implementation waits for Gate A and Gate B. |
| C13 | Finish reviewer cannot soften vs PStack review gate | Both must pass. |

## Tiers

Init/shape questions and direction pick: T3 (session). concept-seed script T0; writing directions T2. UI unit build T2 floor. Detector T0. critique/audit T2, different model from the writer. Finish reviewer T2-high (T3 for persuasion/experience surfaces), different family when reachable. Polish passes and documenter T1. Impeccable's agents set `model: inherit`; always spawn them with an explicit model.

Impeccable is installed for Claude Code. On a Codex conductor, UI units run as `claude -p` workers, or the C10 fallback is named at Gate B.
