# Business: brief, Gate 0, decision log, prototype

Read at phases 3 through Gate 0, and whenever the brief changes.

## The brief

`docs/business/brief.md` in the project, from `assets/business-brief.md`, written by the conductor from the grill ledger.

- **Business language only.** No screens, endpoints, tables, frameworks or tools. Test: a business person could read every line and run every scenario by hand.
- **Requirements** `BR-n`, each `must` or `should`, with the owner's own words beside it (`Said: "..."`).
- **Success criteria** `AC-n.m`, each measurable: a time, a count, an amount, or a state. Grill "fast" or "easy" into a number; if the owner will not give one, list it under open business decisions.
- **Acceptance scenarios** `UAT-n.m (AC-n.m)`: Given / When / Then, at least one per criterion. A criterion with no scenario cannot pass Gate 0.
- Out of scope; open business decisions; assumptions the owner delegated ("agent, my call").
- Small runs: a few lines, shown in chat.
- The owner owns every line. **An agent never edits the brief, a criterion, or a scenario to make something pass.**

## Gate 0 (S0)

- After the brief is written, before any technical phase. Blocks Arena, approaches, design sections, S3, S4, and technical grilling. Reading the existing code to understand today's product is allowed.
- Board for project runs (stops.md), chat for small. Show requirements, criteria, scenarios, out of scope, open decisions, delegated assumptions.
- The one question: "Is this what the business needs? Approve, or say what to change. Do you want a clickable prototype and walkthrough video first? (or park to share with stakeholders)". Say plainly that approving starts technical design, not building.
- Record: `sdlc_state.py approve --gate S0 --artifact docs/business/brief.md ...` and one decision log entry (approved brief and hash; deferred `should` items).
- Later brief changes go back through Gate 0 for that change only; design and plan are then re-checked against the new hash.

## Decision log

`docs/business/decisions.md`, append-only, written with `sdlc_state.py decide` (assigns `BD-nnn`). Never edit an entry; a change adds a new entry with `--status "supersedes BD-00n"`.

Write an entry for: each business call in discovery and the grill (scope, policy, audience, priority, thresholds); delegated defaults ("agent, my call"); Gate 0 approval; picks with business consequences (S3, S4, S6, S7); trade-offs forced at Gate A or B; brief changes (S10); prototype offer answer; S16 outcome; waivers that are business risk. Technical decisions stay in PStack's trail.

## Prototype and walkthrough video (optional, before Gate 0)

Offered in the Gate 0 question. Recommend skipping for no-UI work, tiny or small runs with one or two scenarios, and changes inside an existing screen. A "yes, prototype first" holds Gate 0 open.

**Prototype.** One self-contained HTML file (no build, no server, no backend) at `<store>/prototype/index.html`, covering the key journeys in the scenarios, with invented data labeled as such. For UI work it follows Impeccable up to the direction (S4 may happen here if the owner wants options). Throwaway: never copied into the build without going through design and plan. Record with `sdlc_state.py made --label prototype`. Tier: T2 build, T3 conductor for direction.

**Narrated video** (local only; skip and say so when `ffmpeg` or `say` is missing, or when the owner wants it skipped):
1. Script: one scene per key scenario; each beat = narration line + screen action. Save `script.json`.
2. Record: drive the prototype with Playwright (or chrome-devtools-axi in a named session) and take one screenshot per beat at desktop and phone width.
3. Narrate: `say -v <voice> -r 180 -o beat-<n>.aiff "<line>"` (prefer an installed Enhanced/Premium voice).
4. Assemble: per beat, `ffmpeg -loop 1 -i shot.png -i beat.aiff -shortest -vf "drawtext=...caption..." beat.mp4`, then concat with title cards. If `drawtext` is unavailable, burn captions into the PNG first.
5. Check: a contact sheet (one frame per beat beside its narration line) to confirm each scene matches before the owner sees it.
Nothing is uploaded. Tier: T2 script, T0 recording and assembly.

**Review.** Show the prototype path and video on the Gate 0 board. Feedback may change the brief before approval; one short prototype revision round is allowed, more only if the owner asks. Brief changes prompted here are logged "prompted by prototype review".

## Share pack (park after the prototype)

This is the recommended park point when stakeholders should see it. On park, prepare `<store>/share/<date>/`: `prototype.html`, `walkthrough.mp4` (if made), `brief-summary.md` (requirements, criteria, scenarios), `feedback-template.md` (from `assets/feedback-template.md`, one section per scenario). **The agent never sends or uploads it**; sharing is the owner's action (S9).

## Stakeholder feedback on resume

- Save each piece verbatim as `docs/business/feedback/<date>-<who>.md` with who said it. It is input, not a decision.
- Propose brief changes item by item, each tied to the feedback that prompted it; ask Gate 0 for the changed items only. Log accepted changes "prompted by stakeholder feedback (<who>)".
- Stakeholders disagree: one question with both views quoted (S11).
