# UAT: the Gate 0 scenarios, in a real browser

Read at phase 7 (automation units) and 8U.

UAT performs exactly the scenarios approved at Gate 0 against the real, running app. It is not a new test set. Developer tests check the code works; UAT checks the business got what it asked for. Impeccable says whether the interface is good; UAT says whether it does what was asked. Both are needed.

## Plan-time units (Gate B)

1. Add `@playwright/test` as a dev dependency; `npx playwright install chromium` (add webkit when the brief names Safari or iPhone users). Python projects may keep a Node `uat/` folder beside the code.
2. UAT environment: separate port, separate data file or database, seed and reset for each scenario's Given.
3. Test users and sign-in setup, or the owner's one-time sign-in (S13).
4. Accessible names (or `data-testid` where none exists) so controls are findable by what users see.
5. Optionally the project verify skill via `pstack:create-verification-skill` (refresh with `maintain-verification-skill`), pointing at this suite.
6. One automation unit per scenario, written **from the brief, not the code**, by a T2 model different from the builders.

## Layout

```
uat/
  playwright.config.ts   from assets/uat-playwright.config.ts: webServer, desktop + phone projects, trace/video/screenshot on, retries 1
  scenarios/UAT-1.1-<slug>.spec.ts   test title = the scenario's exact Given/When/Then text
  fixtures/              seed data for each Given; reset after each run
  .auth/                 saved sign-in sessions (gitignored)
```

Run all: `npx playwright test -c uat/playwright.config.ts`. One: `--grep UAT-1.2`. Phone only: `--project=phone`. Failure: `npx playwright show-trace <trace.zip>`.

## Rules for the scripts

- **Fixed wording.** The test title carries the exact scenario text; `test.step` names follow the Given / When / Then lines. Automation may add technical steps but never changes what is checked. A different model compares each script's assertions with the brief wording before the run (the wording check); a weakened "then" is fixed in the script, never in the brief.
- **Like a user.** Open, click, type, choose, scroll, wait for the visible result. No internal functions, test-only endpoints or back doors. Direct state setting only to seed the Given before the scenario starts.
- **Selectors by what users see**: `getByRole`, `getByLabel`, `getByText`, taken from scenario words. No CSS paths, XPath or coordinates. A control that cannot be found this way is also an accessibility finding.
- **Waits, never sleeps**: web-first assertions, waiting on the response that causes the side effect, polling up to a timed criterion's own limit.
- **Both viewports**: desktop 1440x900 and a phone profile (~390-412 px, touch), unless the brief says one only.
- **Errors fail the scenario**: collect console errors and failed requests (4xx/5xx) and attach them; an uncaught page error or a 5xx makes it "not met" even if the screen looked right. Warnings are listed only.
- **Data** is invented and labeled; no production data, no real customer in screenshots. External services use sandboxes or local catchers. The agent never types a real password.
- **App start**: a fresh local server per run via `webServer`. A preview deployment only with the owner's go (S9).

## Evidence

- Screenshot per step, trace and video for every run; JSON reporter output feeds the report. Media and the HTML report go to `<store>/uat/<run-id>/` (set `UAT_OUT`, `UAT_HTML`, `UAT_JSON`).
- `docs/business/uat-report.md` from `assets/uat-report.md`, rewritten per run (history in git). Header: brief hash (must equal the Gate 0 hash), build commit, date, counts. Not met, flaky, not run and owner-run rows first.
- `superpowers:verification-before-completion` applies: no "met" without fresh evidence from this run.
- `inflight begin --step uat-<run-id>` before the run; after an interruption rerun only scenarios with no result row.

## Results

| Result | Meaning |
|---|---|
| met | passed first try on every required viewport |
| met, flaky | passed only on the one retry; listed at S16; fixing the flakiness becomes a unit |
| not met | failed, or a page error / 5xx occurred |
| not run | skipped, quarantined, or could not execute; never a pass; a `must` not run blocks acceptance unless the owner waives it at S16 |
| owner runs | cannot be driven by machine; shown on the S16 board for the owner |

## When a scenario is not met

1. **Product wrong**: the serving units go back to build with the evidence, fresh worker one tier up, at most two escalations; then rerun the failed scenarios plus every other `must`.
2. **Script wrong**: a different worker fixes it against the brief wording; the scenario never changes.
3. **Scenario or criterion wrong or impossible**: reopen that item at Gate 0 (S10). The owner decides. An agent never edits the brief.
4. **App would not start, or an outside service is down**: a blocker, never met or not met.

Find the cause from the trace before retrying more than once. Escalation used up: S14.

## S16: acceptance

Board: brief and results side by side, scenario by scenario, with evidence links; not met, flaky, deferred, not run and owner-run items first. Question: "Does this meet the brief? Accept, or name what is not right." Recommend accepting only when every `must` scenario is met. Small runs ask together with merge: "All agreed scenarios met (report). Accept and merge?" Record with `approve --gate S16 --artifact docs/business/uat-report.md` and a decision log entry. Away: hold; nothing merges.
