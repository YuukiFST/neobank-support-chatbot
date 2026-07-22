# Wayfinder plan — how to use this folder

This is a **planning map** for building a flagship customer-support AI agent (job-prep portfolio). It is not code — it is the decisions to make *before* coding.

## Files
- `map.md` — the master plan: destination, fixed rules (Notes), decisions made, fog (not-yet-specified), out-of-scope.
- `tickets/` — one file per pending decision/task. Each has a `## Question` to resolve.

## Ticket labels
- `wayfinder:grilling` — resolve by discussion (one question at a time).
- `wayfinder:research` — resolve by reading docs/APIs; produce a summary.
- `wayfinder:prototype` — resolve by making a rough artifact to react to.
- `wayfinder:task` — do the manual work (e.g. verify hardware), record facts.

## How to work it (on the other PC)
1. Open `map.md`. Read the destination + Notes.
2. Pick the next **unblocked** ticket. A ticket's `<!-- blocks: Txx -->` lists what must close first; if that list is empty (or all listed tickets are done), it's takeable.
3. Resolve its Question. If using Claude Code / an AI: run `/wayfinder <this map>` and it drives one ticket per session.
4. Record the answer at the bottom of the ticket, mark it done, add a one-line entry to `map.md` → "Decisions so far".
5. Newly-unblocked tickets become takeable. Repeat until no tickets remain — then the path is clear and you build.

## Takeable now (no blockers)
- T01 — Verify local model runs + provider facts (task)
- T02 — Design e-commerce domain + knowledge base (grilling)
- T03 — AI-as-ally doc strategy (grilling)
- T04 — Repo skeleton + tooling (grilling)

Everything else waits on these.
