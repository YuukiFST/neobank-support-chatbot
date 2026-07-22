<!-- label: wayfinder:grilling -->
<!-- blocks: T01, T05 -->
<!-- assignee: (unclaimed) -->

# T07 — Memory architecture (short + long + semantic)

## Question

The job names "agent memory and conversational history" explicitly — design all three tiers.

Decide:
- **Short-term:** conversation history window — how many turns, summarization/trimming strategy (LangGraph checkpointer).
- **Long-term:** persistent facts across sessions — what to store (customer profile, past tickets, preferences), the store (SQLite? LangGraph store?), when to write, when to recall.
- **Semantic / RAG:** vector store (Chroma/FAISS, local, free) over the knowledge base + past tickets; local embeddings (Ollama `nomic-embed-text` or sentence-transformers); retrieval trigger and how results enter the prompt.

Output: memory design doc with the tier boundaries and the write/recall rules. Graduates the deep-RAG fog. Use `/grilling`.
