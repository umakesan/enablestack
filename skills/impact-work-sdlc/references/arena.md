# Arena: 4A design and 6A critique

Read only for project-size runs, at phase 4A or 6A. Arena never builds; both phases sit before Gate A.

## Entry criteria

**4A Design Arena** runs when all of 1-3 hold, or 4 alone:
1. Size is project.
2. A one-way door is still open after grilling: data model or storage, public API or file format, auth or security boundary, cross-system integration, migration path, overall module decomposition (or the stack, stack.md).
3. Two or more structurally distinct plausible shapes remain, and no observable fact decides it (if one can, look it up or prototype instead).
4. The owner asks for an arena.

**6A Critique Arena** runs when criterion 2 held, the design touches security, money, or irreversible data, or the owner asks. Not by default when the owner's preference is token-tight.

**Skip** (announce in one line and write a `routing.tsv` skip row): quick or small size; every open decision reversible; one viable shape; a lookup or prototype answers it; owner said "no arena"; token-tight preference; a prior arena on the same frame concluded (resume it instead).

## Seats

Default 3 runners + 1 judge; 4 runners at most.

| Seat | Tier | Rule |
|---|---|---|
| R1 | T3 | Family A |
| R2 | T3 | Family B if reachable; else same family, different effort or generation, and the synthesis says "reduced diversity" |
| R3 | T2 | Different effort; alone carries "smallest thing that holds the invariants" |
| R4 (only on request or >2 named directions) | T2 | Any |
| J judge | T2-high or T3 | Different family from the conductor |

Seats differ by model, family and effort, never by persona.

## Independence

- One frame file (`assets/arena-frame.md`) is every seat's only input. The rubric (3-6 criteria; the business half comes from the approved brief) is withheld from runners.
- Fresh sessions: Claude `Agent` subagent or `claude -p`; Codex `spawn_agent` with `fork_turns: "none"` or `codex exec`. Without `fork_turns: "none"` a Codex seat inherits the conductor's leanings.
- Each seat writes only `arena/<run-id>/cand-<L>/{proposal,evidence}.md`. All seats launch in one message; the judge starts after all runners finish or drop out.
- Blind labels A, B, C with model names stripped; the reveal happens only in the synthesis after scoring.

## Synthesis (conductor, T3) - `assets/arena-synthesis.md`

1. Score each candidate per criterion with quoted evidence; compare with the judge; record which criterion caused any disagreement.
2. Claim ledger: every load-bearing claim with its seats and evidence. **Evidence beats count**: one evidenced claim outranks three reasoning-only ones.
3. Disagreement becomes work: a lookup or prototype (fact), a grill node with a recommendation (preference), or a named trade-off. Never averaged away. Wild divergence means the frame was under-specified: go back for the missing node and re-frame once; a second divergence goes to the owner.
4. Convergence is a finding: present one shape plus its strongest dissent; do not invent alternatives.
5. Graft by hand: name what is taken from which label and why.

**Owner message (S6):** why arena ran (one line), at most two options with three-line trade-offs, convergence or dissent, recommendation, one question ("Go with A+grafts?"). Candidates are linked, not pasted. A yes starts design sections, not building. "Your call" proceeds with the recommendation labeled "my call".

6A findings fold into the builder check's "theirs" pile; they never edit approved sections directly.

## Store and resume

`<store>/arena/<run-id>/` (run-id `<phase>-<UTC date>-<n>`): `frame.md`, `rubric.md`, `seats.tsv`, `cand-<L>/`, `judge.md`, `synthesis.md`. `inflight begin` before the fan-out. On resume, if the frame hash is unchanged, relaunch only seats with no `proposal.md`; if it changed, start a new run id and keep the old one. A synthesis with no recorded pick resumes at the owner question.
