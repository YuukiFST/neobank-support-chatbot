# 01 — Qual modelo local roda o experimento numa RTX 3060 12 GB

Type: research
Status: resolved
Blocked by: —

## Question

Qual modelo de linguagem local a RTX 3060 12 GB consegue rodar com tool calling confiável, latência representativa e reprodutibilidade, para servir aos dois arms do experimento?

Candidatos levantados pelo usuário:

- `prism-ml/Bonsai-27B-gguf`
- `unsloth/gemma-4-12b-it-NVFP4`

Suspeitas a confirmar ou derrubar com fontes primárias:

1. NVFP4 tem aceleração nativa apenas em Blackwell (RTX 50xx); a 3060 é Ampere. O modelo NVFP4 roda nessa placa? Com qual runtime? Com qual penalidade?
2. Um 27B em GGUF Q4 ocupa mais que 12 GB de VRAM. Que quantização cabe inteira na placa, e o que a queda de quantização faz com a qualidade de tool calling?
3. Offload parcial para RAM contamina a métrica de latência do artigo — quantificar o impacto.

Entregar também:

- Quais dos candidatos suportam tool calling / function calling estruturado no runtime disponível (Ollama, llama.cpp, vLLM).
- Alternativas fortes na faixa de 7B-14B com tool calling comprovado, caso os dois candidatos falhem.
- Como fixar aleatoriedade (seed, temperatura) no runtime escolhido, já que reprodutibilidade é requisito do artigo.
- Como medir tokens de entrada e saída e latência no runtime escolhido.

## Answer

Resolvido em 2026-07-31. Investigação completa em `research/01-modelo-local.md`, com URL primária por afirmação e marcação explícita do que é inferência e do que não foi encontrado.

**Recomendação:** modelo principal **Qwen3.5-9B** em GGUF Q6_K (7,46 GB) ou Q8_0 (9,53 GB) — já é o modelo do `.env.example` deste repo, cabe inteiro nos 12 GB mesmo em Q8_0, e pontua 66,1 no BFCL-V4 e 79,1 no τ²-Bench.
Caber em Q8_0 abre uma possibilidade útil: rodar Q4 como condição de operação e Q8 como controle de quantização.
Reserva: **Gemma 4 12B** no GGUF QAT de primeira parte do Google (6,98 GB).
Runtime: `llama-server` para as execuções medidas, Ollama apenas para desenvolvimento.

**Os dois candidatos originais foram derrubados, por motivos diferentes:**

- `gemma-4-12b-it-NVFP4` — FP4 só tem tensor core nativo em Blackwell (`sm_100a`/`sm_120a` no PTX ISA); a RTX 3060 é `sm_86` e não tem nem FP8. O vLLM cai silenciosamente em Marlin W4A16, não roda nativamente em Windows, e o checkpoint nem converte para GGUF por ter dois `config_groups`.
- `prism-ml/Bonsai-27B-gguf` — rejeitado por qualidade, não por memória. Ele cabe (3,53 GiB) e roda em llama.cpp mainline. O problema está no achado 1 abaixo.

**As três descobertas decisivas:**

1. **A compressão agressiva ataca exatamente a capacidade sob teste.** Medição do próprio fabricante do Bonsai, em infraestrutura idêntica: de FP16 para 1 bit o custo é de 1,4 ponto em matemática e **21,6 pontos no τ²-Bench**. O dano se concentra em seguimento de instrução e tool calling multi-turno — que é o objeto deste artigo.
2. **Sucesso de tarefa sozinho é métrica cega.** O arXiv:2607.27275 mostra INT4 contra BF16 sem diferença de placar no τ²-bench (±7,5 pontos) enquanto **amplifica alucinação de nome de ferramenta em 2,5×** — o placar esconde o defeito porque o orçamento de retry o absorve. O experimento precisa registrar métricas decompostas: `valid_json@1`, `correct_function@1`, `correct_args@1`.
3. **Robustez a formato de prompt pesa mais que capacidade bruta.** No BFCL V4 a família Qwen oscila de 14 a 18 pontos só com variação de formatação; modelos especialistas em function calling oscilam 81,5. Como os dois braços deste experimento usam prompts diferentes por construção, um modelo frágil a formato afogaria o efeito do tratamento sob ruído.

**Quatro bloqueios no repo que impedem o experimento hoje** (levantados junto, entram nos tickets 03 e 09):

- O LiteLLM é chamado com prefixo `ollama/`, que roteia para `/api/generate` e não aceita `tools`; o correto para tool calling é `ollama_chat/`.
- `llm_completion()` descarta `tool_calls` da resposta.
- Não existe nenhuma instrumentação de latência.
- O braço multi-agente atual **não usa tool calling do LLM** — mapeia intenção para ferramenta por um dicionário fixo `INTENT_TOOLS`.
