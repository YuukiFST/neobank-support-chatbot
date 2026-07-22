<!-- label: wayfinder:prototype -->
<!-- blocks: T04 -->
<!-- assignee: (unclaimed) -->

# T12 — Interface + delivery

## Question

Decide the platform the agent runs in and how the recruiter experiences it.

Decide: **FastAPI** backend shape (endpoints: chat, health, metrics; session handling; key stays server-side); the **web chat front** (Gradio/Streamlit for speed vs a small React app — delegable to an AI); local run via `docker compose` with Ollama; the **recorded demo** (GIF/video) that always works; optional **live path** via Groq free tier (no GPU needed). Bilingual PT+EN in the UI.

Output: interface spec + delivery/README plan (A primary: repo + demo; C optional: run live via Groq). Use `/prototype`. Feeds nothing downstream — this is a leaf toward the destination.
