# Lifecycle: states, records, checkpoints, park, resume

Read at phase 0 and on every resume.

## Contents
- States and transitions
- Records and their single writer
- `sdlc_state.py` usage
- Checkpoint cadence
- Park
- Unplanned stops
- Resume
- Close

## States and transitions

`enter -> sized -> discovering -> grilling-business -> brief-written [-> prototype] -> gate-0 -> [stack] -> [arena:design] -> approaches -> designing:<n> -> design-written -> [arena:critique] -> gate-a -> planning -> gate-b -> executing -> precheckin -> review -> uat -> s16 -> s8-merge -> closed`

- Small runs skip `prototype` (unless asked), `stack` when a scaffold exists, both arena states, `approaches`, multi-section design, and `gate-b`. S16 and S8 are asked as one question.
- **Ratchet.** Hidden complexity moves the size up and the pointer back to the earliest invalidated phase, never down.
- **Deltas.** A change to the approved brief returns to `gate-0` for that change only (S10). A change to approved design intent returns to `designing:<n>` for that delta and re-passes Gate A for the delta. Never edit an approved artifact to match what was built.
- **Opt-out.** "Just start, skip the questions": record the opt-out with the owner's words in the decision log, state in one line how it will get made, route to the PStack playbook. Gate B still applies for project size.

## Records and their single writer

| Record | Where | Writer |
|---|---|---|
| Business brief, decision log, UAT report, stakeholder feedback | project `docs/business/` | conductor |
| Park note / checkpoint | project `docs/sdlc/checkpoint.md` | `sdlc_state.py` (conductor) |
| Machine state (`state.json`), rendered `sdlc.md` | store | `sdlc_state.py` |
| Grill ledger `grill.md` | store | conductor (grill-me answers) |
| Routing ledger `routing.tsv` | store | conductor (`sdlc_state.py route`) |
| Boards and verbatim board feedback | store `boards/` | conductor |
| Prototype, video, share pack | store `prototype/`, `share/<date>/` | conductor |
| UAT evidence (screenshots, traces, video, HTML report) | store `uat/<run-id>/` | Playwright run |
| Arena runs | store `arena/<run-id>/` | conductor (frame, rubric, seats, synthesis); each seat its own folder |
| Technical decision trail, PStack resume record | PStack store and `resume.mjs` | PStack |
| PRODUCT.md, DESIGN.md, `.impeccable/` | project | Impeccable |

Store default: `~/.claude/orchestrate/<slug>/` (override with `SDLC_STORE_ROOT`). The owner may opt out of `docs/business/` in the repo at Gate 0; then those files move to the store and the choice is logged.

## `sdlc_state.py` usage

Run from anywhere; `<skill>` is this skill's folder.

```bash
S=<skill>/scripts/sdlc_state.py
$S init --project . --slug volunteer-signup --title "Volunteer sign-up" --size project --ui yes
$S phase --project . grilling-business --next "ask node G-3" --question ""
$S decide --project . --title "..." --decision "..." --options "(a) (b)" --by "owner" --words "exact words" --where "phase 3, node G-2" --why "..." --affects "BR-1, UAT-1.1"
$S approve --project . --gate S0 --artifact docs/business/brief.md --words "approved, go" --by "owner" --channel lavish
$S verify --project .          # exit 3 if any approved artifact changed
$S inflight --project . begin --step U3 --detail "build cancel action, T1 sonnet"
$S unit --project . --id U3 --status done --commit abc1234   # also closes the in-flight record
$S made --project . --label prototype --path ~/.claude/orchestrate/<slug>/prototype/index.html
$S route --project . --phase 8 --unit U3 --tier T1 --rule default --runtime claude --mechanism agent --model sonnet --effort medium --outcome pass --reviewer opus
$S park --project . --by "owner" --reason "sharing the prototype" --next "collect feedback, re-ask Gate 0"
$S resume --project .
$S check --project .           # resume check: gates, in-flight, git, versions moved; exit 3 stale, 4 interrupted
```

- `approve` refuses agent approvers and empty words. `--by` is who said it; in a test run with a stand-in, write `test owner (not the captain)`.
- Gate ids: `S0`, `S1`, `S2`, `S3`, `S4`, `S5`, `S6`, `S7:<n>` per section, `S8`, `S16`, `S17:<check>`.
- Hashes ignore line-ending and trailing-whitespace changes only; any other edit makes the gate stale.

## Checkpoint cadence

| When | Make durable |
|---|---|
| The owner answers anything | grill ledger row; for a business call, `decide` - before the next message |
| Every phase boundary or stop answered | `phase` (refreshes checkpoint and `sdlc.md`), `approve` for gates, PStack `resume.mjs publish --project <dir>` when in git |
| Before a long step (arena fan-out, plan unit, UAT run, prototype or video render) | `inflight begin` with step id, inputs, worker and model |
| After each unit passes its checks | commit on the run branch, then `unit --status done --commit <sha>` |
| After each UAT scenario | result row appended to the UAT report draft |
| Context getting full | checkpoint, then one line: "Saved; continue in a fresh session with the skill and 'resume'." |

## Park

The owner may answer "park" to any stop, or say it at any time. Park stops all work unless the owner names work to continue.

1. Finish or back out of the current atomic step. Start nothing new; stop subagents.
2. Commit work in progress on the run branch as one `wip:` commit (local only).
3. `sdlc_state.py park --by ... --reason ... --next ...`; commit `docs/sdlc/checkpoint.md`. Publish the PStack resume record.
4. Log the park in the decision log only if the owner gave a business reason.
5. Stop any board server. After a prototype, prepare the share pack (business.md "Share pack").
6. Reply: where it parked, what was saved, where the share pack is, "to continue, invoke the skill with 'resume' here".

Park differs from away: away keeps working up to the next stop; park stops now.

## Unplanned stops

Token or context exhaustion, crash, rate limit, quota: the same resume. At most the one in-flight step is lost.

- Rate limit: retry with backoff on the same tier; then routing fallback (same tier other model, then up). Never down silently.
- Quota exhausted for the needed tier on every reachable family: checkpoint, `park --by agent-auto --reason "quota: <what>, resets <when>"`, and ask S12 on resume.

## Resume

1. `sdlc_state.py check --project <dir>`; also `resume.mjs read --project <dir>` when in git. A missing or corrupt record is reported, never reconstructed from memory.
2. **Stale gate (exit 3)**: show what changed (`git diff` against the approved commit when available), treat it as new input, ask that gate for the change only. Never silently accept or revert.
3. **Interrupted step (exit 4)**: commit any uncommitted partial work to a side branch `wip/<step>-<date>` (never discard), redo the step from its plan with a fresh worker at the same tier; delete the side branch only after the redo passes. Arena: relaunch only seats without `proposal.md`. UAT: rerun only scenarios without a result row. Render: rerun from the recorded script.
4. **Moved while parked**: list owner version changes, model catalog changes, and default-branch movement in one line each; a moved default branch makes a rebase the first unit.
5. `sdlc_state.py resume`. If parked at a stop with a business question open, ask once: "Anything from stakeholders or new priorities since <date>?" Otherwise go straight to the open question.
6. Continue at the exact step. Never re-ask a closed grill node; never re-present an approved section.

## Close

PStack `show-me-your-work` audits the trail. The close summary lists: gates with hashes, decision log count, routing outcomes per tier (escalations, fallbacks), pre-check-in warnings and waivers with expiry, UAT result counts and evidence paths, UI line (detector, finish disposition, DESIGN.md) when `ui: yes`, and anything left open. A proposal to change a routing floor goes to the owner; never adjust it automatically.
