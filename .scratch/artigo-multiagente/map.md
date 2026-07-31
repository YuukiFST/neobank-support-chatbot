# Mapa: Artigo — Multi-agente vs agente único no suporte bancário

Label: `wayfinder:map`

## Destination

Artigo científico de 5 a 7 páginas, em normas ABNT, escrito e entregue na disciplina de Metodologia Científica.
O artigo reporta um experimento controlado sobre este repositório comparando arquitetura multi-agente (supervisor LangGraph + especialistas) contra agente único com tool calling, medindo sucesso de tarefa como desfecho primário e latência, tokens e custo como secundários.
O esforço termina com o PDF final entregue, incluindo os números do experimento rodado em hardware local.

## Notes

**Domínio:** engenharia de agentes de IA + metodologia científica experimental.

**Este mapa carrega execução.** Contrário ao padrão do wayfinder, o destino inclui fazer, não só decidir: implementar o arm B, rodar o experimento, analisar e escrever são tickets de tarefa dentro do mapa.

**Contexto fixo (decidido na sessão de charting, 2026-07-31):**

- Disciplina de Metodologia Científica, 5-7 páginas, ABNT desejado (professora não exige).
- Sem prazo fixo.
- Apresentação será em vídeo, gravada no PC de casa: RTX 3060 12 GB.
- Modelo roda local por causa da apresentação — provider local, não API paga.
- **Modelo escolhido: Qwen3.5-9B** (decidido pelo usuário em 2026-07-31, aceitando a recomendação do ticket 01). Quantização exata e runtime ficam para o ticket 05.
- Pergunta de pesquisa (rascunho, aceito na sessão de charting): a arquitetura multi-agente supervisor+especialistas entrega ganho de sucesso de tarefa suficiente para justificar seu custo em latência e tokens, comparada a um agente único com tool calling, num chatbot de suporte bancário?

**Restrição inegociável do usuário: plágio é crime.**
Toda referência é citada; nenhum trecho é copiado.
Texto gerado por LLM é reescrito na voz do autor antes de entrar no artigo — ver ticket 06.

**Fontes de referência que o usuário quer priorizar:** relatórios técnicos e papers dos laboratórios fortes da área — Anthropic, OpenAI, DeepSeek, Moonshot AI (Kimi), Z.AI (GLM), Alibaba (Qwen), MiniMax, Meta, NVIDIA — mais academia (MIT e afins).

**Artefatos de apoio em `.scratch/artigo-multiagente/research/`:** `03-storm-controversia.md` mapeia onde a área discorda e quais armadilhas metodológicas derrubam este tipo de experimento.
Não é fonte citável — foi gerado por simulação de perspectivas, não por recuperação de documentos.
Qualquer afirmação dele que entrar no artigo precisa ser rastreada até uma fonte primária.

**Skills a consultar por sessão:** `research` para tickets AFK de leitura; `grilling` + `domain-modeling` para tickets de decisão; `no-ai-slop` para toda redação do artigo; `prove` se o harness de avaliação precisar de garantias.

**Repositório sob estudo:** este próprio repo.
Fatos já levantados no charting: `eval/eval_set.jsonl` tem 15 casos; `eval/runner.py` é o harness; `prompts/` contém `router.md`, `account.md`, `card.md`, `kb.md`, `risk.md`, `escalation.md` e `judge.md` (LLM-as-judge já existe).

## Decisions so far

<!-- uma linha por ticket fechado -->

- [Qual modelo local roda o experimento numa RTX 3060 12 GB](issues/01-modelo-local-rtx3060.md) — Qwen3.5-9B GGUF Q6_K ou Q8_0 (cabe inteiro nos 12 GB), reserva Gemma 4 12B QAT, runtime `llama-server`. Ambos os candidatos originais caíram: NVFP4 exige Blackwell, e o Bonsai-27B perde 21,6 pontos em tool calling multi-turno pela compressão. Descobriu de quebra que o braço A não usa tool calling do LLM — ver [O braço multi-agente precisa usar tool calling do LLM?](issues/09-o-que-esta-sendo-comparado.md).
- [Como declarar o uso de IA como auxiliar de pesquisa](issues/13-declaracao-de-uso-de-ia.md) — nenhuma norma obriga um aluno de graduação, mas declarar compensa: ser flagrado sem declarar custa o dobro da penalidade de declarar, e detalhar não piora. Lugar decidido: subseção numerada ao fim do Método. A ABNT não prevê elemento para isso. Três modelos prontos em `research/06-declaracao-de-ia.md`.
- [Normas ABNT aplicáveis a este artigo](issues/11-normas-abnt.md) — NBR 6022:2018, **6023:2025**, **10520:2023**, 6024:2012, 6028:2021 e tabulação do IBGE, com modelos prontos em `research/05-normas-abnt.md`. Duas armadilhas: a citação agora é `(Silva, 2019)` e não `(SILVA, 2019)`, e a 6023:2025 não tem categoria para preprint nem para documentação de software — que é a maior parte das fontes deste artigo.
- [Marcadores linguísticos de texto gerado por IA, em português acadêmico](issues/10-marcadores-de-texto-de-ia.md) — tabelas de vocabulário, sintaxe, estrutura e tipografia em `research/04-marcadores-de-ia.md`, com seção de mitos. Contra-achados: excesso de conectivos, voz passiva e vocabulário pobre **não** são marcadores de IA. Não existe estudo de deriva lexical em português, então a tabela de vocabulário é inferência transposta do inglês. Simplificar o texto para parecer humano aumenta o falso positivo dos detectores de 5% para 57%.
- [Literatura primária sobre arquiteturas de agentes LLM](issues/02-literatura-primaria.md) — 37 fontes levantadas (14 revisadas por pares) em `research/02-literatura.md`; τ-bench define o sucesso a adotar, MAST sustenta a discussão, "AI agents that matter" legitima custo como desfecho. Achado que vira contribuição: não há evidência revisada por pares de que supervisor vença agente único.

## Not yet specified

- Desenho das tabelas e figuras do artigo (quantas cabem em 5-7 páginas, o que vira gráfico e o que vira tabela).
- Outline final das seções em ABNT e distribuição de páginas.
- Ameaças à validade a declarar (só fecha depois do protocolo e da escolha de modelo).
- Roteiro da apresentação em vídeo e o que precisa estar rodando ao vivo.

## Out of scope

- Melhorar o chatbot além do estritamente necessário para o experimento.
- Guardrails, RAG e prompt caching como objetos de estudo (podem aparecer como contexto do sistema, nunca como variável manipulada).
- Publicar em evento ou periódico.
