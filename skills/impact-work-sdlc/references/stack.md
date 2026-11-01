# Stack choice (S3)

Read only for a new project with no existing scaffold, after Gate 0.

> **Status: default method, not yet approved by the captain.** Built from the stack-skill research recommendation. Flag it at the S3 board until approved; swapping the evaluator is a one-line change here.

## Skip or shrink

- An existing codebase answers the stack question: no S3; record nothing new.
- The owner names the stack: record an ADR with "decided by: <owner>" and skip the evaluation.
- Small runs: one evaluation pass, no Arena.

## Method

1. **Constraints from the brief**: scale, budget, team skills, compliance, hosting, timeline, offline or mobile needs.
2. **Facts**: gather primary-source facts (current versions, licences, hosting limits, pricing) with mattpocock `research` when installed, otherwise direct lookups. Every ecosystem number (stars, downloads, last release, CVEs) is fetched live (GitHub API, npm/PyPI, OSV) or marked "estimate". Never invent a number.
3. **Evaluate**: `tech-stack-eval` (shawnpang/startup-founder-skills, pinned commit) when installed. If it is not installed, use the rubric below; preflight reports which.
4. **One-way door** (a new project usually is): run it inside PStack `arena` with 2-3 seats on the same frame (arena.md), a blind judge, conductor synthesis. Otherwise a single pass.
5. **Tie-break**: if two stacks stay close, a 1-2 hour throwaway spike (mattpocock `prototype` or PStack Prototype playbook) settles it with evidence.
6. **S3 board**: matrix, cost, risks, recommendation with confidence, one question.
7. **Record**: an ADR in `docs/adr/` in mattpocock `domain-modeling` format (1-3 sentences, optional status, options, consequences), plus a decision log entry when cost, hiring, or lock-in is affected.

## Built-in rubric (fallback)

- Start from the problem and the team, not the technology; push back on solution-first framing.
- 2-4 candidates, including the simplest that could work.
- 6-8 weighted criteria drawn from the brief's constraints (for example: fit to scenarios, team familiarity, operating cost over 12 months, hosting simplicity, ecosystem health, security posture, migration cost later).
- Score 1-5 with a one-line reason each; weights sum to 100.
- End with one winner and a confidence level. No "it depends" without a follow-up question.

## Tiers

Evaluation seats and judge T2 (different family from the conductor when reachable); synthesis and the owner conversation T3; fact fetching T0 or scripted.
