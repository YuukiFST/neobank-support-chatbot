# Zero-cost deploy: hosting story for NeoBank

Ticket: [Deploy at zero cost](../issues/08-zero-cost-deploy.md)
Parent: [Map: NeoBank as an AI Engineer portfolio](../map.md)
Researched: 2026-08-14
Labels: `wayfinder:research`

## Scope and method

Every limit below was read from the vendor's own pricing or documentation page on 2026-08-14, and the URL is cited inline.
Where a number could only be found on third-party blogs, it is marked **unverified** rather than presented as fact.
Hard constraint applied throughout: no invoice, ever, and no credit card on file where it can be avoided.
Azure, AWS and GCP are out of scope as the primary platform per the map, so Google Cloud Run is evaluated only to be rejected on the record.

Two findings invalidate the assumptions the ticket was written with, so read these first.

1. **Hugging Face Spaces is no longer a free container host.**
   "Gradio and Docker Spaces run on compute and require a paid plan to create: PRO for personal accounts, Team or Enterprise for organizations."
   ([huggingface.co/docs/hub/spaces-overview](https://huggingface.co/docs/hub/spaces-overview))
   PRO is $9/month ([huggingface.co/pro](https://huggingface.co/pro)), which is an invoice, so Spaces is out.
   The only remaining free path is up to 2 Gradio Spaces on ZeroGPU for personal accounts in good standing, which is not a Docker path and not a FastAPI path.

2. **Koyeb was acquired by Mistral AI on 2026-02-17 and its free tier appears closed to new signups.**
   The acquisition itself is confirmed by Koyeb's own blog index ("entered into a definitive agreement to join Mistral AI", 2026-02-17, [koyeb.com/blog](https://www.koyeb.com/blog)) and by [TechCrunch](https://techcrunch.com/2026/02/17/mistral-ai-buys-koyeb-in-first-acquisition-to-back-its-cloud-ambitions/).
   Koyeb's pricing FAQ still documents the free Service ([koyeb.com/docs/faqs/pricing](https://www.koyeb.com/docs/faqs/pricing)), but multiple secondary sources report new users can only register for paid plans.
   **Unverified:** I could not confirm the free-tier closure on a Koyeb-owned page, and the docs contradict the secondary sources.
   Either way, the same FAQ says a credit card is required for account validation, which fails the constraint on its own.

## 1. The API (FastAPI in a container)

| Host | Free compute | Idle / cold start | Container support | Credit card | Source |
|---|---|---|---|---|---|
| Render Free | 512 MB RAM, 0.1 CPU; 750 free instance-hours per workspace per month | Spins down after 15 min without inbound traffic; spin-up "takes about one minute" | Dockerfile and native runtimes | Not required to sign up; without a payment method Render suspends instead of billing | [render.com/docs/free](https://render.com/docs/free), [render.com/docs/compute-plans](https://render.com/docs/compute-plans) |
| Koyeb Free | 512 MB RAM, 0.1 vCPU, 2 GB SSD, one Service, Frankfurt or Washington DC | Does not auto-scale to zero, so no cold start | Yes, "deploy containers from any registry" | **Required** for account validation | [koyeb.com/docs/faqs/pricing](https://www.koyeb.com/docs/faqs/pricing) |
| Hugging Face Spaces | CPU Basic 2 vCPU / 16 GB / 50 GB ephemeral is $0/hour, but creating a Docker or Gradio Space requires a paid plan | Free hardware sleeps after 48 h idle and restarts on visit | Docker SDK exists, gated behind PRO | PRO is $9/month | [huggingface.co/docs/hub/spaces-gpus](https://huggingface.co/docs/hub/spaces-gpus), [huggingface.co/docs/hub/spaces-overview](https://huggingface.co/docs/hub/spaces-overview) |
| Fly.io | "There is no free tier"; cheapest machine is $1.94/month (shared-cpu-1x 256 MB, syd) | n/a | Yes | "All organizations (except for Linked Organizations) require a credit card on file" | [fly.io/docs/about/pricing](https://fly.io/docs/about/pricing/) |
| Railway Free | $1 of usage credit per month; 1 vCPU, 0.5 GB RAM, 1 GB ephemeral, 0.5 GB volume | n/a | Yes | Trial states "No credit card required"; free plan terms unspecified | [railway.com/pricing](https://railway.com/pricing), [docs.railway.com/reference/pricing/plans](https://docs.railway.com/reference/pricing/plans) |
| Cloudflare Containers | None; requires Workers Paid at $5/month | Scales to zero | Yes | Paid plan required | [developers.cloudflare.com/containers/pricing](https://developers.cloudflare.com/containers/pricing/) |
| Cloudflare Workers Free | 100,000 requests/day, 10 ms CPU per request, 128 MB memory | n/a | No containers, no long-running process | Not required | [developers.cloudflare.com/workers/platform/limits](https://developers.cloudflare.com/workers/platform/limits/) |
| Google Cloud Run | 2,000,000 vCPU-s, 400,000 GiB-s, 1,000,000 requests, 1 GB egress per month | Scales to zero, cold start on first request | Yes, container-native | Billing account required; card needed once free tier is exceeded | [cloud.google.com/run/pricing](https://cloud.google.com/run/pricing) |
| Deta | Deta Space shut down; no current free offering to evaluate | — | — | — | (no live pricing page found) |

**Recommendation: Render Free web service, deployed from a Dockerfile.**
It is the only option that combines container support, no required credit card, and a documented permanent free tier from a vendor whose business is still general-purpose hosting.

**Rejected and why.**
Koyeb is technically the better product for a demo because its free Service never sleeps, but it demands a card for verification and its free tier is under a strategic cloud that just pivoted to enterprise AI inference.
Hugging Face Spaces was the ticket's leading candidate and is now simply a paid product for Docker.
Fly.io has no free tier and mandates a card.
Railway's $1/month credit cannot keep a 0.5 GB service running for a month.
Cloudflare Workers cannot host a LangGraph process at 10 ms CPU per request, and Cloudflare Containers costs $5/month.
Cloud Run has by far the best free allowance but is excluded twice over: the map puts large clouds out of scope, and it requires a billing account, which means a card and a real risk of an invoice.

**Two consequences of choosing Render that the build must absorb.**
The 15-minute spin-down means an interviewer's first request waits about a minute, so the README must say so and the frontend must show a warming state rather than a timeout.
512 MB RAM rules out running a local embedding model in the API process, so `bge-m3` must be replaced by a hosted embedding call (Gemini Embedding is on the free tier) or moved entirely to an offline ingestion step whose output is written to the database.

A keep-warm cron from GitHub Actions would consume roughly 730 instance-hours per month against the 750-hour allowance, leaving effectively no headroom for a second free service and no margin for error.
**Unverified:** whether Render's terms permit keep-warm pinging of a Free instance is not stated on the free-tier docs page, so treat this as an open question rather than a plan.

## 2. Managed Postgres

| Provider | Free storage | Compute | Idle behaviour | pgvector | Credit card | Source |
|---|---|---|---|---|---|---|
| Neon Free | 0.5 GB per project, up to 100 projects | 100 CU-hours per project per month (~400 h at 0.25 CU) | Autosuspend after 5 min, cannot be disabled on Free | **Yes**, "available on every Neon plan with no add-on or paid tier required" | "no credit card required" | [neon.com/pricing](https://neon.com/pricing), [neon.com/docs/introduction/plans](https://neon.com/docs/introduction/plans), [neon.com/docs/extensions/pgvector](https://neon.com/docs/extensions/pgvector) |
| Supabase Free | 500 MB database, 500 MB RAM shared CPU, 5 GB egress, 2 active projects | Shared | **Projects are paused after 1 week of inactivity** | **Yes**, `create extension vector` | Not stated on the pricing page | [supabase.com/pricing](https://supabase.com/pricing), [supabase.com/docs/guides/database/extensions/pgvector](https://supabase.com/docs/guides/database/extensions/pgvector) |
| Aiven Free | 1 GB storage, 1 GB RAM, 1 CPU, 1 dedicated VM | Dedicated but tiny | Not stated | **Probably not** — the plan table lists "Extensions (PostGIS, PL/v8, etc)" as Hobbyist-and-above | Not stated on the pricing page | [aiven.io/pricing](https://aiven.io/pricing) |
| Railway | No standalone free database; runs against the $1/month credit | — | — | Self-installed image | See above | [railway.com/pricing](https://railway.com/pricing) |
| Koyeb Postgres Free | 1 GB storage | **5 hours of active time per month** | — | Not stated | Required | [koyeb.com/docs/faqs/pricing](https://www.koyeb.com/docs/faqs/pricing) |

**Recommendation: Neon Free with pgvector.**
It is the only option that is explicitly card-free, explicitly permanent, and explicitly ships pgvector on the free plan.
Its 5-minute autosuspend is harmless because reconnects wake it, and it pairs naturally with an API that also sleeps.

**Rejected and why.**
Supabase pauses free projects after one week of inactivity, which is exactly the access pattern a portfolio demo has, and unpausing is a manual step an interviewer will never take.
Aiven's free plan appears to exclude extensions, which would defeat the whole point of collapsing the vector store into Postgres.
Koyeb's 5 active hours per month is not a database, it is a demo of a database.

The binding constraint is 0.5 GB per project.
A pgvector HNSW index over a real document corpus will hit that ceiling long before the corpus feels "large", so the RAG corpus ticket must size the corpus against 0.5 GB including index overhead, or shard across two Neon projects (100 are allowed) with the corpus in one and the operational tables in the other.

## 3. Separate vector store, if kept

| Provider | Free tier | Inactivity policy | Credit card | Source |
|---|---|---|---|---|
| Qdrant Cloud Free | Single node, 0.5 vCPU, 1 GB RAM, 4 GB disk, ~1M vectors at 768 dims | **Suspended after 1 week, deleted after 4 weeks** of inactivity | "You don't need a credit card to join" | [qdrant.tech/pricing](https://qdrant.tech/pricing/), [qdrant.tech/documentation/cloud/create-cluster](https://qdrant.tech/documentation/cloud/create-cluster/) |
| Pinecone Starter | Up to 2 GB storage, 1M read units/mo, 2M write units/mo, 1 GB egress/mo, 5 indexes, 100 namespaces per index | Not stated on the pricing page | Not stated on the pricing page | [pinecone.io/pricing](https://www.pinecone.io/pricing/) |
| Chroma Cloud Starter | $0/month plus usage, with $5 in free credits; writes $2.50/GiB, storage $0.33/GiB/month, queries $0.0075/TiB, network $0.09/GiB | Credits generally do not expire | Card accepted for Starter; the plan is usage-billed once credits run out | [trychroma.com/pricing](https://www.trychroma.com/pricing) |

**Recommendation: do not keep a separate vector store — collapse retrieval into Neon pgvector.**
This also fixes the existing embedding-mismatch bug in `chroma_client.py:45` by deleting the component that contains it.

**Rejected and why.**
Qdrant Cloud is the strongest free vector database on specs and needs no card, but a cluster that is deleted after four weeks of inactivity is disqualifying for an artifact whose entire purpose is to still work when someone clicks it three months from now.
Pinecone Starter has generous storage but its card and inactivity terms are not documented on the pricing page, so it cannot be certified card-free.
Chroma Cloud is usage-billed with a $5 credit, which is a metered invoice on a delay and directly violates the hard constraint.

## 4. Redis

| Option | Free tier | Credit card | Source |
|---|---|---|---|
| Upstash Redis Free | 256 MB max data, 500,000 commands/month, 10 GB bandwidth, 1 free database | Not required; "Once you enter your credit card, your database will be upgraded to the pay-as-you-go plan" | [upstash.com/pricing/redis](https://upstash.com/pricing/redis) |
| Render Key Value | No free instance type documented on the free-tier page | n/a | [render.com/docs/free](https://render.com/docs/free) |
| Postgres as queue and cache | Included in the Neon free plan already chosen | Not required | see §2 |

**Recommendation: eliminate Redis and move the queue into Postgres.**
The system runs as a single Render instance with no horizontal scaling available on the free tier, so the distributed-coordination argument for Redis does not apply.
A `SELECT ... FOR UPDATE SKIP LOCKED` job table gives the ingestion worker exactly the semantics `worker.py` needs, with transactional visibility a Redis list cannot offer, and it removes a whole free-tier account from the dependency surface.
Per-request rate limiting can live in-process for the same reason: one instance, one counter.

**Rejected and why.**
Upstash Free is genuinely card-free and would work, but 500,000 commands per month is a budget that a polling worker can exhaust by itself, and adding a fourth vendor to keep a component the architecture no longer needs is a net loss.
Keep Upstash documented as the fallback if the design later requires cross-process coordination.

This decision should be recorded as an ADR, since it reverses what the current code does.

## 5. Model inference (Gemini free tier)

**What is verifiable.**
Gemini's pricing page lists a Free Tier column reading "Free of charge" for input and output on `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.5-pro`, the `gemini-3.x` Flash and Flash-Lite families, and Gemini Embedding ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)).
The same page states that on the Free Tier, content **is** used to improve Google products, whereas on the paid tier it is not.
It also lists "Grounding with Google Search" as **Not available** on the Free Tier for these models.
Rate limits are "applied per project, not per API key", and exceeding them returns `429 RESOURCE_EXHAUSTED` ([ai.google.dev/gemini-api/docs/rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits)).
Leaving the free tier requires linking a Cloud Billing account and prepaying a minimum of $10 ([ai.google.dev/gemini-api/docs/billing](https://ai.google.dev/gemini-api/docs/billing)), which is a useful guarantee: the free tier cannot silently become an invoice.

**What is not verifiable.**
Google no longer publishes the per-model free-tier RPM / TPM / RPD table in its documentation.
The rate-limits page now says limits "can be viewed in Google AI Studio" and links to an authenticated dashboard at `aistudio.google.com/rate-limit`.
Third-party sources consistently report **10 RPM, 250,000 TPM and 250 RPD for `gemini-2.5-flash`** on the free tier, following a reduction Google applied on 2025-12-07, but **no Google-owned page confirms these numbers**, so they must be treated as unverified and re-read from the AI Studio dashboard by a human before any eval budget is planned around them.

**Tool calling on the free tier.**
The function-calling documentation states no tier restriction and demonstrates the feature on `gemini-3.6-flash` ([ai.google.dev/gemini-api/docs/function-calling](https://ai.google.dev/gemini-api/docs/function-calling)).
The pricing page separately marks *Grounding with Google Search* — a different, billed feature — as unavailable on the free tier.
So the working conclusion is that ordinary function calling is available for free, but this is inferred from the absence of a restriction rather than from a positive statement, and it should be confirmed with a one-request smoke test before the agent architecture depends on it.

**What happens when quota runs out mid-eval.**
The API returns `429 RESOURCE_EXHAUSTED` and the daily counter resets at the start of the next quota day.
If the widely reported 250 RPD figure holds, a single eval run of 30 cases through a multi-step agent averaging 8 model calls per case consumes 240 requests, which is one full day's quota for one run — so a naive eval-on-every-PR pipeline is impossible on the free tier.
The eval harness must therefore be built to survive this rather than to avoid it:

- Treat `429` as a **checkpointed pause**, not a failure — persist per-case results, and resume the run at the first unfinished case.
- Distinguish a quota exhaustion from a grader failure in the report, so an interviewer never sees a run that looks like the agent was wrong when it was only throttled.
- Use separate Google Cloud projects for the live demo and for eval runs, since limits are per project — the demo must not be able to starve the eval, or vice versa.
- Run the full LLM-backed eval **nightly on a schedule**, not per PR; per PR, replay recorded model responses (cassettes) so the graders and the harness are still tested on every change at zero quota cost.
- Keep the Ollama-on-RTX-3060 path as the reproducibility escape hatch the map already names, and make the model provider a single LiteLLM configuration switch so a quota wall becomes a config change, not a code change.

The free tier's data-use terms are a real consideration for a banking demo: prompts go into Google's product improvement pipeline, so the seeded demo data must be entirely synthetic and the README should say so explicitly.

## 6. CI/CD

| Item | Terms | Source |
|---|---|---|
| GitHub Actions on public repos | "GitHub Actions usage is free for self-hosted runners and for public repositories that use standard GitHub-hosted runners" — effectively unlimited minutes | [docs.github.com/billing/.../about-billing-for-github-actions](https://docs.github.com/en/billing/managing-billing-for-your-products/about-billing-for-github-actions) |
| GitHub Actions on private repos, Free plan | 2,000 minutes/month on standard runners | same |
| Render deploys | Free web services build and auto-deploy from a connected GitHub repo; builds count against included pipeline minutes | [render.com/docs/free](https://render.com/docs/free) |

The repository must stay **public** — that is the single decision that makes CI free, and it aligns with it being a portfolio artifact anyway.

Proposed pipeline shape, to be confirmed by the CI/CD ticket:

- **On every PR:** ruff, `mypy --strict`, unit tests, integration tests against an ephemeral Postgres service container, and the eval harness running on recorded cassettes. No live model calls.
- **On merge to `main`:** the same gates, then trigger the Render deploy, then a post-deploy smoke test that hits the public URL and asserts a health endpoint and one seeded read-only agent turn.
- **Nightly on a schedule:** the full eval suite against live Gemini, publishing accuracy, latency, token and cost-per-decision numbers as a build artifact and committing the report so the numbers are readable without running anything.
- **Never in CI:** anything that writes to the production demo database, so a failed deploy cannot corrupt the seeded state.

Note the tension flagged in §1: Render's pipeline minutes and the 750 free instance-hours share one budget, so a keep-warm cron and a chatty deploy pipeline compete for the same allowance.

## 7. The public demo problem

A banking agent that executes actions, exposed on the open internet with a free-tier model key behind it, has three distinct failure modes, and they need three distinct defences.

**Quota drain.** Anyone can burn the day's 250 requests in a minute and leave the demo dead for the rest of the day, which is the worst possible state for an artifact whose job is to be clicked by a stranger.
Defences: per-IP and global daily request caps enforced in the API before any model call; a hard cap on turns per session and tokens per turn; a circuit breaker that flips the demo into a pre-recorded transcript mode when the daily budget is spent, so the page still shows something coherent instead of a 429.

**Abuse of the action surface.** The whole point of the repositioning is that the agent really executes `pay_invoice`, `block_card` and `request_limit_increase`.
Defences: every demo session is bound to a **seeded synthetic customer** created per session and destroyed on a schedule, so an attacker can only act on their own throwaway record; no real payment, card or bank integration exists at all, only the local Postgres tables; a nightly job resets the demo dataset so accumulated damage has a bounded lifetime.

**Prompt injection and reputational content.** A public LLM endpoint will be jailbroken, and the transcript will be someone's screenshot.
Defences: keep the existing guardrails but stop pretending English-only regex is enough — this is a separate ticket; log every blocked attempt as an eval candidate, which is exactly the "every correction becomes a test" loop the map calls the sharpest idea in the job postings.

**On read-only mode:** a fully read-only public demo is the safest option but it deletes the single differentiator the whole repositioning is built on, so it is the wrong default.
The right shape is **actions enabled, blast radius zero**: real tool execution against per-session seeded data, with the human-approval step in the autonomy boundary being a genuine part of the demo rather than a safety bolt-on.

**On a recorded walkthrough:** record one regardless.
It costs nothing, it survives the free tier being throttled, changed or revoked, and it is what a busy interviewer actually watches.
The live URL proves the system runs; the recording proves what it does when it runs well; the committed eval report proves it does it repeatably.
All three should be linked from the top of the README.

## Recommended stack

| Component | Choice | Free-tier ceiling | Credit card |
|---|---|---|---|
| API | Render Free web service, Dockerfile deploy | 512 MB RAM, 0.1 CPU, 750 instance-hours/month, sleeps after 15 min idle, ~1 min cold start | Not required |
| Database | Neon Free | 0.5 GB storage/project, 100 CU-hours/project/month, autosuspend after 5 min | Not required |
| Vector store | Neon pgvector, same database | shares the 0.5 GB | Not required |
| Queue and cache | Postgres job table with `FOR UPDATE SKIP LOCKED`; no Redis | shares the 0.5 GB | Not required |
| Model inference | Gemini free tier via LiteLLM, `gemini-2.5-flash` class, Gemini Embedding for retrieval | rate limits unverified; see §5 | Not required; upgrading needs a $10 prepay, so no accidental billing |
| Local fallback | Ollama on the RTX 3060 12 GB, same LiteLLM interface | local hardware | n/a |
| CI/CD | GitHub Actions on a public repo, auto-deploy to Render on merge to `main` | unlimited standard-runner minutes | Not required |
| Demo protection | per-session seeded synthetic customer, per-IP and daily caps, nightly data reset, recorded walkthrough fallback | n/a | n/a |

No component in this stack requires a credit card, and no component is usage-billed, so there is no path by which an invoice appears.
The three real ceilings to design against are 0.5 GB of Postgres, 512 MB of API RAM, and an unverified but small daily Gemini request quota.

## Open questions for the human

1. **Read the actual Gemini free-tier limits from `aistudio.google.com/rate-limit` and paste them into this file.**
   Everything in §5 about eval budgeting rests on a number I could not verify from a public Google page, and the whole eval design changes if the real RPD is 50 rather than 250.
2. **Confirm with a single smoke test that function calling works on a free-tier key**, since acceptance criterion 3 is unbuildable if it does not.
3. **Does Render's free tier permit keep-warm pinging?** If yes, the cold start disappears at the cost of nearly the entire 750-hour allowance; if no, the README must own the one-minute wait.
4. **Is 0.5 GB enough for the "large corpus of real public documents" in criterion 4**, including the pgvector index? This needs a sizing estimate before the corpus ticket picks documents, and if it is not, decide between sharding across Neon projects or narrowing the corpus.
5. **Is the free tier's "content used to improve Google products" acceptable** for the demo, given all data is synthetic? I believe yes, but it is a governance claim the README will make and should be a deliberate decision, not an omission.
6. **Should Render be treated as a single point of failure worth hedging?** Its free tier is the last card-free container host standing after Spaces and Koyeb changed terms this year, and there is no obvious replacement if it follows them.
7. **Confirm the repository will be public**, which the CI cost model assumes and which the repo-rename question in the map is already adjacent to.
