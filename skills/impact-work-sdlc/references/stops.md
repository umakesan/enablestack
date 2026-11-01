# Stops: when the owner decides

Read before every stop.

**Rule:** stop only when the answer changes what gets built, cannot be undone, reaches people or systems outside the project, or spends beyond what was agreed. Everything else is decided by the agent and logged.

## Stop list

| Stop | When | Surface | A yes starts |
|---|---|---|---|
| S0 Gate 0: business brief | End of business grill (small, project) | Board (project) / chat (small) | Technical design, not building. Offers the prototype. |
| S1 Gate A: design vs brief | Small and project | Board: coverage of every `must` BR and scenario, contradictions, brief hash match | Planning only |
| S2 Gate B: plan | Project | Board: units, tiers, worker counts, arena use, cost estimate, scenario coverage and automation units, pre-check-in setup and machine installs | The build |
| S3 Stack choice | New project with no scaffold, after S0 | Board: matrix, cost, risks, recommendation | Design on that stack |
| S4 Visual direction | UI work, new surface or new look, after S0 | Visual board (Impeccable decision page) | Design sections on that direction |
| S5 Comp pick | Comp-led UI work | Visual board, three comps | The UI section |
| S6 Approach pick | Project | Board: options naming the BRs they serve | Design sections |
| S7 Each design section | Project | Board card or chat | The next section |
| S8 Merge | Every merge | Board: PR or branch, pre-check-in results on the merge result, warnings, suppressions, waivers, AI security reviews, UAT summary. Approve S8 against the board file itself. | That one merge |
| S9 Irreversible or outward action | Deploy, publish, force-push, deleting or migrating real data, messages to people, public posts, remotes, sharing a board | Chat, naming the exact action and target | That one action |
| S10 Scope change | A finding or new fact would change the approved brief or design | Board: evidence, options, recommendation | Return to Gate 0 or phase 5 for the delta |
| S11 Conflicting answers | Two owner answers contradict | Chat, both quoted | The resolution |
| S12 Spend over the cap | Over the Gate B cap, `max`/`ultra` effort, quota park | Chat or board | Raise the cap, or stop |
| S13 Credentials | Login, token, paid service | Chat, naming the login. Never ask for a secret in chat. | The owner signs in |
| S14 Retries used up | A unit failed at T3 after two escalations | Board: evidence, options (rescope, accept gap, stop) | The chosen option |
| S15 Live UI editing | Impeccable `live` / `generate` | Only when the owner asks and is present | That session |
| S16 UAT acceptance | After browser UAT | Board: brief and results side by side; not met, flaky, not run first | Merge ask (small: asked together with S8) |
| S17 Waive a blocking check | A blocking pre-check-in finding accepted unfixed, or a required check cannot run | Board: evidence, risk, expiry | That waiver until its expiry |

S3, S4, S6 only happen after S0. Every stop accepts "park" (lifecycle.md).

## Not stops: decide and log

Size and `ui` flag (stated, owner may override); whether Arena runs; model choices, fallbacks, retries within the cap; facts the code or docs answer; defaults the owner delegated; detector findings fixed or ignored with a reason (unless the ignore hides a brand-pinned value: S10); which polish passes run; routine fixes inside a unit; branch names and commit messages; writing DESIGN.md for an already chosen look.

## How every stop is asked

- One question per message. Evidence first, then the recommendation, then exactly what a yes starts and what still needs a separate go.
- Recommendations never pre-empt taste: Impeccable's "category standard" option is offered, never recommended.
- **Record immediately**: `sdlc_state.py approve` (words verbatim, who, channel, hash), plus a `decide` entry for business consequences.
- **Gate refusals.** The conductor refuses to pass a gate on an agent's own say-so, on silence, or on a default.

## Boards

Default surface for any stop with a document to read (S0, prototype review, S1, S2, S3-S7, S8, S10, S12, S14, S16, S17). Yes/no stops with no document stay in chat.

1. Copy `assets/gate-board.html` to `<store>/boards/<stop>.html`; fill it (light theme; header says what a yes releases; attention items first).
2. Open with `lavish-axi <file>` on loopback. Arm a tracked listener (`lavish-axi poll` in a tracked background task; inside firstmate, its listener). Never fire-and-forget.
3. Save every annotation and message verbatim to `<store>/boards/<stop>-feedback.md`; treat them as input (questions answered, corrections become ledger nodes or design changes).
4. Approval on the board is recorded like chat, channel `lavish`.
5. On park, stop the server; keep source and feedback on disk. Resume reopens the same board.

**Fallback:** Lavish missing or unreachable: write the same document as Markdown in the project (or store), ask the one question in chat, and say the board was not available.

**Safety:** loopback by default. LAN binding only when the owner is remote and asks, with the caveat that the server is unauthenticated. `lavish-axi share` (public hosting) is S9: never without the owner's explicit go.

## When the owner is away

- Work every non-stop step up to the next stop, post the question, hold. Stops never take a default.
- Work that does not depend on the open stop may continue (an independent unit already approved at Gate B). Work that depends on it waits.
- Impeccable's "probe once, infer and label" applies only to facts inside non-stop steps with clear evidence; never to S3, S4, S5.
- For long waits, park safely instead of holding a session open. Milestones go into a short progress note, not extra questions.
- Away is detected mechanically: the question was posted and no answer arrived in the session or relay round.

## Test runs with a stand-in owner

When a supervisor authorizes a stand-in to answer stops for a **test**, every answer is recorded with `--by "test owner (not the captain)"` in the decision log and gate records, and is never treated as a real owner decision.
