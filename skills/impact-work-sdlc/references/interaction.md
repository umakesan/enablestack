# Interaction: how questions are asked

Read at phases 2-6.

## Invariant

Every message to the owner ends with at most one question.

## Question styles by phase

| Phase | Style | Why |
|---|---|---|
| 2 Discover | Open, describe-it questions with **no** suggested answer (brainstorming) | The owner's own words carry intent |
| 3 Business grill | Closed, one at a time, exactly **one** recommended answer with its reason (grill-me) | Fast convergence on business facts |
| 5 Technical grill | Same as 3, scoped to the decision nodes section n depends on | Grill before present |

Business grill asks only what is needed, for whom, what success looks like, and how a business person would check it. A technical question that comes up in phase 3 is written to the ledger with status `parked-technical` and asked in phase 5. The brief stays business-only.

For UI work, Impeccable's init and shape purpose/people/outcome/states questions join the same ledger and are asked once, inside discovery and the business grill (ui.md).

## Evidence before questions

A fact the agent can observe (code, docs, running something, a cheap prototype) is looked up and recorded with its `file:line` or artifact path, never asked. Only product or preference calls reach the owner. Lookups go to T0/T1 explorer workers.

## Grill ledger

`<store>/grill.md`, one row per node (template `assets/grill-ledger.md`). Write the row the moment the owner answers, before composing the next message. Record answers verbatim with who gave them.

## Rules

1. **Grill before present.** For design section n, close its nodes in dependency order, then present the section. "Does this look right?" is that message's one question.
2. **A correction reopens nodes, not the tree.** Mark affected nodes and their dependents `reopened`, re-grill only those, re-present section n. Approved sections stay approved unless they depend on a reopened node.
3. **Stopping rule.** A branch closes when every node is answered, evidenced, or defaulted. The owner can say "enough" or "use your defaults" at any time; open nodes become labeled `assumption` rows ("agent, my call") and are listed at Gate 0 (business) or in the written design (technical). After about ten questions in one phase or section, offer one checkpoint line: keep going, or default the rest.
4. **Builder check is the one sanctioned batch.** The written design's builder-check "theirs" pile (and any Critique Arena findings) arrives as one message, most important first, each item with a recommended answer.
5. **Arena choice** is one message with at most two options and one question; full candidates are linked, not pasted.
6. **Conflicting answers** (S11): show both verbatim, ask one question.

## Relay mode

When the owner sits behind a supervisor (for example firstmate) rather than in the session: one keyed question per round trip. No gate passes on silence; the question stays open and the run holds at that stop. Batching is allowed only for the builder-check pile.
