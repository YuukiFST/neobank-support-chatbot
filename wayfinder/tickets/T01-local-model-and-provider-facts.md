<!-- label: wayfinder:task -->
<!-- blocks: (none) -->
<!-- assignee: (unclaimed) -->

# T01 — Verify local model runs + pin provider setup facts

## Question

The provider design is decided (LangChain abstraction: Groq free API as default, local Ollama Qwen3.5-9B as power option, env-flag switch). What remains is factual verification other tickets depend on:

1. Does the target PC actually run **Qwen3.5-9B** quantized? Capture RAM/VRAM, pick quantization (Q4/Q5), measure tokens/sec. If it can't, name the fallback local model.
2. Exact **Ollama tag** for Qwen3.5-9B (and the embedding model tag, e.g. `nomic-embed-text`).
3. **Groq** free-tier facts: sign up, get key, note the free models available (e.g. Llama-3.x), rate limits, and that no billing/card is attached.
4. Confirm the LangChain packages: `langchain-groq`, `langchain-ollama`, `init_chat_model` behavior for switching.

Record: model tags, quantization, measured speed, Groq free models + limits, where the key lives (server-side env only). These facts feed Memory (T07) and Interface/delivery (T12).
