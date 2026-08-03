# Mapa: Artigo — Multi-agente vs agente único no suporte bancário

Label: `wayfinder:map`

## Destination

Artigo científico de 5 a 7 páginas, em normas ABNT, escrito e entregue na disciplina de Metodologia Científica.

O artigo ancora-se em **dois trabalhos revisados por pares do mesmo tema** — a seleção de ferramentas por um LLM degrada conforme o tamanho e a redação do conjunto exposto — e os demonstra na prática sobre este repositório.
O experimento mantém modelo, ferramentas e tarefas fixos e varia apenas **o escopo de ferramentas visível por chamada**.

Desfecho primário: **acurácia de seleção de ferramenta**. Secundários: latência, tokens e sucesso de tarefa.

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
**Requisito da disciplina, declarado pelo usuário em 2026-08-03:** o trabalho exige **dois artigos científicos sobre o mesmo tema** e uma **demonstração prática** ligada a eles. O projeto ser protótipo, com código fraco e funcionalidade faltando, é aceito — a demonstração pode expor o que falta.

**Âncoras escolhidas (2026-08-03), ambas revisadas por pares:**

- PARAMANAYAKAM, Varatheepan et al. **Less is more**: optimizing function calling for LLM execution on edge devices. DATE 2025. arXiv:2411.15399. — reduzir o conjunto de ferramentas exposto melhora function calling; a falha é de **seleção**, não de janela de contexto. Ficha em `research/02-literatura.md` §3.3.
- BLANKENSTEIN, Thierry et al. **BiasBusters**: uncovering and mitigating tool selection bias in large language models. ICLR 2026. arXiv:2510.00307. — a seleção é enviesada pela similaridade semântica entre consulta e metadados da ferramenta; pequenas edições de descrição deslocam a escolha. Mitigação proposta: filtrar para um subconjunto relevante antes de escolher. Ficha em §3.5.

Os dois convergem no mesmo mecanismo: **o que o modelo vê por chamada determina a escolha**. É esse mecanismo que o experimento reproduz.

**Reenquadramento do eixo primário (2026-08-03).**
O eixo deixa de ser "multi-agente contra agente único" e passa a ser **escopo de ferramentas por chamada**.
A arquitetura multi-agente entra como **um mecanismo de partição de ferramentas** — precisamente a mitigação que os dois papers propõem (k-NN sobre a biblioteca em Less is more; filtragem para subconjunto relevante em BiasBusters).
Consequência prática: o "terceiro braço" do ticket 07 deixa de ser opcional e vira condição central do desenho.

- Pergunta de pesquisa (revista em 2026-08-03): o ganho atribuído à arquitetura multi-agente vem da arquitetura em si, ou do escopo reduzido de ferramentas que ela impõe a cada chamada do modelo?

**Fontes que continuam citáveis, agora como fundamentação e método, não como âncora:** MAST (Cemri et al., NeurIPS 2025) e Xu et al. para a discussão de multi-agente; τ-bench (Yao et al., ICLR 2025) para a definição de sucesso; OpenAI e Anthropic (§3.1, §3.2, §3.4) como convergência independente de fornecedor, sempre declarada como não revisada.

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
- [O que o harness de avaliação atual já faz](issues/03-inspecionar-harness-eval.md) — as quatro hipóteses sobre o código foram confirmadas com `arquivo:linha`. O runner não grava nada e não mede latência, tokens nem ferramentas; o LLM-as-judge **não existe** (`prompts/` é diretório morto); o dataset tem 15 casos com `pix_status` descoberto e dois casos impossíveis de passar. Nada do experimento existe hoje: o braço B, a instrumentação e o oráculo de sucesso precisam ser construídos do zero.
- [Como declarar o uso de IA como auxiliar de pesquisa](issues/13-declaracao-de-uso-de-ia.md) — nenhuma norma obriga um aluno de graduação, mas declarar compensa: ser flagrado sem declarar custa o dobro da penalidade de declarar, e detalhar não piora. Lugar decidido: subseção numerada ao fim do Método. A ABNT não prevê elemento para isso. Três modelos prontos em `research/06-declaracao-de-ia.md`.
- [Normas ABNT aplicáveis a este artigo](issues/11-normas-abnt.md) — NBR 6022:2018, **6023:2025**, **10520:2023**, 6024:2012, 6028:2021 e tabulação do IBGE, com modelos prontos em `research/05-normas-abnt.md`. Duas armadilhas: a citação agora é `(Silva, 2019)` e não `(SILVA, 2019)`, e a 6023:2025 não tem categoria para preprint nem para documentação de software — que é a maior parte das fontes deste artigo.
- [Marcadores linguísticos de texto gerado por IA, em português acadêmico](issues/10-marcadores-de-texto-de-ia.md) — tabelas de vocabulário, sintaxe, estrutura e tipografia em `research/04-marcadores-de-ia.md`, com seção de mitos. Contra-achados: excesso de conectivos, voz passiva e vocabulário pobre **não** são marcadores de IA. Não existe estudo de deriva lexical em português, então a tabela de vocabulário é inferência transposta do inglês. Simplificar o texto para parecer humano aumenta o falso positivo dos detectores de 5% para 57%.
- [O experimento tem um terceiro braço?](issues/07-terceiro-braco.md) — sim, e ele virou o eixo do artigo. O reenquadramento de 2026-08-03 promoveu a condição "escopo de ferramenta reduzido" de braço extra a variável principal, porque é a mitigação que as duas âncoras propõem. A pergunta "quantos braços" morre; sobra qual conjunto de ferramentas cada condição expõe, que migrou para [Desenho das condições de escopo de ferramenta](issues/15-condicoes-de-escopo-de-ferramenta.md). Compute extra e isolamento de contexto seguem confundidos entre C2 e C3 — limitação a declarar.
- [Literatura primária sobre arquiteturas de agentes LLM](issues/02-literatura-primaria.md) — 37 fontes levantadas (14 revisadas por pares) em `research/02-literatura.md`; τ-bench define o sucesso a adotar, MAST sustenta a discussão, "AI agents that matter" legitima custo como desfecho. Achado que vira contribuição: não há evidência revisada por pares de que supervisor vença agente único.

## Pré-requisito de código, fora deste mapa

Uma auditoria do repositório em 2026-07-31 produziu `plans/` na raiz, com oito planos de implementação e um índice.
A **fase 0** daqueles planos (001 a 005) é pré-requisito deste experimento: ela torna o projeto verificável, faz falha de infraestrutura parar de virar resposta válida, e instrumenta tokens, latência e chamadas de ferramenta — inclusive um registro por execução em JSONL, desenhado para a análise deste artigo.

Regra de coordenação: ao fim da fase 0, **congelar o commit** e rodar todas as execuções medidas sobre ele.
O artigo cita esse commit exato.
Corrigir código no meio das execuções invalida a série.

O plano `007-intents-que-nao-executam.md` altera `INTENT_TOOLS`, que é o objeto do ticket [O braço multi-agente precisa usar tool calling do LLM?](issues/09-o-que-esta-sendo-comparado.md).
As duas decisões precisam ser tomadas juntas.

## Not yet specified

- Desenho das tabelas e figuras do artigo (quantas cabem em 5-7 páginas, o que vira gráfico e o que vira tabela).
- Outline final das seções em ABNT e distribuição de páginas.
- Ameaças à validade a declarar (só fecha depois do protocolo e da escolha de modelo).
- Roteiro da apresentação em vídeo e o que precisa estar rodando ao vivo.
- Como as duas âncoras são apresentadas na fundamentação: lado a lado como um único mecanismo, ou uma como efeito de tamanho e outra como efeito de redação. Depende de o ticket 16 entrar ou não.
- Se o repositório vira artefato citável do artigo (commit congelado, instruções de reprodução) ou fica só como contexto.

## Out of scope

- Melhorar o chatbot além do estritamente necessário para o experimento.
- Guardrails, RAG e prompt caching como objetos de estudo (podem aparecer como contexto do sistema, nunca como variável manipulada).
- Publicar em evento ou periódico.
- **Comparação direta multi-agente contra agente único como desfecho primário** — fora de escopo desde 2026-08-03. MAST (NeurIPS 2025) e Xu et al. seguem citados na fundamentação e na discussão, mas o artigo não se propõe a decidir essa disputa: ela exige poder estatístico que 15 casos não dão, e nenhuma das duas fontes é âncora demonstrável na prática sobre este repo. O que sobra dela no artigo é a interpretação do contraste C2 contra C3.
- **Memória de conversa e avaliação multi-turno.** Não existe checkpointer no grafo (`agent.py:289`) e o estado carrega uma mensagem por requisição (`app.py:234`). Construir memória é esforço M que não serve ao eixo de escopo de ferramenta, que é medível em turno único. Declarar como limitação e como trabalho futuro.
