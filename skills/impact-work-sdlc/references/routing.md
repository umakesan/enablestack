# Routing: which model tier does which job

Read at phase 0 (tier check), Gate B (unit tiers), and phase 8.

## Tiers (the stable contract; resolve models live at run time)

| Tier | Bar | Illustrative Claude alias | Illustrative Codex slug |
|---|---|---|---|
| T3 | Right when intent is ambiguous or the decision costly to reverse | `fable` @high (@xhigh synthesis) | `gpt-6-astra` @xhigh |
| T2 | Sound engineering judgment on a defined problem | `opus` @medium-high | `gpt-6.1-sol` @medium-high |
| T1 | Faithful execution of a well-specified unit with tests | `sonnet` @medium | `gpt-6.1-terra` @low-medium |
| T0 | Mechanical; or a plain script | `haiku` @low | `gpt-6-luna` @low |

Model names change; the mapping above is an example. Resolve from the live `Agent` tool / `claude --model` / Codex catalog and record the catalog source in the ledger. Never `max` or `ultra` effort without the owner's word (S12).

## Hard boundaries

- **The conductor cannot switch its own model mid-session.** "A different model for this step" always means a separate worker (subagent, `claude -p --model`, `codex exec -m`). Never claim to have switched.
- At phase 0, state the session model; for a project run below T3, recommend relaunching (`claude --model fable`) and continue only if the owner accepts.

## Phase floors

| Step | Where | Floor |
|---|---|---|
| Discover, business grill, brief, sections, written design, synthesis | session | T3 |
| Evidence lookups inside grilling | worker | T0/T1 |
| Builder check; Gate A design-vs-brief check | worker | T2, different model from the designer |
| Plan (`how`, `architect`, `multi-phase-plan`) | worker or session | T2 high; `check-plan.mjs` T0 |
| Plan unit build | worker | T1 default; UI units T2 |
| New behavior tests for a unit | worker | the unit's tier; mechanical test updates T0 |
| Run tests, lint, scanners | script | T0 |
| UAT scenario scripts; verification driver | worker | T2, different model from the builders |
| UAT run | script | T0 |
| Independent review | worker | **T2, different model from the writer** (cross-family when reachable); T3 for risky units |
| AI security review (`thermo-nuclear-review`) | worker | T2; T3 for auth, money, data, secrets |
| Polish/harden/adapt/clarify, documenter | worker | T1 |
| Close audit | worker | T1 |

## Unit tier rules (applied at Gate B, rule recorded per unit)

- **Raise to T3**: cross-cutting design, concurrency, subtle algorithm; security, auth, money, irreversible data; a public interface the sketch did not specify; no executable acceptance criterion.
- **Raise to T2**: touches 3+ modules; plan marks a judgment call inside; any UI unit.
- **Lower to T0** only when purely mechanical with a deterministic check. Nothing else goes below the floor.

## Escalation ladder

- A gate miss: failed tests, a reviewer "act on" finding due to execution quality, a silently absorbed deviation from the plan, or two failed attempts at one step.
- On a miss: a **fresh** worker one tier up with consolidated scope. At most two escalations per unit. A miss at T3 stops the unit: S14.
- An escalation never lowers the reviewer's tier. Cheaper work never approves itself.

## Fallback and safeguards

1. Same tier, nearest model in the same family. 2. Same tier, other family. 3. Up one tier.
- **Never fall down a tier silently.** A forced downgrade is logged and gets a T3 reviewer.
- **Owner model limits.** If the owner restricts models (for budget) so that the "different model, T2+" review or a unit's tier floor cannot be met in one family, say so at Gate B and recommend a cross-runtime reviewer (`codex exec` on another family) when reachable; if the owner keeps the limit, log each affected review as "same family" and list them at S8 and close.
- A capacity or thread-limit error stops spawning; it is not a reason to try a cheaper model.
- Arena: 3 seats default, 4 max, one re-frame. Escalation: 2 per unit. Spend over the Gate B cap: S12.
- Arena seats and independent units launch in parallel; escalation retries are sequential per unit.

## Routing ledger

Every model choice is one row in `<store>/routing.tsv` via `sdlc_state.py route` (columns in `assets/routing-ledger-header.tsv`): phase, unit, tier, rule, runtime, mechanism (session/agent/spawn_agent/exec/script), resolved model, effort, catalog source, attempt, outcome (pass/gate-miss/dropout/fallback/skip), reviewer model, escalated-from. Arena skips are rows too. Changing a floor is an owner-approved edit proposed from ledger evidence at close.
