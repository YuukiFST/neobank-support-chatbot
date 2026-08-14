# Research: Observability and cost per decision

Ticket: [Observability and cost per decision](../issues/06-observability-and-cost.md)
Parent: [Map: NeoBank as an AI Engineer portfolio](../map.md)
Researched: 2026-08-14
Constraint governing every recommendation: zero invoice, ever.

## Executive summary

Recommended stack, one line each:

- **Tracing:** Langfuse Cloud Hobby as the live backend, plus a committed JSONL/Markdown trace export in the repo as the durable portfolio artifact.
- **Cost model:** LiteLLM's `model_prices_and_context_window.json` as the price source, pinned per release, with every number labelled `estimated_cost_usd` and a `billed: false` flag.
- **Attribution unit:** the **agent turn** is the primary unit; the **resolution** is the reporting unit; tool calls and LLM calls are child spans that roll up.
- **Metrics:** eight agentic metrics defined below, all computed from the trace store rather than from ad-hoc counters.
- **Dashboard:** an in-app `/metrics/report` page rendered server-side plus a committed static HTML snapshot; Grafana stays for the local `docker compose` path only.

A caveat that shapes everything below: **verification of vendor free tiers in August 2026 is partly blocked.**
Langfuse and Grafana publish exact free-tier numbers on public pricing pages and those are cited.
Google no longer publishes a static free-tier rate-limit table — the docs now say limits "can be viewed in Google AI Studio" behind a login ([ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)).
Every RPM/RPD figure circulating in blog posts for Gemini free tier is therefore unverifiable from a primary source, and this document does not quote one.

---

## 1. Tracing backend under zero cost

### The four candidates, measured

| Option | Free-tier limit | Credit card | LangGraph / LiteLLM integration | Survives as portfolio artifact |
|---|---|---|---|---|
| Langfuse Cloud (Hobby) | 50,000 units/month, 30-day data access, 2 users | **No** | Native, both | Only for 30 days |
| Langfuse self-hosted | Unlimited, MIT-licensed core | N/A | Identical to Cloud | Only while the stack runs |
| OTel + free collector (Grafana Cloud) | 50 GB traces/month, 14-day retention, 3 users | **No** | Generic, no LLM semantics | Only for 14 days |
| Own JSONL | Unlimited | N/A | Manual instrumentation | **Permanently, in git** |

**Langfuse Cloud Hobby** is free at 50,000 units/month with 30-day data access, 2 users, and no credit card ([langfuse.com/pricing](https://langfuse.com/pricing)).
The billable unit is *any* tracing data point — "traces, observations (individual steps: spans, events, and generations), and scores" ([langfuse.com/pricing](https://langfuse.com/pricing)).
That definition is the trap for this project specifically.
A 9-node LangGraph run instrumented at node granularity emits roughly one trace + 9 span observations + n LLM generations + n tool spans + any eval scores.
Call it 15–25 units per agent turn as a working estimate; that puts the ceiling somewhere around 2,000–3,000 turns per month, which is plenty for demos but can be consumed in a single careless eval sweep over a few hundred cases with multiple graders.
The eval harness must therefore either sample its tracing or write to a separate local sink — see the recommendation.

**Langfuse self-hosted** is genuinely unrestricted: as of June 2025 every product feature (tracing, prompt management, evals, playground, annotation queues) is MIT-licensed, with only enterprise compliance features (SCIM, audit logs, project-RBAC, UI customisation) behind a commercial licence ([langfuse.com/self-hosting](https://langfuse.com/self-hosting)).
The cost is operational, not financial.
Self-hosting requires Postgres, **ClickHouse**, Redis/Valkey, S3-compatible blob storage, and two application containers (web + worker) ([langfuse.com/self-hosting](https://langfuse.com/self-hosting)).
The docs are explicit that the Docker Compose path is for "testing and low-scale deployments" and "lacks high-availability, scaling capabilities, and backup functionality" ([langfuse.com/self-hosting](https://langfuse.com/self-hosting)).
That footprint does not fit any free hosting tier this project can plausibly use, and it doubles the `docker compose` weight of a repo whose reviewer will never run it.

**Integration quality is a tie between the two Langfuse options and a clear loss for raw OTel.**
LangGraph is traced through the LangChain `CallbackHandler` — `config={"callbacks": [langfuse_handler]}` on graph invocation — capturing node executions, tool calls, LLM invocations, nested agent hierarchies, token usage and cost ([langfuse.com/integrations/frameworks/langgraph](https://langfuse.com/integrations/frameworks/langgraph)).
Two caveats from that page matter here: Python 3.11+ is required (fine, the project is on 3.12), and under LangGraph Server the callback must be attached at compile time via `.with_config()` rather than per-invocation.
LiteLLM logs to Langfuse either through the proxy callback or the SDK, with "token usage, cost, and latency captured per request" ([langfuse.com/integrations/gateways/litellm](https://langfuse.com/integrations/gateways/litellm)).

**OpenTelemetry with a free collector** is the option that looks most "production" and delivers least here.
Grafana Cloud Free is real and cardless: 50 GB traces/month, 10k active metric series, 50 GB logs, all at 14-day retention, 3 active Grafana users ([grafana.com/pricing](https://grafana.com/pricing)).
But generic OTel carries no LLM semantics out of the box — no prompt, no completion, no token/cost fields — so you get spans with durations and nothing an AI-engineering interviewer cares about.
The GenAI semantic conventions that would supply those fields have been moved out of the main semconv repo into a dedicated `open-telemetry/semantic-conventions-genai` repository, and **I could not verify their current stability designation from the primary source** — the repo landing page does not state it and the old spec page is a redirect notice ([opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/)).
Treating them as stable in August 2026 would be a guess.
Worth knowing regardless: Langfuse itself speaks OTLP/HTTP on `/api/public/otel/v1/traces`, so choosing Langfuse does not lock the project out of OTel — the app can emit standard OTel spans and point the exporter at Langfuse ([langfuse.com/integrations/native/opentelemetry](https://langfuse.com/integrations/native/opentelemetry)).

**Own JSONL** is the only option where the artifact outlives the vendor.
It is also the only one that survives the eval harness running a few hundred cases in CI without touching a quota.

### The portfolio-artifact question, which decides this

Langfuse supports making an individual trace or session public via a shareable link that requires no login ([langfuse.com/docs/observability/features/url](https://langfuse.com/docs/observability/features/url)).
That sounds like the answer, and it half is.
The blocker is retention: Hobby gives **30-day data access** ([langfuse.com/pricing](https://langfuse.com/pricing)).
A trace link pasted into a README rots in a month, and a dead link in a portfolio is worse than no link.
Grafana Cloud Free is worse still at 14 days ([grafana.com/pricing](https://grafana.com/pricing)).

**Recommendation: Langfuse Cloud Hobby as the live backend, with a committed trace export as the durable artifact.**

Concretely:

1. Wire the Langfuse LangChain `CallbackHandler` into the compiled LangGraph, and enable the LiteLLM Langfuse callback so token/cost land on generations automatically.
2. Add a second, always-on sink: a `TraceRecorder` writing one JSON object per turn to JSONL, dependency-injected so tests get a named in-memory fake.
3. Gate the Langfuse sink behind an env flag and default it **off in CI** so the eval suite never burns the 50k-unit budget.
4. Commit a curated handful of exported traces (happy path, tool call, approval-gated action, guardrail block, escalation) into `docs/traces/` as JSONL plus a rendered Markdown view.
5. Put the live Langfuse share links in the README next to the committed exports, labelled as "live trace (may expire)".

**Rejected: Langfuse self-hosted.** Postgres + ClickHouse + Redis + S3 + two app containers is a second system to operate for a project that already has enough moving parts, and no free host will run it.
**Rejected: OTel + Grafana Cloud as the primary trace store.** LLM-specific semantics are not settled, 14-day retention is shorter than Langfuse's, and the resulting traces show durations instead of decisions.
**Rejected: JSONL alone as the only backend.** It costs a reviewer real effort to read raw JSONL, and "I built my own tracing" reads as not knowing the standard tool — the tool is table stakes, the export is the differentiator.

---

## 2. Cost per decision when the bill is zero

### Where the price tables come from

Two viable sources, and they differ in maintenance burden.

**LiteLLM's `model_prices_and_context_window.json`** is a single community-maintained JSON covering 100+ providers, fetched from GitHub at runtime by default with a local `model_prices_and_context_window_backup.json` fallback ([github.com/BerriAI/litellm](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json), [docs.litellm.ai/docs/completion/token_usage](https://docs.litellm.ai/docs/completion/token_usage)).
The project already depends on LiteLLM, so `response._hidden_params["response_cost"]` and `completion_cost()` are available with zero new dependencies.
LiteLLM's own docs describe this as a "community maintained list" — that is an accuracy caveat worth stating out loud in an ADR rather than pretending the number is authoritative.
The docs do not describe fallback behaviour for a model absent from the map (an Ollama tag, for instance), so the code must handle a `None`/0 cost explicitly instead of assuming.

**Langfuse's own price table** is the second source: it ships predefined prices for popular OpenAI, Anthropic and Google models, with "a daily automated audit" verifying prices against official provider documentation, and it accepts custom model definitions via UI or Models API for self-hosted and fine-tuned models ([langfuse.com/docs/observability/features/token-and-cost-tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)).
Critically, ingested cost wins over inferred cost on that page — so the app can compute the number itself and ship it, and Langfuse will not overwrite it.

**Vendor pages are the ground truth for spot checks.**
Google publishes per-model per-1M-token prices at [ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), and that page states the free tier is literally "Free of charge" for input and output on the Flash-class models, with the tradeoff spelled out as "Content used to improve our products" on free tier versus "Content **not** used to improve our products" on paid.
That last line is a governance detail this project should surface, not just a pricing footnote.

### Keeping prices current without a subscription

Do not fetch prices at request time.
A runtime fetch makes cost non-reproducible: the same eval run replayed next month yields a different number, which destroys the ability to compare a regression against a baseline.

Recommended mechanism:

- Vendor a `pricing/model_prices.json` into the repo, derived from LiteLLM's map, holding only the handful of models this project actually uses.
- Stamp it with `source_url`, `source_commit_sha`, and `fetched_at`.
- Add a weekly GitHub Actions job that re-fetches upstream, diffs the models in use, and opens a PR when anything moved — free minutes on a public repo, and the PR itself is evidence of an LLMOps habit.
- Fail the eval suite loudly if a model in a run has no price entry, rather than silently recording zero.

### The honest label

The number is a **counterfactual**, not a receipt, and the schema should say so rather than the README doing it in prose.

Proposed field naming, replacing the dead `cost_brl_equiv` field at `shared/domain/models.py:152`:

```
estimated_cost_usd: float          # computed from the pinned price table
cost_basis: "public_price_table"   # never "invoice"
billed: false                      # free tier — nothing was actually charged
pricing_source_sha: "<commit>"     # which table produced this number
provider_tier: "gemini_free"       # or "ollama_local"
```

For Ollama there is no vendor price, so `estimated_cost_usd` must be `null` with `cost_basis: "local_inference"` — not zero.
Zero would imply local inference is free, which conflates "no invoice" with "no cost" and is exactly the sloppiness a senior reviewer probes.
If a comparable figure is wanted for Ollama, compute it as a *shadow price*: what the same token counts would have cost on the reference hosted model, stored in a separate `shadow_cost_usd` field with the reference model named.

The one-line framing for the README: *"Costs are computed from published price tables against measured token counts; the system runs on free tiers, so no invoice exists. The point is the instrumentation, not the number."*

**Recommendation: LiteLLM price map, vendored and pinned, with a weekly refresh PR; every cost field carries `billed: false` and its pricing-table SHA.**
**Rejected: runtime fetch from `api.litellm.ai`.** Non-reproducible costs make eval baselines meaningless and add a network dependency to a hot path.
**Rejected: hand-maintained price constants.** They go stale silently, and the staleness is invisible in the output.

---

## 3. The attribution unit

Four candidates were on the table: HTTP request, agent turn, tool call, full resolution.

**HTTP request is wrong** because it is an artifact of transport, not of the agent.
One request may run a 9-node graph with three LLM calls, or it may hit a cache and return in 4 ms.
Averaging those together produces a p95 latency that describes nothing, and streaming responses break the request boundary entirely.

**Tool call is too fine to be the primary unit** but is essential as a child span.
A tool call has no independent cost — it exists because an LLM decided to call it — so attributing cost to it double-counts or under-counts depending on how you allocate the deciding LLM call.

**Full resolution is the unit the business cares about and the one a hiring manager understands**, but it is unusable as the primary instrumentation unit because it can span days when a human approval is pending.
You cannot compute a latency histogram over a unit whose duration includes an operator's lunch break.

**The agent turn is the right primary unit.**
Definition: one user input entering the graph through to the graph emitting a user-visible response or halting at an approval gate.
It is the smallest unit that contains a complete decision, it has a clean start and end, its cost is the sum of its child LLM generations with no allocation ambiguity, and its latency is meaningful because it is bounded by machine work.
It maps one-to-one onto a Langfuse trace, which makes the instrumentation fall out naturally.

**Recommendation: instrument at three nested levels, report at two.**

```
resolution   (session_id)      -> business unit: cost & turns to resolve, wall-clock excluded from latency SLO
  turn       (trace_id)        -> PRIMARY unit: cost per decision, latency p50/p95, tool-selection correctness
    step     (span_id)         -> LLM generation / tool call / retrieval; diagnostic only, rolls up
```

Report **cost per turn** and **cost per resolution**; report **latency per turn** only.
For resolution latency, split it into two numbers that never get averaged together: `agent_time` (sum of turn durations) and `wait_time` (time blocked on human approval).
Merging them is the single most common way this metric gets faked, and separating them is a cheap thing to point at in an interview.

**Rejected: HTTP request.** Transport boundary, not decision boundary.
**Rejected: tool call as primary.** No independent cost, ambiguous allocation.
**Rejected: full resolution as primary.** Human wait time makes the latency distribution meaningless.

---

## 4. Agentic metrics worth instrumenting

Generic web metrics (RPS, error rate, p95) are necessary and boring; they already have a Prometheus histogram at `shared/infrastructure/observability.py:36`.
These eight are the ones that say "this person has run an agent in production".

All of them should be **derived from the trace store**, not incremented by scattered `Counter.inc()` calls.
The existing dead counters at `observability.py:34-42` are the evidence for why: a counter incremented at a call site is invisible when the call site is not exercised, and nobody notices for months.
Derive from traces, then export the derived values to Prometheus in one place.

### 4.1 Tool-selection accuracy (production)

The hard part is that production has no labels.
Three tiers, in increasing honesty cost:

- **Offline (labelled):** eval cases carry an `expected_tool` field; accuracy is exact-match on the tool name, plus a separate argument-correctness score. This is the number that goes in CI.
- **Production proxy:** count `tool_error_rate` (tool raised or returned a domain error), `tool_retry_rate` (same tool called twice in a turn with different args), and `abandoned_tool_rate` (tool result never referenced in the final response). None of these is accuracy; all three correlate with it.
- **Production ground truth:** operator corrections. The Amazon posting's loop from the map — every correction becomes a test — means a corrected turn writes an eval case with the operator's tool choice as the label. Accuracy then becomes measurable on exactly the traffic that was hard.

Report the offline number as "tool selection accuracy" and the production ones under their own names.
Calling a proxy "accuracy" is the dishonesty an interviewer will find.

### 4.2 Autonomy-boundary violations

Requires the boundary to be a declared object, not a convention: a policy table mapping `tool -> max_autonomous_risk` with an explicit approval requirement above it.
A violation is any span where a tool executed with `requires_approval == true` and no `approval_id` on the trace.
Target is exactly zero, and it must be a **hard gate in CI**, not a dashboard number — a metric that is supposed to always be zero belongs in a test, and only belongs on the dashboard as proof it is being watched.
Instrument it as `boundary_violations_total{tool, reason}` and additionally as a `boundary_blocks_total` — the count of times the boundary correctly *stopped* something, which is the number that shows the mechanism is live rather than dead code.

### 4.3 Approval-queue depth and wait

Depth is a Gauge sampled from the approvals table: `approval_queue_depth{risk_tier}`.
Wait is a Histogram of `approved_at - requested_at`, recorded on resolution, bucketed in minutes not seconds.
Add `approval_outcome_total{decision}` over approved / rejected / expired.
The rejection rate is the interesting one: a rejection rate near zero means the gate is theatre and the agent should have been allowed to act; a high rate means the agent's judgment is poor. Neither extreme is good, and saying that out loud is a strong signal.

### 4.4 Retrieval hit rate

The existing `KB_RETRIEVALS` / `KB_CACHE_HITS` pair at `observability.py:41-42` measures cache hits, which is a performance metric, not a retrieval-quality metric. Keep it, rename it, and add the real ones.

On a labelled eval set, per query: `recall@k`, `MRR`, and `hit_rate@k` (fraction of queries where at least one relevant chunk is in the top k).
In production without labels, use `grounding_rate`: the fraction of answers where the cited chunk ids are a non-empty subset of the retrieved set, plus `no_result_rate` and `low_score_rate` (top similarity below a threshold).
Track retrieval separately from the agent, per acceptance criterion 4 in the map — a joint number hides which half is broken.

### 4.5 Escalation rate

`escalations_total / turns_total`, sliced by trigger reason: guardrail block, low confidence, tool failure, explicit user request, policy requirement.
The reason slice is what makes this diagnostic rather than decorative.
A rising escalation rate with a stable reason mix is load; a shifting mix is a regression.
The `ESCALATIONS` counter at `observability.py:40` already exists with an `intent` label — add `reason`.

### 4.6 Trust score (P3)

There is no standard definition, so the honest move is to define it explicitly and defend the definition rather than borrow a number that sounds authoritative.
Proposal: a per-turn composite in [0,1], stored as a Langfuse score so it is visible on the trace.

```
trust = w1 * grounded            (every factual claim maps to a retrieved chunk)
      + w2 * tool_success        (no tool errors in the turn)
      + w3 * within_boundary     (no approval bypass)
      + w4 * (1 - contradiction) (answer does not contradict retrieved context)
```

Compute it with a cheap LLM-as-judge on the free tier for the grounding and contradiction terms, deterministically for the other two.
Publish the weights, publish the judge prompt, and publish the judge's own agreement rate against a small human-labelled set — an unvalidated LLM judge is a number with no error bars, and stating its agreement rate is the difference between a metric and a vibe.

### 4.7 Cost per decision

`estimated_cost_usd` per turn, p50 and p95, sliced by intent and by whether the turn used tools.
The p95/p50 ratio is the interesting derived value: a wide spread means a subset of turns is looping.

### 4.8 Turns to resolution

Median turns per resolved session, plus the fraction of sessions exceeding a turn budget.
This is the metric that catches an agent that is technically accurate but exhausting to use, and almost no portfolio has it.

**Recommendation: derive all eight from the trace store in one `metrics/derive.py` module, export to Prometheus from that single place, and mirror the per-turn scores into Langfuse as scores so they appear on the shareable trace.**
**Rejected: incrementing counters at call sites.** That pattern is what produced the four dead counters this ticket exists to fix.

---

## 5. The dashboard

The framing in the ticket is right: the reviewer will never run `docker compose`.
Optimise for the reviewer who has a browser tab and four minutes.

Grafana's cost is not money — Grafana OSS is free and Grafana Cloud Free is cardless at 10k active series and 14-day retention ([grafana.com/pricing](https://grafana.com/pricing)).
Its cost is that it is a *separate system* whose value is invisible unless someone runs it, and a JSON dashboard definition in the repo is unreadable as evidence.
The current 219-byte panel-less `ops/grafana/dashboards/neobank.json` is worse than nothing, because it is a claim with no substance behind it.

An in-app page has the opposite profile: it is reachable from the public deploy, it can be screenshotted into the README, and it can show things Grafana structurally cannot — a trace tree with the tool calls, the approval queue with its pending items, the eval run history with per-metric deltas.
Grafana is built for time-series over infrastructure; this project's most interesting numbers are per-decision records, which are rows, not series.

**Recommendation: a purpose-built `/report` page in the app, server-rendered, plus a static snapshot committed to the repo.**

Shape of it:

- **Header:** last eval run — action accuracy, tool-selection accuracy, retrieval recall@k, p95 turn latency, estimated cost per turn, each with the delta against the previous run and each labelled with the free-tier caveat.
- **Cost panel:** estimated cost per turn and per resolution, with `billed: false` and the pricing-table SHA rendered on the page, not hidden in a tooltip.
- **Autonomy panel:** boundary blocks, boundary violations (should read 0), approval queue depth, median approval wait, approval outcome mix.
- **Trace explorer:** the curated committed traces from `docs/traces/`, rendered as expandable trees, working with no database and no API key.
- **Links out:** live Langfuse share links, marked as expiring.

The static snapshot matters as much as the live page: regenerate it in CI on every eval run and commit it, so the numbers are visible on GitHub even when the deploy is cold or the free tier is exhausted.

Keep Prometheus and keep a **real** Grafana dashboard for the local path — deleting them would remove a legitimate skill signal, and six of eight postings ask for production observability, which conventionally means exactly this stack.
But fix the empty JSON file or delete it; an empty dashboard is a broken promise of the same kind this whole repositioning exists to eliminate.

**Rejected: Grafana as the primary dashboard.** Invisible to a reviewer who does not run the stack, and structurally poor at per-decision rows.
**Rejected: deleting Grafana/Prometheus entirely.** They are asked for by name in the target postings, and the marginal cost of keeping a working local dashboard is small.

---

## Facts that could not be verified

Stated plainly rather than estimated:

- **Gemini free-tier RPM/TPM/RPD.** Google's rate-limit documentation no longer publishes a static table and defers to a logged-in AI Studio page ([ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)). Blog aggregators disagree with each other by a factor of three on the same model. Someone with a Google account must read the AI Studio rate-limit page and record the numbers; ticket 08 needs this too.
- **Whether Gemini free tier supports tool/function calling without restriction.** Not confirmed from a primary source in this pass. This is load-bearing for acceptance criterion 3 and should be resolved by an actual API call, not by documentation.
- **Stability status of the OpenTelemetry GenAI semantic conventions.** They moved to `open-telemetry/semantic-conventions-genai` and neither the redirect page nor the repo landing page states a stability designation ([opentelemetry.io/docs/specs/semconv/gen-ai](https://opentelemetry.io/docs/specs/semconv/gen-ai/)). Treat as unstable until confirmed.
- **Exact Langfuse units consumed per LangGraph turn.** The unit definition is documented ([langfuse.com/pricing](https://langfuse.com/pricing)) but the per-turn count depends on this graph's instrumentation depth. The 15–25 figure above is a reasoned estimate, not a measurement. Measure it on the first 50 real turns and revise the CI-tracing policy accordingly.
- **LiteLLM's behaviour for a model absent from the price map.** Undocumented on the token-usage page ([docs.litellm.ai/docs/completion/token_usage](https://docs.litellm.ai/docs/completion/token_usage)). Determine empirically with an Ollama model before relying on it.

---

## Open questions for the human

1. **Is a Langfuse Cloud account acceptable at all?** It is cardless and free, but it means production traces (including any synthetic customer data) leave the machine and sit on a third party's infrastructure. If the answer is no, the fallback is JSONL plus the in-app trace explorer, losing the recognisable-tool signal but losing no capability.
2. **Free-tier data usage.** Gemini's pricing page states free-tier content is "used to improve our products" while paid-tier content is not ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)). For a banking-domain project with synthetic data this is probably fine, but it is a governance point the README should declare, and you should decide whether to declare it as a limitation or as a deliberate accepted risk.
3. **Trust score weights.** The `w1..w4` composite above is a proposal. Do you want to own that definition and defend it in an interview, or drop trust score (it is marked P3) and ship the seven metrics that need no invented formula?
4. **Does the eval suite trace to Langfuse at all?** Tracing every eval case is the best artifact and the fastest way to burn 50k units. Options: never trace in CI, trace a fixed 10-case sample, or trace only failures. Recommend "failures only", but it is a real tradeoff.
5. **Cost currency.** The dead field is `cost_brl_equiv` (BRL). Price tables are USD. Reporting in BRL requires an FX rate, which is another thing to pin and keep current for no analytical gain. Recommend dropping BRL and reporting USD only — confirm, since the domain is Brazilian.
6. **Who reads the report page — is it public?** If the in-app `/report` is publicly reachable on the zero-cost deploy, it exposes usage volumes and possibly prompt content from the trace explorer. Decide whether it is public with curated static traces only, or auth-gated with a public screenshot in the README.
7. **Ordering against ticket 08.** This ticket's recommendation assumes a host exists that can run the FastAPI app; it deliberately does not assume one that can run ClickHouse. If ticket 08 lands a host that could run self-hosted Langfuse for free, the recommendation in section 1 is worth revisiting.

## Sources

- [Langfuse pricing](https://langfuse.com/pricing)
- [Langfuse self-hosting](https://langfuse.com/self-hosting)
- [Langfuse LangGraph integration](https://langfuse.com/integrations/frameworks/langgraph)
- [Langfuse LiteLLM integration](https://langfuse.com/integrations/gateways/litellm)
- [Langfuse token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)
- [Langfuse OpenTelemetry integration](https://langfuse.com/integrations/native/opentelemetry)
- [Langfuse trace URLs and public sharing](https://langfuse.com/docs/observability/features/url)
- [Grafana pricing](https://grafana.com/pricing/)
- [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [LiteLLM model price map](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json)
- [LiteLLM token usage and cost](https://docs.litellm.ai/docs/completion/token_usage)
- [OpenTelemetry GenAI semantic conventions (redirect notice)](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
