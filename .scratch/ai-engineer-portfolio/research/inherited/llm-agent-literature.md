# 02 — Literatura primária: arquiteturas de agentes LLM

Resolução do ticket `.scratch/artigo-multiagente/issues/02-literatura-primaria.md`.
Data da pesquisa: 31 jul. 2026. Todas as datas de acesso das fontes online são 31 jul. 2026.

## Como ler este documento

Cada fonte traz: referência em ABNT NBR 6023, URL efetivamente acessada, ano, **tipo**, as afirmações citáveis (parafraseadas, com localização no documento) e a seção do artigo onde ela cabe.

Três categorias de tipo, e a distinção importa para o peso da citação:

| Marca | Significado |
|---|---|
| **[REVISADO POR PARES]** | Publicado em anais de conferência ou periódico com revisão. Peso pleno. |
| **[PREPRINT arXiv]** | Depositado no arXiv sem veículo confirmado. Citável, mas o artigo deve dizer que é preprint. |
| **[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO]** | Blog de engenharia, documentação de fornecedor ou relatório institucional. Fonte primária legítima, mas **sem revisão por pares e frequentemente sem protocolo divulgado**. O artigo precisa declarar isso ao citar. |

**Regra antiplágio aplicada aqui:** toda afirmação abaixo está parafraseada. As poucas aspas são citações literais curtas (< 15 palavras) com localização exata. Nada foi copiado em bloco. Ao levar para o artigo, reescreva ainda na sua voz — este arquivo é nota de leitura, não texto pronto.

**Regra antifabricação aplicada aqui:** nenhuma referência foi escrita de memória. Cada título, autoria, ano, veículo, ID arXiv e DOI foi lido na página efetivamente acessada. Onde a verificação falhou, a fonte está na seção final "Não verificadas — não citar", e não conta para o mínimo.

## Contagem

| Tema | Fontes utilizáveis | Das quais revisadas por pares |
|---|---|---|
| 1. Padrão supervisor/orquestrador | 4 | **0** |
| 2. Multi-agente que piora ou não compensa | 4 | 1 |
| 3. Tool calling e número de tools | 10 | 4 |
| 4. Benchmarks de atendimento ao cliente | 7 | 3 |
| 5. LLM-as-judge | 7 | 4 |
| 6. Custo, latência e tokens como métrica | 5 | 2 |
| **Total** | **37 fontes distintas** | **14** |

Algumas fontes servem a mais de um tema e aparecem contadas no tema principal, com remissão cruzada. O mínimo do ticket (12 utilizáveis, ao menos 5 revisadas por pares) está folgadamente cumprido: **14 fontes revisadas por pares**, publicadas em NeurIPS (2), ICLR (2), ICML, ACL, EMNLP, NAACL (2), TACL, TMLR (2) e DATE.

**O zero na linha do tema 1 não é falha de busca, é o achado.** Não existe, no material verificado, evidência revisada por pares de que o padrão supervisor com especialistas supere um agente único. Toda afirmação quantitativa nesse sentido vem de blog de fornecedor com benchmark interno não divulgado. Isso precisa aparecer no artigo, e é justamente o que dá razão de ser ao experimento.

---

# Tema 1 — Padrão supervisor / orquestrador com sub-agentes especialistas

## 1.1 LangChain — documentação oficial do padrão multi-agente

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / documentação de fornecedor]**

LANGCHAIN. **Multi-agent**. Documentação LangChain OSS (Python). [S. l.: s. n.], [s. d.].
Disponível em: https://docs.langchain.com/oss/python/langchain/multi-agent. Acesso em: 31 jul. 2026.

Referência complementar da API: LANGCHAIN. **langgraph-supervisor**. Referência da API Python. Disponível em: https://reference.langchain.com/python/langgraph-supervisor. Acesso em: 31 jul. 2026.

- Define o padrão *subagents*: um agente principal coordena sub-agentes expostos como ferramentas, e todo o roteamento passa por ele, que decide quando e como invocar cada um. É a definição canônica da arquitetura implementada neste repo (seção "Subagents").
- Motivações declaradas para multi-agente (seção "Why multi-agent?"): gerenciamento de contexto, desenvolvimento distribuído por times independentes e paralelização. A condição de gatilho citada é o agente ter ferramentas demais e escolher mal entre elas.
- A própria documentação abre com a ressalva de que nem toda tarefa complexa precisa de multi-agente, e que um agente único com as ferramentas e o prompt certos costuma chegar a resultado semelhante. Vindo do fornecedor do framework, é uma frase forte para a discussão.
- Quantifica o custo de roteamento (seção "Performance comparison"): o padrão de sub-agentes consome **4 chamadas de modelo** para um pedido simples de um turno, contra **3** nos outros padrões. Também alerta que *handoffs* rodam em sequência e não aproveitam chamadas de ferramenta em paralelo.

**Cabe em:** metodologia (definição da arquitetura do braço A) e fundamentação teórica.

**Ressalva a declarar:** a página `docs.langchain.com` não usa a palavra "supervisor" — a API nomeada `create_supervisor` / `create_handoff_tool` vive na referência separada `langgraph_supervisor`. Documentação online é sem data e muda sem aviso; registre a data de acesso, como a NBR 6023 exige.

## 1.2 Anthropic — sistema multi-agente de pesquisa

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog de engenharia]**

HADFIELD, Jeremy et al. **How we built our multi-agent research system**. [S. l.]: Anthropic, 13 jun. 2025.
Disponível em: https://www.anthropic.com/engineering/multi-agent-research-system. Acesso em: 31 jul. 2026.

- Descreve o produto como arranjo orquestrador-trabalhador: um agente líder planeja e delega a sub-agentes que atuam em paralelo (seção "Architecture overview for research"). É a descrição, do lado da indústria, mais próxima do padrão supervisor deste artigo.
- Declara a condição de contorno do padrão (seção "Benefits of a multi-agent system"): domínios em que todos os agentes precisam do mesmo contexto, ou em que há muitas dependências entre agentes, são inadequados. Também afirma que programação tem menos subtarefas genuinamente paralelizáveis do que pesquisa.
- Torna explícito o argumento econômico, na mesma seção: multi-agente só se justifica quando o valor da tarefa absorve o gasto adicional de tokens.
- Relata patologias de coordenação observadas em versões iniciais (seção "Prompt engineering and evaluations for research agents"): sub-agentes criados em número absurdo para consultas triviais, trabalho duplicado e lacunas deixadas entre sub-agentes quando as instruções eram vagas.
- Registra que agentes são *stateful* e que erros se acumulam, e que a execução síncrona faz o sistema inteiro travar esperando um sub-agente (seção "Production reliability and engineering challenges").

**Números citáveis** (todos na seção "Benefits of a multi-agent system", salvo indicação):
- Multi-agente (líder Claude Opus 4 + sub-agentes Claude Sonnet 4) superou o agente único Claude Opus 4 em **90,2%**.
- Agentes consomem cerca de **4x** mais tokens que chat; sistemas multi-agente, cerca de **15x** mais que chat.
- No BrowseComp, o **uso de tokens sozinho explica 80% da variância** de desempenho.
- Heurísticas de calibração de esforço (seção "Prompt engineering and evaluations"): busca factual simples = 1 agente e 3-10 chamadas de ferramenta; comparação direta = 2-4 sub-agentes com 10-15 chamadas cada.

**Cabe em:** fundamentação teórica (definição do padrão) e discussão (o multiplicador de 15x em tokens e o argumento "o valor precisa justificar o custo" incidem diretamente sobre os desfechos secundários deste artigo).

**Ressalva obrigatória:** é um post de engenharia de fornecedor sobre o próprio produto. Os 90,2% vêm de avaliação interna da Anthropic, **sem protocolo divulgado, sem descrição do conjunto de tarefas e sem revisão por pares**. Não use esse número como se fosse resultado experimental publicado.

## 1.3 Anthropic — quando e como usar sistemas multi-agente

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog]**

PHILLIPS, Cara. **Building multi-agent systems: when and how to use them**. [S. l.]: Anthropic, 23 jan. 2026.
Disponível em: https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them. Acesso em: 31 jul. 2026.

- Três justificativas declaradas para dividir em múltiplos agentes: proteger o contexto da poluição por saída de subtarefa irrelevante, explorar em paralelo um espaço de busca maior e especializar (conjuntos de ferramentas, prompts de sistema, domínio). A especialização por número de ferramentas é acionada por volta de **20+ ferramentas** num agente só.
- Enuncia a contraposição diretamente: um agente único bem projetado rende mais do que a maioria dos desenvolvedores espera, e cada agente acrescentado é mais um ponto de falha.
- Relata casos em que melhorar o prompt de um agente único igualou o resultado de um sistema multi-agente complexo, e alerta contra decompor por tipo de problema em vez de por fronteira de contexto.
- Atribui a sobrecarga a três fontes nomeadas: contexto duplicado entre agentes, mensagens de coordenação e sumarização nos *handoffs*.

**Números citáveis:** implementações multi-agente costumam usar **3-10x mais tokens** que a versão de agente único para tarefas equivalentes (afirmado duas vezes no post). Citação literal curta, na discussão de sobrecarga: os sistemas *"spent more tokens coordinating than executing"*.

**Cabe em:** fundamentação teórica (critérios de decisão da arquitetura) e discussão.

**Ressalva:** atenção a não somar ou confundir os multiplicadores. O 15x de 1.2 é contra *chat*; o 3-10x daqui é contra *agente único*. São bases diferentes. Nenhum dos dois tem protocolo de medição publicado.

## 1.4 Kulkarni & Kulkarni — comparação de padrões de orquestração em documentos financeiros

**[PREPRINT arXiv]**

KULKARNI, Siddhant; KULKARNI, Yukta. **Benchmarking multi-agent LLM architectures for financial document processing**: a comparative study of orchestration patterns, cost-accuracy tradeoffs and production scaling strategies. [S. l.]: arXiv, 24 mar. 2026. Preprint. arXiv:2603.22651.
Disponível em: https://arxiv.org/abs/2603.22651. Acesso em: 31 jul. 2026.

- Compara quatro padrões de orquestração na mesma tarefa (seção III, System Architecture): pipeline sequencial, *fan-out* paralelo com merge, **supervisor-trabalhador hierárquico** e laço reflexivo autocorretivo. O hierárquico é o análogo direto do supervisor LangGraph deste artigo.
- Conclusão arquitetural (seção VII): o padrão supervisor-trabalhador fica na fronteira de Pareto custo-acurácia e é apresentado como o melhor compromisso de produção; o laço reflexivo só se justifica quando acurácia domina custo.
- Avalia em cinco eixos simultâneos (resumo): F1 por campo, acurácia por documento, latência ponta a ponta, custo por documento e eficiência de tokens. Esse enquadramento de cinco eixos é bom precedente para o desenho de desfechos deste artigo.

**Números citáveis** (Tabela III, seção V-A, coluna Claude 3.5 Sonnet): sequencial F1 0,903 / US$ 0,187 por doc / 38,7 s; paralelo F1 0,914 / US$ 0,221 / 21,3 s; **hierárquico F1 0,929 / US$ 0,261 / 46,2 s**; reflexivo F1 0,943 / US$ 0,430 / 74,1 s. A seção V-A afirma que o hierárquico atinge 98,5% do F1 do reflexivo a 60,7% do custo.

**Cabe em:** fundamentação teórica e metodologia (a tabela de custo e latência é modelo direto para a tabela deste artigo).

**RESSALVA CRÍTICA, não omita:** conforme a seção III, **não existe braço de agente único neste estudo** — a linha de base é o pipeline sequencial multi-agente. Portanto a fonte sustenta "o supervisor é o melhor padrão *entre* padrões multi-agente", e **não** "multi-agente vence agente único". Além disso, há divergência entre os números do resumo (hierárquico F1 0,921 a 1,4x do custo) e os da Tabela III; cite sempre com a localização exata que você usou. Preprint recente, dois autores, sem veículo.

---

# Tema 2 — Evidência de que multi-agente piora ou não compensa

Este é o tema mais bem sustentado do levantamento, e o resultado agregado é assimétrico: **a única afirmação quantitativa de que um supervisor vence um agente único vem de blog de fornecedor com benchmark interno não divulgado (1.2); toda medição revisada por pares ou independente encontrada aponta para paridade ou para o lado contrário.** Essa assimetria é, ela própria, um achado honesto e deve estar na discussão.

## 2.1 Cemri et al. — por que sistemas multi-agente LLM falham (MAST)

**[REVISADO POR PARES — NeurIPS 2025]** — *fonte mais forte do levantamento para este tema*

CEMRI, Mert et al. Why do multi-agent LLM systems fail? In: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS 38 (NeurIPS 2025), Datasets and Benchmarks Track. **Anais** [...]. [S. l.: s. n.], 2025. arXiv:2503.13657. DOI 10.48550/arXiv.2503.13657.
Disponível em: https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html. Acesso em: 31 jul. 2026.

- Afirmação de abertura (resumo e seção 1): o entusiasmo com sistemas multi-agente LLM não é acompanhado por ganho em benchmark, e os ganhos costumam ser mínimos frente a *frameworks* de agente único e a linhas de base simples como *best-of-N*.
- Constrói o MAST, taxonomia empírica de **14 modos de falha em 3 categorias**: problemas de desenho do sistema, desalinhamento entre agentes e verificação da tarefa (resumo; seção 4).
- Taxonomia derivada da análise de 150 traços por anotadores especialistas, com concordância entre anotadores **kappa = 0,88**; conjunto MAST-Data liberado com mais de **1.600 traços anotados** em **7 frameworks** (resumo).
- A seção 5.3 relata que correções táticas dirigidas melhoraram os resultados sem fechar a lacuna: as taxas de conclusão permaneceram baixas, e os autores concluem que são necessárias mudanças estruturais, não remendos de prompt.

**Números citáveis:** taxas de falha de **41% a 86,7%** em 7 frameworks multi-agente de código aberto do estado da arte (seção 1, detalhamento na Figura 5, Apêndice B). Distribuição das falhas: desenho do sistema ~**44,0%**, desalinhamento entre agentes ~**32,4%**, verificação de tarefa ~**23,6%** (Figura 1 e seção 4). Melhor ganho de intervenção tática observado: **+15,6%** no ChatDev (seção 5.3).

**Cabe em:** fundamentação teórica (as 14 categorias dão vocabulário nomeado para classificar os erros que o supervisor deste artigo produzir) e discussão (é a citação revisada por pares mais forte para "multi-agente frequentemente não compensa").

**Nota de verificação:** a condição de revisão por pares foi estabelecida na página dos anais do NeurIPS, não no arXiv — o campo *Comments* do arXiv não menciona veículo. Use a redação da v3/NeurIPS: a categoria é "system design issues" (a v1 dizia "specification issues").

## 2.2 Xu et al. — repensando o valor do fluxo multi-agente

**[PREPRINT arXiv]**

XU, Jiawei et al. **Rethinking the value of multi-agent workflow**: a strong single agent baseline. [S. l.]: arXiv, 18 jan. 2026. Preprint. arXiv:2601.12307. DOI 10.48550/arXiv.2601.12307.
Disponível em: https://arxiv.org/abs/2601.12307. Acesso em: 31 jul. 2026.

- Pergunta central (resumo): como a maioria dos *frameworks* multi-agente é homogênea — mesmo LLM base, diferindo só em prompt, ferramentas e posição no fluxo — um agente único conseguiria simular o fluxo inteiro via conversa multi-turno? É essencialmente a hipótese nula deste artigo.
- Resposta (resumo e Tabela 1): em sete benchmarks cobrindo código, matemática, QA, raciocínio de domínio e planejamento/uso de ferramentas do mundo real, o agente único iguala o fluxo multi-agente homogêneo, e chega a igualar um fluxo heterogêneo otimizado automaticamente.
- Argumento de eficiência: a implementação de agente único aproveita reuso de cache KV, que a execução multi-agente entre LLMs distintos não consegue explorar.
- Limitação declarada pelos próprios autores (resumo): a execução em LLM único não captura fluxos genuinamente heterogêneos, justamente porque o cache KV não é compartilhado entre modelos diferentes. Cite isso para não fazer discussão de um lado só.

**Números citáveis:** Tabela 1 (único vs multi, mesmo framework): HumanEval pass@1 91,1 vs 90,1; MBPP 78,8 vs 78,8; GSM8K 92,9 vs 93,6; MATH 53,8 vs 55,6; HotpotQA F1 68,4 vs 72,1; DROP F1 81,1 vs 83,1 — padrão de paridade, com vitórias nos dois sentidos. Tabela 2 (custo por tarefa): GSM8K US$ 0,697 único vs US$ 1,134 multi (~39% mais barato); MBPP US$ 0,283 vs US$ 0,393 (~28%); MATH US$ 2,039 vs US$ 2,343 (~13%). Tabela 4 (Qwen-3 8B, cache KV ativo): latência 53,53 s único vs 54,98 s multi.

**Cabe em:** discussão (principal contrapeso quantitativo) e metodologia (o relato de custo por tarefa e latência é modelo diretamente imitável para os desfechos secundários).

**Ressalva:** preprint de janeiro de 2026, sem veículo, sem revisão. Os fluxos avaliados não têm forma de supervisor; a analogia com este artigo é boa mas não é exata.

## 2.3 Yan — argumento contra sistemas multi-agente

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / ensaio de blog]**

YAN, Walden. **Don't build multi-agents**. [S. l.]: Cognition AI, 12 jun. 2025.
Disponível em: https://cognition.com/blog/dont-build-multi-agents. Acesso em: 31 jul. 2026.

- Dois princípios declarados (seção "Principles of Context Engineering"): compartilhar o traço completo do agente em vez de mensagens isoladas, e tratar toda ação como portadora de uma decisão implícita, porque decisões conflitantes produzem resultado ruim.
- Mecanismo de falha argumentado para sub-agentes paralelos: dois sub-agentes interpretam uma subtarefa subespecificada de formas diferentes, produzem artefatos incompatíveis, e o agente que faz o *merge* não consegue reconciliar. Passar o texto original da tarefa a cada sub-agente é argumentado como insuficiente, porque sessões reais carregam contexto multi-turno e histórico de chamadas de ferramenta que moldam a interpretação.
- Argumenta que humanos resolvem esse conflito conversando, e que agentes LLM atuais não conduzem discurso cruzado proativo de forma confiável.

**Números citáveis:** nenhum. É ensaio argumentativo sem medição. Use pelo mecanismo causal, nunca como evidência empírica.

**Cabe em:** discussão. É a articulação mais limpa do *porquê* um supervisor com especialistas pode perder para um agente único — exatamente a história causal necessária se o experimento não mostrar ganho.

**Ressalva obrigatória:** artigo de opinião de empresa concorrente, sem experimento e sem dados.

## 2.4 Zhang et al. — parar de supervalorizar o debate multi-agente

**[PREPRINT arXiv]**

ZHANG, Hangfan et al. **Stop overvaluing multi-agent debate**: we must rethink evaluation and embrace model heterogeneity. [S. l.]: arXiv, 12 fev. 2025 (v3: 21 jun. 2025). Preprint. arXiv:2502.08788. DOI 10.48550/arXiv.2502.08788.
Disponível em: https://arxiv.org/abs/2502.08788. Acesso em: 31 jul. 2026.

- Avaliação sistemática de 5 métodos representativos de debate multi-agente em 9 benchmarks com 4 modelos fundacionais (resumo).
- Achado principal (resumo): o debate multi-agente frequentemente não supera linhas de base simples de agente único (Chain-of-Thought, Self-Consistency), mesmo consumindo substancialmente mais computação em inferência. É a comparação normalizada por computação de que este artigo precisa, porque é a mesma troca que o experimento mede.
- Diagnostica a prática de avaliação da área como o problema: cobertura estreita de benchmarks, linhas de base fracas e montagens experimentais inconsistentes (resumo). Serve para justificar por que este estudo usa um agente único *forte*, com tool calling, e não um espantalho.
- Heterogeneidade de modelos é apontada como a única intervenção que ajuda de forma consistente. Ressalva relevante para o desenho deste artigo: supervisor e especialistas aqui compartilham o mesmo modelo base, isto é, o caso homogêneo que o paper considera o mais fraco.

**Números citáveis:** apenas 5 métodos / 9 benchmarks / 4 modelos, do resumo. **Nenhuma estatística do corpo do texto pôde ser verificada** (as renderizações HTML e o ar5iv devolveram só resumo e referências). Não cite números internos deste paper.

**Cabe em:** discussão, e metodologia como justificativa da linha de base forte.

**Nota:** o título da v1 era outro ("If Multi-Agent Debate is the Answer, What is the Question?") e o ar5iv ainda serve o título antigo. Cite o título atual da v3, como acima.

## 2.5 Anthropic (1.3) e LangChain (1.1), reaproveitadas

Ambas contêm a afirmação, vinda do próprio fornecedor, de que um agente único bem construído costuma empatar com o sistema multi-agente. Ver 1.1 e 1.3. Para a discussão, o fato de a admissão vir de quem vende a solução multi-agente aumenta o valor retórico da citação.

---

# Tema 3 — Tool calling: confiabilidade e efeito do número de ferramentas

Resumo honesto deste tema, para orientar a redação: **as afirmações mais quantitativas e mais explícitas sobre "mais ferramentas degradam a seleção" vêm de documentação de fornecedor, não de revisão por pares.** A literatura revisada sustenta bem o *mecanismo*, mas não publica a curva dose-resposta. Enquadre a lacuna como motivação do experimento.

## 3.1 Anthropic — ferramenta de busca de ferramentas (limiar explícito)

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / documentação de fornecedor]**

ANTHROPIC. **Tool search tool**. Claude Platform Docs, seção Tool use. [S. l.: s. n.], versões de recurso datadas `20251119`.
Disponível em: https://platform.claude.com/docs/en/docs/agents-and-tools/tool-use/tool-search-tool. Acesso em: 31 jul. 2026.

- Afirma diretamente que a capacidade do modelo de escolher a ferramenta certa se deteriora quando o conjunto disponível passa de uma faixa entre 30 e 50 ferramentas. Localização: introdução, marcador "Tool selection accuracy". Citação literal curta: *"Claude's ability to pick the right tool degrades once you exceed 30–50 available tools"*.
- Nomeia dois custos distintos de carregar todas as definições de antemão: inchaço de contexto e queda da acurácia de seleção (mesma lista).
- Limiar operacional para abandonar o tool calling plano (seção "Limits and best practices" → "When to use tool search"): 10 ou mais ferramentas, ou definições acima de 10 mil tokens, ou agregação de vários servidores MCP. Abaixo de 10 ferramentas, recomenda o tool calling plano.

**Números citáveis:** limiar de degradação **30-50 ferramentas**; uma montagem MCP de cinco servidores custa **~55 mil tokens** só em definições antes de qualquer trabalho, e a busca de ferramentas corta isso em **mais de 85%**, carregando **3-5 ferramentas** por requisição.

**Cabe em:** fundamentação teórica (fundamenta a hipótese de degradação por número de ferramentas) e metodologia (dá um corte defensável para quantas ferramentas o braço de agente único carrega e quantas cada especialista carrega).

**Ressalva obrigatória:** é documentação de fornecedor. **Não há experimento publicado por trás do número 30-50.** Cite como recomendação de prática do fabricante, nunca como resultado empírico.

## 3.2 Anthropic — uso avançado de ferramentas (magnitude do efeito)

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog de engenharia]**

ANTHROPIC. **Introducing advanced tool use on the Claude Developer Platform**. [S. l.]: Anthropic, 24 nov. 2025.
Disponível em: https://www.anthropic.com/engineering/advanced-tool-use. Acesso em: 31 jul. 2026.

- Relata avaliações internas em que habilitar descoberta de ferramentas sob demanda, em vez de carregar uma biblioteca grande no contexto, elevou substancialmente a acurácia da tarefa — o mesmo modelo, com as mesmas ferramentas, indo melhor quando vê menos por vez.
- Nomeia os dois modos de falha dominantes em uso de ferramentas: seleção errada e parâmetros errados, e liga explicitamente a seleção errada a nomes confundíveis (exemplo dado: `notification-send-user` vs `notification-send-channel`).
- Relata que chamada programática de ferramentas (manter resultados intermediários fora do contexto) reduz tokens e melhora acurácia ao mesmo tempo.

**Números citáveis** (seção "Tool Search Tool", salvo indicação): acurácia em avaliações MCP internas com bibliotecas grandes de ferramentas — **Opus 4: 49% → 74%**; **Opus 4.5: 79,5% → 88,1%**. Contexto: **~77 mil → ~8,7 mil tokens** antes de qualquer trabalho. Custo por servidor: GitHub 35 ferramentas ~26 mil tokens; Slack 11 ferramentas ~21 mil; total **58 ferramentas ≈ 55 mil tokens**. Seção "Programmatic Tool Calling": média **43.588 → 27.297 tokens (−37%)**.

**Cabe em:** fundamentação teórica (magnitude do efeito) e discussão (base de comparação para os deltas medidos neste artigo).

**Ressalva obrigatória:** o post atribui 49%→74% e 79,5%→88,1% a "teste interno em avaliações MCP com bibliotecas grandes de ferramentas". **Não nomeia o benchmark, não informa quantas ferramentas havia e não afirma literalmente que a linha de base era "todas as ferramentas carregadas de antemão"** — essa é a leitura natural, mas é inferência. Cite como avaliação interna de fornecedor.

## 3.3 Paramanayakam et al. — menos é mais (melhor âncora acadêmica do tema)

**[REVISADO POR PARES — DATE 2025]**

PARAMANAYAKAM, Varatheepan; KARATZAS, Andreas; ANAGNOSTOPOULOS, Iraklis; STAMOULIS, Dimitrios. Less is more: optimizing function calling for LLM execution on edge devices. In: DESIGN, AUTOMATION AND TEST IN EUROPE CONFERENCE (DATE), 2025. **Anais** [...]. [S. l.: s. n.], 2025. arXiv:2411.15399.
Disponível em: https://arxiv.org/abs/2411.15399. Acesso em: 31 jul. 2026.

- Afirmação central: reduzir o número de ferramentas expostas ao modelo melhora mensuravelmente o desempenho de function calling (título e resumo).
- A falha documentada **não é limite de janela de contexto, e sim falha de seleção**: um modelo cuja janela comporta todas as definições ainda assim escolhe errado. É exatamente a distinção de que este artigo precisa, porque exclui "o prompt não coube" como explicação alternativa.
- O método proposto é recuperação de ferramentas sem treino (k-NN sobre a biblioteca) — arquiteturalmente o mesmo movimento que o braço multi-agente faz ao particionar ferramentas entre especialistas.
- Reduzir ferramentas melhora latência e energia junto com acurácia, o que sustenta os desfechos secundários.

**Números citáveis:** bibliotecas de **51 funções** (BFCL) e **46 funções** (GeoEngine); profundidade de recuperação k = 3 e k = 5. Taxas de sucesso após a redução: Hermes2-Pro-8b ~71%; Qwen2-7b 68%; Llama3.1-8b 44,2%. Redução de tempo de execução de até **80%**. Observação motivadora, seção I: o Llama3.1-8b-q4_K_M tem janela de 16K que comporta todas as ferramentas e ainda assim falha, atribuído a *"the large number of available options confusing the LLM"*.

**Cabe em:** fundamentação teórica (âncora revisada por pares mais forte da hipótese) e discussão.

**Ressalva:** o enquadramento é execução em borda com modelos pequenos e quantizados. Cite pela **direção e pelo mecanismo, não pela magnitude** — os valores absolutos não transferem para um chatbot bancário. Observação de conveniência para este artigo: como o modelo aqui roda local na RTX 3060, o regime é mais próximo do desse paper do que seria com um modelo de fronteira via API.

## 3.4 OpenAI — guia de function calling (segundo limiar independente)

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / documentação de fornecedor]**

OPENAI. **Function calling**. Guia da API. [S. l.: s. n.], [s. d.].
Disponível em: https://developers.openai.com/api/docs/guides/function-calling. Acesso em: 31 jul. 2026.

- Dá um teto numérico explícito para quantas funções devem estar visíveis por vez, enquadrado como questão de acurácia e não de tokens. Seção "Best practices for defining functions", citação literal curta: manter *"fewer than 20 functions available at the start of a turn"*.
- Registra que as definições de função entram na mensagem de sistema, contam contra o limite de contexto e são cobradas como tokens de entrada (seção "Token Usage") — é o mecanismo pelo qual número de ferramentas vira custo, que é o desfecho secundário deste artigo.
- Recomenda avaliar com números diferentes de funções, isto é, o próprio fornecedor trata a contagem de ferramentas como variável experimental.

**Cabe em:** fundamentação teórica e metodologia. O valor aqui é a **convergência independente**: OpenAI recomenda < 20 e Anthropic aponta degradação em 30-50, o que mostra que a recomendação não é idiossincrasia de um laboratório.

**Ressalva:** a própria OpenAI qualifica o < 20 como sugestão branda. Reproduza essa qualificação. Nenhum experimento público a sustenta.

## 3.5 Blankenstein et al. — viés de seleção de ferramentas (BiasBusters)

**[REVISADO POR PARES — ICLR 2026]**

BLANKENSTEIN, Thierry et al. BiasBusters: uncovering and mitigating tool selection bias in large language models. In: INTERNATIONAL CONFERENCE ON LEARNING REPRESENTATIONS (ICLR), 2026. **Anais** [...]. [S. l.: s. n.], 2026. arXiv:2510.00307.
Disponível em: https://arxiv.org/abs/2510.00307. Acesso em: 31 jul. 2026.

- Quando várias ferramentas resolvem a mesma tarefa, a escolha do modelo é sistematicamente enviesada e não neutra — avaliado em sete LLMs sobre um benchmark de categorias com ferramentas funcionalmente equivalentes.
- A similaridade semântica entre a consulta e os metadados da ferramenta é o fator dominante da seleção, ou seja, a seleção se comporta como recuperação sobre descrições, não como raciocínio deliberado sobre capacidade.
- Pequenas edições nas descrições de ferramentas deslocam significativamente a escolha do modelo.
- A mitigação proposta é filtrar o conjunto de ferramentas para um subconjunto relevante antes de escolher — suporte revisado por pares ao princípio que embasa o braço multi-agente deste artigo.

**Cabe em:** fundamentação teórica e **metodologia — esta é uma ameaça direta à validade interna deste experimento**: as descrições e nomes das ferramentas precisam ser idênticos nos dois braços, senão a qualidade da redação das descrições vira variável confundidora.

**Ressalva:** afirmações em nível de resumo apenas; o texto completo não foi lido, então as localizações internas não estão fixadas.

## 3.6 Patil et al. — Berkeley Function-Calling Leaderboard (BFCL)

**[REVISADO POR PARES — ICML 2025]**

PATIL, Shishir G. et al. The Berkeley Function Calling Leaderboard (BFCL): from tool use to agentic evaluation of large language models. In: INTERNATIONAL CONFERENCE ON MACHINE LEARNING, 42., 2025. **Proceedings of Machine Learning Research**, v. 267, p. 48371-48392, 2025.
Disponível em: https://proceedings.mlr.press/v267/patil25a.html. Acesso em: 31 jul. 2026.
Página oficial do leaderboard: https://gorilla.cs.berkeley.edu/leaderboard.html. Acesso em: 31 jul. 2026.

- É o benchmark de referência para function calling e o instrumento padrão para medir se o modelo emite a chamada certa — use para definir "sucesso de tarefa" com credibilidade na metodologia.
- A avaliação é por casamento de árvore sintática abstrata (AST) mais verificações executáveis, e os autores afirmam que o método AST escala para milhares de funções — desenho de avaliação defensável e adaptável.
- A taxonomia do próprio benchmark separa o caso de uma função candidata do caso de várias ("multiple function"), isto é, trata o **número de funções candidatas como eixo de dificuldade**.
- Relata que os modelos lidam bem com interações isoladas, mas que memória, decisão dinâmica e raciocínio de horizonte longo seguem em aberto — apoia enquadrar a orquestração multi-agente como resposta a uma limitação conhecida.

**Números citáveis** (do blog oficial de Berkeley, não do paper): 2.000 pares pergunta-função-resposta na era v1/v2; a categoria "multiple function" invoca uma chamada entre **2 a 4** documentações JSON de função. Histórico: v1 introduziu avaliação AST, v2 acrescentou funções corporativas, v3 multi-turno, v4 avaliação agêntica.

**Cabe em:** metodologia (métrica de sucesso e desenho de avaliação) e fundamentação teórica.

**RESSALVA DE HONESTIDADE, obrigatória:** a categoria "multiple function" do BFCL chega no máximo a **2-4 funções candidatas**. Portanto **o BFCL não demonstra degradação com 20, 50 ou 100 ferramentas**. Se o artigo insinuar que demonstra, é sobreafirmação. Além disso, o texto completo do paper não pôde ser lido (PDF do PMLR e do OpenReview inacessíveis); os números acima vêm do blog oficial de Berkeley e devem ser citados a ele.

## 3.7 Liu et al. — perdido no meio (apenas analogia)

**[REVISADO POR PARES — TACL 2024]**

LIU, Nelson F. et al. Lost in the middle: how language models use long contexts. **Transactions of the Association for Computational Linguistics**, [S. l.], v. 12, p. 157-173, 2024. DOI 10.1162/tacl_a_00638.
Disponível em: https://aclanthology.org/2024.tacl-1.9/. Acesso em: 31 jul. 2026.

- O desempenho é maior quando a informação relevante está no início ou no fim do contexto e cai marcadamente quando está no meio — estabelecido em QA multi-documento e recuperação chave-valor.
- O efeito persiste em modelos construídos explicitamente para contexto longo, isto é, não se resolve com janela maior. É a ponte honesta para o argumento deste artigo: uma janela que comporta 60 definições de ferramenta não garante que o modelo atenda à definição de que precisa.

**Cabe em:** fundamentação teórica, **como mecanismo de apoio apenas**.

**RESSALVA obrigatória:** o paper trata de *documentos recuperados*, não de definições de ferramenta. Use somente como analogia declarada ("um mecanismo análogo, documentado para recuperação de documentos"), nunca como evidência sobre ferramentas. O texto completo não foi lido nesta pesquisa; cite em nível de resumo, sem fixar seções.

## 3.8 Anthropic — execução de código com MCP (custo de contexto)

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog de engenharia]**

ANTHROPIC. **Code execution with MCP**: building more efficient agents. [S. l.]: Anthropic, 4 nov. 2025.
Disponível em: https://www.anthropic.com/engineering/code-execution-with-mcp. Acesso em: 31 jul. 2026.

- Clientes MCP padrão carregam toda definição de ferramenta no contexto de antemão, de modo que o custo de contexto cresce com o tamanho da superfície de ferramentas conectada e não com o que a tarefa precisa (seção "Tool definitions overload the context window").
- Resultados intermediários de ferramentas, e não só as definições, são uma segunda fonte de inflação de contexto.

**Números citáveis:** **150.000 → 2.000 tokens** (~98,7% de redução) ao migrar de chamadas diretas para execução de código (seção "Excessive token consumption from tools makes agents less efficient").

**Cabe em:** fundamentação teórica (mecanismo de custo de contexto) e discussão.

**Ressalva:** esta fonte trata de **custo de tokens, não de acurácia de seleção**. Não a use para argumentar degradação de acurácia — para isso, use 3.1 e 3.3.

## 3.9 Anthropic — escrevendo boas ferramentas para agentes

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog de engenharia]**

ANTHROPIC. **Writing effective tools for agents — with agents**. [S. l.]: Anthropic, 11 set. 2025.
Disponível em: https://www.anthropic.com/engineering/writing-tools-for-agents. Acesso em: 31 jul. 2026.

- Acrescentar ferramentas não é monotonicamente benéfico; recomenda um conjunto pequeno de ferramentas de alto impacto em vez de cobertura exaustiva da API (seção "Choosing the Right Tools for Agents"). Citação literal curta: *"Too many tools or overlapping tools can also distract agents from pursuing efficient strategies"*.
- Sobreposição e vagueza, e não só a contagem bruta, dirigem os erros de seleção — o que importa muito num chatbot bancário onde vários especialistas compartilham verbos (consultar saldo / consultar fatura / consultar limite).
- Nomear ferramentas com prefixo de serviço alterou mensuravelmente o desempenho de avaliação (seção "Namespacing Tools"), evidência de que decisões superficiais de nomenclatura movem o resultado de seleção.

**Cabe em:** fundamentação teórica e **metodologia** — junto com 3.5, é o que justifica manter nomes e descrições de ferramentas idênticos entre os dois braços. Se os especialistas receberem nomes melhores que as ferramentas do agente único, isso é um confundidor.

**Ressalva:** qualitativo; o efeito de nomenclatura é afirmado sem números publicados.

## 3.10 Yeon et al. — certificação quantitativa de seleção de ferramentas

**[PREPRINT arXiv]**

YEON, Jehyeok; CHAUDHARY, Isha; SINGH, Gagandeep. **Quantitative certification of agentic tool selection**. [S. l.]: arXiv, 5 out. 2025 (rev. 13 maio 2026). Preprint. arXiv:2510.03992.
Disponível em: https://arxiv.org/abs/2510.03992. Acesso em: 31 jul. 2026.

- Introduz o LLMCert-T, arcabouço de certificação estatística da correção de seleção de ferramentas, e argumenta que a seleção errada é problema de segurança (por exemplo, acesso indevido a dados) — enquadramento que transfere bem para o domínio **bancário**.
- Agentes que parecem fortes em conjuntos de ferramentas limpos e curados desabam quando o conjunto é ampliado com distratores realistas. É o mais próximo de um resultado controlado de "aumente as ferramentas, veja a acurácia cair" encontrado na literatura acadêmica.
- Duas das especificações tratam explicitamente da composição e da profundidade do conjunto candidato ("Distractor Selection" e "Top-N Saturation"), isto é, tratam o tamanho do conjunto como variável independente.
- Avaliado sobre conjuntos BFCL e OpenAPI, o que o conecta a 3.6.

**Números citáveis:** os limites superiores certificados de correção caem para cerca de **20%** sob as especificações de distratores e de saturação Top-N, muito abaixo dos limites inferiores dos mesmos agentes em conjuntos limpos.

**Cabe em:** fundamentação teórica e discussão (enquadramento de risco em finanças).

**Ressalva:** preprint, sem veículo, afirmações em nível de resumo, localizações não fixadas.

---

# Tema 4 — Benchmarks de agentes em atendimento ao cliente

**Correção de partida, importante:** o τ-bench **não é preprint**. Foi publicado no **ICLR 2025** (pôster). O PDF da v1 no arXiv ainda traz o rodapé "Preprint. Under review." e o campo de comentários do arXiv está vazio, razão pela qual é largamente citado errado como preprint. A condição de revisão por pares foi confirmada na página de anais do ICLR. **Cite como ICLR 2025.**

## 4.1 Yao et al. — τ-bench (âncora principal da definição de sucesso)

**[REVISADO POR PARES — ICLR 2025, pôster]** — *documente esta com a maior profundidade*

YAO, Shunyu; SHINN, Noah; RAZAVI, Pedram; NARASIMHAN, Karthik. τ-bench: a benchmark for tool-agent-user interaction in real-world domains. In: INTERNATIONAL CONFERENCE ON LEARNING REPRESENTATIONS (ICLR), 2025. **Anais** [...]. [S. l.: s. n.], 2025. arXiv:2406.12045. DOI 10.48550/arXiv.2406.12045.
Disponível em: https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html. Acesso em: 31 jul. 2026.
Versão arXiv (de onde vêm as seções e tabelas citadas): https://arxiv.org/abs/2406.12045. Repositório oficial: https://github.com/sierra-research/tau-bench.

### Definição exata de sucesso (§3, parágrafo "Reward", p. 4)

A recompensa de um episódio é **r = r_action × r_output ∈ {0,1}**, produto de dois componentes binários:

1. **r_action** — se o **estado final do banco de dados é idêntico ao banco de dados-verdade único**. Confirmado: **o texto da conversa não é julgado**. A intenção de projeto está explícita em §4.2 ("Faithful rule-based evaluation"): como só um desfecho de banco é possível dada a política do domínio e o desejo declarado do usuário, o julgamento humano subjetivo é substituído por comparação objetiva de estado.
2. **r_output** — se as mensagens do agente ao usuário contêm toda a informação exigida. Verificado por **casamento literal de substring** contra cadeias anotadas. Exemplo trabalhado em §3: para a tarefa da Figura 2d, as respostas do agente precisam conter `"54.04"` e `"41.64"` como substrings.

**Duas ressalvas do próprio paper, a reproduzir honestamente** (§3, mesmo parágrafo):
- r = 1 é **necessário mas não suficiente** para um episódio genuinamente bem-sucedido — o agente pode fazer a escrita correta sem pedir confirmação explícita ao usuário, violando a política, e ainda assim pontuar 1.
- As anotações de tarefa são construídas de modo que a instrução do usuário "garante um único desfecho possível sob a política do domínio" (§3, "Task instances"). Essa unicidade é o que valida a comparação de estado final; ela é **engenheirada, não gratuita**.

### pass^k — fórmula exata (§3, parágrafo "Pass^k metric", p. 4-5)

Definido como a chance de **todas as k tentativas i.i.d. da tarefa terem sucesso**, com média sobre as tarefas — deliberadamente contrastado com o pass@k (chance de **ao menos uma** das k ter sucesso, a métrica de geração de código de Chen et al. 2021). Se a tarefa é executada **n** vezes com **c** sucessos (r = 1), os estimadores não viesados dados são:

- pass^k = E_tarefa [ C(c,k) / C(n,k) ]
- pass@k = 1 − E_tarefa [ C(n−c,k) / C(n,k) ]

No τ-bench o prompt do usuário e as transições do banco são fixos; a única estocasticidade vem da amostragem do LM nas mensagens de usuário e de agente. Logo, **pass^k mede robustez à variação conversacional com semântica idêntica**. O paper também registra que **pass^1 = pass@1 = E[r] = E[c/n]** é a métrica de destaque padrão.

### Domínios (Tabela 1, §4.1, p. 5)

| | τ-retail | τ-airline |
|---|---|---|
| Bancos | 500 usuários, 50 produtos, 1.000 pedidos | 500 usuários, 300 voos, 2.000 reservas |
| Ferramentas | 7 de escrita, 8 de não escrita | 6 de escrita, 7 de não escrita |
| Tarefas | 115 | 50 |

### Números citáveis

- Tabela 2 (§5.1, p. 7) — pass^1 com function calling: gpt-4o **61,2 retail / 35,2 airline / 48,2 média** (melhor); gpt-4-turbo 57,7/32,4; claude-3-opus 44,2/34,7; gpt-3.5-turbo 20,0/10,8; meta-llama-3-70B 14,8/14,4 (pior).
- Figura 4 (§5.1, p. 7) — o pass^k em τ-retail cai acentuadamente com k; o texto afirma que o gpt-4o tem pass^1 acima de 60% mas **pass^8 abaixo de 25%**. (A Figura 4 é gráfico; os valores por k não estão impressos no texto — localização fixada na Fig. 4, valores não fixados.)
- Figura 3 (§5.1) — **function calling nativo supera ReAct e Act formatados em texto** nos modelos do estado da arte.
- Tabela 3 (§5.2, p. 8) — ablação de remoção de política: gpt-4o 61,2→56,8 em retail (−4,4), mas 33,2→10,8 em airline (−22,4). **Atenção: há discrepância no próprio paper** — a Tabela 2 informa 35,2 para gpt-4o em airline e a Tabela 3 informa 33,2. Sinalize se citar as duas.
- Taxonomia de falhas, Figura 5 (§5.2, p. 7): de 36 falhas do gpt-4o analisadas em τ-retail — informação errada 25,0%, argumento errado 19,4%, decisão errada 22,2%, resolução parcial 33,3%.
- **Protocolo experimental (§5, "Methods", p. 6): máximo de 30 ações do agente por tarefa; ao menos 3 tentativas por tarefa nos resultados principais; temperatura do agente 0,0 e do simulador de usuário 1,0; usuário simulado por gpt-4-0613.**
- **Relato de custo (§5.1, "Cost analysis", p. 7):** agente gpt-4o FC + simulação de usuário gpt-4 em τ-retail custa **US$ 0,38 (agente) / US$ 0,23 (usuário) por tarefa**; uma tentativa sobre o conjunto inteiro ≈ **US$ 200**. Prompt de entrada e saída respondem por **95,9% / 4,1%** do preço do agente, isto é, **o custo é dominado pelo prompt de sistema longo (política do domínio + definições de ferramentas)**. Nenhuma medição de latência é reportada.
- Placar do repositório oficial (README, modelos posteriores): claude-3-5-sonnet-20241022 em airline pass^1 0,460 → pass^2 0,326 → pass^3 0,263 → pass^4 0,225; em retail 0,692 → 0,576 → 0,509 → 0,462. O README avisa que as tarefas ali **não são atualizadas** e aponta para o τ³-bench.

**Cabe em:** fundamentação teórica e **metodologia** — é a âncora para definir "sucesso de tarefa" por comparação de estado final e para justificar tentativas repetidas com pass^k em vez de execução única.

**Nota de verificação:** o PDF completo foi baixado e as páginas 1-11 extraídas literalmente; todas as definições, tabelas e números de seção acima foram lidos ali. As páginas de anais e de pôster do ICLR confirmam autoria e veículo. **Todos os números de seção e tabela acima vêm da v1 do arXiv**; o resumo da versão camera-ready do ICLR tem redação levemente diferente, então a camera-ready pode renumerar figuras. Ao citar um número de tabela, explicite que é a versão arXiv.

## 4.2 Barres et al. — τ²-bench (controle duplo)

**[PREPRINT arXiv — rodapé do PDF: "Preprint. Under review."]**

BARRES, Victor; DONG, Honghua; RAY, Soham; SI, Xujie; NARASIMHAN, Karthik. **τ²-Bench**: evaluating conversational agents in a dual-control environment. [S. l.]: arXiv, 9 jun. 2025. Preprint. arXiv:2506.07982. DOI 10.48550/arXiv.2506.07982.
Disponível em: https://arxiv.org/abs/2506.07982. Acesso em: 31 jul. 2026.

- Benchmarks anteriores de agentes conversacionais, inclusive o τ-bench, são **de controle único**: só o agente age sobre o mundo, e o usuário apenas fornece informação. O τ²-bench passa a **controle duplo** — o usuário simulado tem ferramentas e banco próprios (§1, §3).
- Formalizado como **Dec-POMDP** com a tupla (S, {A_i}, {O_i}, T, R, U, M) sobre dois jogadores (§3.1).
- Novo domínio **Telecom** (suporte técnico / diagnóstico); retail e airline vêm do τ-bench (§3.2, Tabela 1).
- As tarefas são **geradas programaticamente** a partir de subtarefas atômicas definidas por funções de inicialização, solução e asserção, o que torna a correção demonstrável em vez de anotada à mão (§3.2, etapa 3).
- Cinco critérios possíveis de avaliação (§3.3, "Task evaluation"), cada tarefa escolhendo um subconjunto: (1) verificação de banco e (2) verificação de informação comunicada — idênticos ao r_action e r_output do τ-bench; (3) **asserções de estado**; (4) **asserções em linguagem natural** sobre o histórico da interação (por exemplo, "o agente diagnosticou a causa"); (5) **casamento de ações**. No domínio Telecom, só funções de asserção são usadas. Recompensa R : S → [0,1] (§3.1).

**Números citáveis:** Tabela 1 (§3.2): telecom com **6 ferramentas de escrita / 7 de leitura para o agente** e **15 / 15 para o usuário**; **114 tarefas amostradas de 2.285** geradas. Figura 3 (§4.2), pass^1 → pass^4 com 4 tentativas por tarefa, temperatura 0 e simulador gpt-4.1: gpt-4.1 retail 0,74→0,53, airline 0,56→0,40, telecom 0,34→0,19; claude-3.7-sonnet retail 0,79→0,60, telecom 0,49→0,25. Confiabilidade do simulador de usuário: telecom **16% de erro / 6% crítico**, contra **40% / 12%** no τ-bench retail (§1). **Relato de custo (§4.1):** agente gpt-4.1 + simulador gpt-4.1 = **US$ 0,086 (agente) / US$ 0,059 (usuário) por tarefa**; todos os domínios com 1 tentativa por tarefa ≈ **US$ 40**.

- **Ablação de maior valor metodológico para este artigo (§4.2, Fig. 4):** sair da condição **No-User** (o agente controla todas as ferramentas e recebe um chamado) para o controle duplo padrão custa **cerca de 20 pontos de pass^1**. Isso isola falha de comunicação/coordenação de falha de raciocínio puro — é um molde direto para isolar qual componente da arquitetura multi-agente causa a queda.

**Cabe em:** fundamentação teórica e discussão.

**Nota de verificação:** o fórum do OpenReview não pôde ser acessado (barreira antibot e API 403), então **nenhum veículo pode ser alegado**. A API do arXiv mostra apenas v1, com campos `comment` e `journal_ref` vazios. Classifique como preprint.

## 4.3 Shi et al. — τ-Knowledge / τ-Banking (o mais próximo deste artigo)

**[PREPRINT arXiv — cabeçalho: "Preprint. Work in progress."]** — *domínio bancário, e a única fonte que junta sucesso + tokens + latência + custo*

SHI, Quan; ZYTEK, Alexandra; RAZAVI, Pedram; NARASIMHAN, Karthik; BARRES, Victor. **τ-Knowledge**: evaluating conversational agents over unstructured knowledge. [S. l.]: arXiv, 4 mar. 2026. Preprint. arXiv:2603.04370.
Disponível em: https://arxiv.org/abs/2603.04370. Acesso em: 31 jul. 2026.

- Introduz o **τ-Banking**, domínio de suporte ao cliente em fintech — o análogo publicado mais próximo do chatbot de suporte bancário deste artigo. O agente navega ~700 documentos não estruturados enquanto executa atualizações de conta mediadas por ferramentas (resumo; §3).
- Introduz **ferramentas descobríveis**: ferramentas não expostas inicialmente ao agente, referenciadas só implicitamente na base de conhecimento, invocadas por `call_discoverable_tool(name, kwargs)` (§3, "Discoverable Tools").
- **Argumenta explicitamente que o progresso em agentes voltados a pessoas deve ser medido não só por sucesso final, mas também por eficiência da solução** — tempo, chamadas de ferramenta e retrabalho conversacional mínimos (§1, parágrafos finais). É justificativa citável e direta para os desfechos secundários deste artigo.
- Mantém o paradigma de estado final do τ-bench: cada tarefa especifica um estado-alvo de banco e a recompensa R : S → [0,1] depende de a sequência de recuperação, invocação e interação produzir o estado final correto (§3). A métrica de sucesso é **pass^k**, definida em §5 como a probabilidade de a tarefa ter sucesso em **todas** as k tentativas independentes, com **k ≤ 4**.
- A correção das tarefas foi auditada por **dois revisores independentes** não envolvidos na criação, que verificaram o estado final esperado, a minimalidade e completude dos documentos-ouro e simularam manualmente ao menos uma trajetória válida por tarefa (§4, etapa 5).

**Números citáveis:** Tabela 1 (§3) — τ-Banking com **698 documentos**, 194.562 tokens, 21 categorias, **51 ferramentas descobríveis**, **14 ferramentas permanentes**, **97 tarefas**, média de **18,6 documentos exigidos** e **9,52 chamadas de ferramenta exigidas por tarefa** (mín. 1, máx. 33). Resultados (§6, Tabela 2): melhor configuração GPT-5.2 (high) + busca em terminal = **25,52 pass^1**; Claude-4.5-Opus 24,74; melhor **pass^4 = 13,40**. No cenário **Gold** (documentos-verdade injetados, recuperação removida como gargalo) o melhor é 39,69 pass^1, caindo para 26,80 pass^4 — logo, recuperação não explica tudo.
**Relato de eficiência (§1 e §6, Fig. 3):** o GPT-5.2 (high) iguala o Claude-4.5-Opus em sucesso, mas usa **~1,7x mais tokens**, **~2,3x mais comandos** e leva **~9x mais tempo**. **A Figura 3 (direita) é uma fronteira de Pareto de duração média por tarefa (segundos) contra pass^1** — é o melhor precedente disponível para o relato conjunto de sucesso, latência e tokens deste artigo.

**Cabe em:** fundamentação teórica, **metodologia** e discussão. É a fonte que mais diretamente licencia o conjunto exato de desfechos deste artigo (sucesso primário; latência, tokens e custo secundários) num cenário **bancário**.

**Ressalva:** preprint de 2026, marcado pelos próprios autores como trabalho em andamento. Pareie sempre com uma âncora revisada por pares (4.1 ou 6.2).

## 4.4 Huang et al. — CRMArena

**[REVISADO POR PARES — NAACL 2025]**

HUANG, Kung-Hsiang et al. CRMArena: understanding the capacity of LLM agents to perform professional CRM tasks in realistic environments. In: CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS (NAACL-HLT), 2025, Albuquerque. **Anais** [...]. v. 1: Long Papers. [S. l.]: ACL, 2025. p. 3830-3850. DOI 10.18653/v1/2025.naacl-long.194.
Disponível em: https://aclanthology.org/2025.naacl-long.194/. Acesso em: 31 jul. 2026.

- Benchmark construído sobre uma **plataforma corporativa real** (Salesforce), e não sobre ambiente sintético de brinquedo, desenhado com especialistas de CRM (resumo).
- **Nove tarefas de atendimento ao cliente em três perfis**: agente de atendimento, analista e gerente (resumo).
- **16 objetos industriais comuns** (conta, pedido, artigo de base de conhecimento, caso), com alta interconexão, mais variáveis latentes para tornar a distribuição realista (resumo).

**Números citáveis:** agentes LLM do estado da arte têm sucesso em **menos de 58%** das tarefas com prompting ReAct e em **menos de 65%** mesmo com function calling (resumo).

**Cabe em:** fundamentação teórica — é evidência revisada por pares de que tarefas corporativas de atendimento seguem não resolvidas, **e de que a arquitetura do agente (ReAct vs function calling) muda o sucesso de forma mensurável**, o que é paralelo direto à comparação supervisor vs agente único deste artigo.

**Ressalva:** só a página de anais e o resumo foram lidos; **localização não fixada** para definições internas de métrica. Para essas, use 4.5.

## 4.5 Huang et al. — CRMArena-Pro

**[PREPRINT arXiv]**

HUANG, Kung-Hsiang et al. **CRMArena-Pro**: holistic assessment of LLM agents across diverse business scenarios and interactions. [S. l.]: arXiv, 24 maio 2025. Preprint. arXiv:2505.18878. DOI 10.48550/arXiv.2505.18878.
Disponível em: https://arxiv.org/abs/2505.18878. Acesso em: 31 jul. 2026.

- Expande o CRMArena para **19 tarefas validadas por especialistas** em quatro competências, em organizações B2B e B2C (§3).
- Acrescenta duas dimensões ausentes no CRMArena: **interação multi-turno** e **consciência de confidencialidade** (§3.6, §4).
- **Protocolo de avaliação (§4.1, "Evaluation Metrics"), útil como contraste ao τ-bench:** três mecanismos, escolhidos por tipo de tarefa — **casamento exato** para tarefas com resposta única identificável; **F1 sobre sobreposição de tokens** para tarefas textuais generativas; e, no cenário multi-turno, um **extrator de respostas baseado em LLM** (gpt-4o) para tirar os identificadores do diálogo livre antes do casamento. Confidencialidade é julgada por **juiz LLM**. **Nota para este artigo: isto é casamento de resposta, não comparação de estado final — protocolo mais fraco que o do τ-bench, e o contraste é citável.**
- No cenário multi-turno (§3.6), usuários simulados liberam a informação relevante **de forma incremental**, forçando o agente a fazer perguntas de esclarecimento.

**Números citáveis:** Tabela 2 — melhor modelo gemini-2.5-pro: **54,1% (B2B) / 58,3% (B2C) em turno único**, caindo para **35,1% / 30,0% em multi-turno**. Tabela 3 — consciência de confidencialidade de 0,0-0,4% com prompt padrão, subindo até 62,9% com prompt específico, **ao custo de degradar a conclusão da tarefa**. §4.4 traz a **Figura 5, custo (US$) por instância de consulta contra desempenho**. Não há dados de latência nem de contagem de tokens no texto principal.

**Cabe em:** metodologia e discussão — a degradação de turno único para multi-turno (~58% → ~35%) é a evidência externa mais limpa de que **o protocolo de medição muda o número mais do que o modelo muda**, o que reforça por que o protocolo deste artigo precisa estar declarado com precisão.

**Ressalva:** preprint. Campos `comment` e `journal_ref` vazios no arXiv, apenas v1, e não aparece na página de anais da ACL do primeiro autor (onde o CRMArena aparece).

## 4.6 Chen et al. — ABCD (o caso de contraste pré-LLM)

**[REVISADO POR PARES — NAACL 2021]**

CHEN, Derek; CHEN, Howard; YANG, Yi; LIN, Alexander; YU, Zhou. Action-based conversations dataset: a corpus for building more in-depth task-oriented dialogue systems. In: CONFERENCE OF THE NORTH AMERICAN CHAPTER OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS (NAACL-HLT), 2021. **Anais** [...]. [S. l.]: ACL, 2021. p. 3002-3017. DOI 10.18653/v1/2021.naacl-main.239.
Disponível em: https://aclanthology.org/2021.naacl-main.239/. Acesso em: 31 jul. 2026.

- Interações de suporte ao cliente exigem seguir **procedimentos de múltiplos passos derivados de políticas explícitas da empresa**, e não apenas preencher campos — o enquadramento de conformidade a política que o τ-bench depois herda (resumo, §1). O τ-bench cita o ABCD.
- **Contraste-chave de protocolo:** o ABCD avalia **predição por turno**, não estado final. *Action State Tracking* (§6.1) pede a próxima ação como tripla (botão, campo, valor), medida por acurácia geral. *Cascading Dialogue Success* (§6.2) exige decidir a cada turno entre agir, falar ou encerrar e prever **todos os passos restantes**, com **crédito parcial em cascata**; enunciados são medidos por recuperação, não por métricas de geração, porque BLEU é pouco confiável para paráfrases.
- **É exatamente o protocolo que o τ-bench substituiu**: acurácia por turno contra trajetórias anotadas versus comparação binária de estado final contra um banco-alvo. É a melhor justificativa disponível para este artigo escolher o segundo.

**Números citáveis:** **10.042 conversas**, média de **22,1 turnos por diálogo**, 177.407 turnos, média de 3,73 ações por diálogo, **55 intenções**, **30 domínios**, **231 campos únicos** (contra 7 domínios / 24 campos do MultiWOZ). Tabela 3 (AST): melhor RoBERTa com Ação 65,8% (linha de base em pipeline 32,3%). Tabela 4 (CDS): melhor RoBERTa-Large **31,9%** contra **82,7% humano**. A lacuna para o humano era de **50,8 pontos absolutos** (resumo).

**Cabe em:** fundamentação teórica (enquadramento histórico: atendimento como sequência de ações restringida por política, e os limites da avaliação por turno).

## 4.7 Mao et al. — BFCL V3, avaliação por estado

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / blog acadêmico]**

MAO, Huanzhi et al. **BFCL V3**: multi-turn and multi-step function calling. Berkeley Function Calling Leaderboard, blog. [S. l.]: UC Berkeley Gorilla, 19 set. 2024 (atualizado em 10 dez. 2024).
Disponível em: https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html. Acesso em: 31 jul. 2026.

- O BFCL V3 adota **avaliação baseada em estado**: compara o **estado do sistema de apoio (excluindo atributos privados) após a execução de todas as chamadas ao fim de cada turno**. Isso corrobora de forma independente a decisão de projeto do τ-bench — dois grupos separados convergiram para a comparação de estado final em agentes multi-turno com ferramentas.
- Mantém **também** uma avaliação baseada em resposta para requisições somente de leitura, comparando o caminho de execução contra caminhos-verdade mínimos viáveis. O paralelo estrutural com o r_action (estado) × r_output (informação) do τ-bench é evidente.
- Justificativa explícita contra casamento exato estrito, citável na metodologia: modelos tomam **trajetórias diferentes e igualmente válidas**, executam **ações legítimas de recuperação** após erros e dão passos extras desnecessários mas válidos. A correção adotada é casamento por **subconjunto**: o modelo passa se seus resultados contiverem as chamadas-verdade como subconjunto.
- Escala: **1.000 entradas multi-turno** = 200 base + 800 aumentadas (parâmetros faltantes 200, funções faltantes 200, contexto longo 200, composta 200). O post em si não traz números de acurácia.

**Cabe em:** metodologia — corroboração secundária de que comparação de estado final é o oráculo padrão da área para agentes multi-turno, e argumento pronto para explicar por que casamento exato de trajetória é o oráculo errado.

**Ressalva:** blog de laboratório, sem revisão por pares e sem DOI. Ver também 3.6, que é a versão revisada por pares do BFCL, publicada no ICML 2025.

## 4.8 Recomendações práticas para o protocolo deste artigo

Extraídas das fontes acima, todas rastreáveis:

1. **Defina sucesso exatamente como o τ-bench e diga que é isso.** r = r_action × r_output, binário: comparação de estado final do banco mais verificação da informação exigida transmitida ao usuário. Cite ICLR 2025, §3. **Depois enuncie você mesmo a ressalva do τ-bench** (r = 1 é necessário mas não suficiente — o agente pode chegar ao estado certo por rota que viola a política). Bancas premiam essa honestidade.
2. **pass^k é a métrica de confiabilidade certa e é barata de justificar.** Fórmula pass^k = E[C(c,k)/C(n,k)] com n tentativas e c sucessos. Numa comparação multi-agente vs agente único, pass^k é justamente onde as arquiteturas divergem: τ-bench, τ²-bench e τ-Knowledge mostram rankings de pass^1 que **não sobrevivem** ao pass^4. Orce ao menos 3 a 4 tentativas por caso (τ-bench usou ≥3; τ²-bench e τ-Knowledge usaram 4).
3. **Copie a convenção de temperatura:** agente em 0, simulador de usuário em 1 (τ-bench §5); o τ²-bench usou 0 nos dois. Limite também o número de ações do agente (τ-bench: 30).
4. **Precedente para custo existe em abundância; para latência é escasso.** τ-bench §5.1 reporta US$/tarefa e a divisão 95,9%/4,1% entrada/saída. τ²-bench §4.1 reporta US$/tarefa. CRMArena-Pro Fig. 5 plota custo por consulta contra desempenho. **Só o τ-Knowledge (Fig. 3, direita) plota latência (duração em segundos) contra pass^1** — é a única citação que cobre sucesso, tokens, latência e custo juntos, e faz isso em domínio bancário. Como é preprint de 2026, pareie com âncora revisada por pares.
5. **Âncora bancária:** τ-Banking (4.3) — 97 tarefas, ~700 documentos, melhor modelo em 25,52 pass^1. É o ambiente publicado mais próximo de um chatbot de suporte bancário, e a definição de sucesso deste artigo pode ser apresentada como adaptação dele.

---

# Tema 5 — LLM-as-judge: validade, viés e concordância com humanos

Relevância direta para este repo: `prompts/judge.md` já define um juiz de 5 dimensões (helpfulness, accuracy, hallucination, language, security) em escala 1-5 com saída JSON, e `eval/runner.py` hoje decide `passed` por regra programática (intent exato + escalonamento + substring), sem chamar o juiz. As fontes abaixo dizem o que precisa ser feito para o juiz ser defensável no artigo.

## 5.1 Zheng et al. — julgando o LLM-as-a-judge (fonte canônica)

**[REVISADO POR PARES — NeurIPS 2023, Datasets and Benchmarks Track]**

ZHENG, Lianmin et al. Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. In: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS 36 (NeurIPS 2023), Datasets and Benchmarks Track. **Anais** [...]. [S. l.: s. n.], 2023. arXiv:2306.05685.
Disponível em: https://arxiv.org/abs/2306.05685. Acesso em: 31 jul. 2026.

- Um juiz LLM forte (GPT-4) reproduz preferências humanas — tanto de especialistas em ambiente controlado quanto de multidão — aproximadamente na mesma taxa em que dois humanos concordam entre si (resumo; detalhe na seção 4.2). É a justificativa canônica para usar juiz LLM como proxy de anotação humana.
- Nomeia e mede empiricamente três vieses do juiz, mais a limitação de raciocínio em matemática e lógica (seção 3.3, "Limitations of LLM-as-a-judge"): viés de posição, viés de verbosidade e viés de autoenaltecimento.
- Propõe mitigações na seção 3.4: trocar a posição das duas respostas e chamar o juiz duas vezes (declarando empate quando os veredictos divergem), julgamento com poucos exemplos, julgamento com cadeia de raciocínio e **avaliação guiada por referência**, em que se fornece uma resposta de referência ao juiz.

**Números citáveis, por nível de confiança:**
- ALTA: resumo — mais de **80%** de concordância entre o juiz GPT-4 e humanos, descrita como o mesmo nível da concordância humano-humano.
- ALTA: Tabela 5, seção 4.2 (MT-Bench, votos não empatados): GPT-4 pareado vs humano = **85%**; GPT-4 nota única vs humano = **85%**; humano vs humano = **81%**.
- ALTA: Tabela 2, seção 3.3 (consistência sob troca de posição): GPT-4 **65,0%**, GPT-3.5 46,2%, Claude-v1 23,8%.
- MÉDIA, **reconfira antes de imprimir**: Tabela 6 (Chatbot Arena, não empatados) ≈ **87%**; viés de autoenaltecimento — GPT-4 favorece as próprias saídas em ~10 pontos percentuais de taxa de vitória, Claude-v1 em ~25 pontos (seção 3.3, Fig. 2); avaliação guiada por referência reduzindo a taxa de erro do juiz em matemática de 70% para 15% (seção 3.4); poucos exemplos elevando a consistência do GPT-4 de 65,0% para 77,5%.
- **NÃO CITE** os percentuais do arranjo S1 (com empates incluídos) — vieram inconsistentes entre leituras (66% vs 70%).

**Cabe em:** fundamentação teórica (justificativa do juiz), metodologia (troca de posições, avaliação guiada por referência, relatar concordância humana) e discussão (limitações).

**Ressalva importante para este artigo:** todos esses números de concordância foram medidos sobre **respostas de chat abertas**, não sobre trajetórias de agente com uso de ferramentas. Ver 5.7.

## 5.2 Panickssery et al. — avaliadores LLM reconhecem e favorecem as próprias gerações

**[REVISADO POR PARES — NeurIPS 2024]**

PANICKSSERY, Arjun; BOWMAN, Samuel R.; FENG, Shi. LLM evaluators recognize and favor their own generations. In: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS 37 (NeurIPS 2024). **Anais** [...]. [S. l.: s. n.], 2024. arXiv:2404.13076.
Disponível em: https://proceedings.neurips.cc/paper_files/paper/2024/hash/7f1f0218e45f5414c79c0679633e47bc-Abstract-Conference.html. Acesso em: 31 jul. 2026.

- Define a autopreferência de forma operacional (resumo): o avaliador LLM pontua as próprias gerações mais alto que as de outros, enquanto anotadores humanos as julgam de qualidade equivalente. É a definição mais precisa disponível para justificar, na metodologia, não deixar o juiz avaliar o próprio sistema.
- LLMs, incluindo GPT-4 e Llama 2, têm acurácia não trivial em distinguir as próprias saídas das de outros modelos e de humanos (resumo).
- Estabelece correlação linear entre a capacidade de autorreconhecimento e a força do viés de autopreferência, controlada por ajuste fino (resumo).

**Cabe em:** metodologia (justifica usar um modelo juiz de família distinta dos sistemas sob teste) e discussão (ameaça à validade).

**RESSALVA DE DESENHO, ação recomendada:** neste experimento os dois braços rodam o **mesmo modelo local** e, se o juiz também for esse modelo, a autopreferência incide sobre os dois braços. Isso atenua o viés *comparativo*, mas não elimina o problema de nível absoluto de nota. Declare isso nas ameaças à validade e, se possível, use um modelo juiz diferente.

**Nota:** o resumo afirma a correlação linear sem dar um coeficiente único na página acessada. Localização não fixada para o coeficiente.

## 5.3 Wang et al. — LLMs não são avaliadores justos (viés de posição)

**[REVISADO POR PARES — ACL 2024]**

WANG, Peiyi et al. Large language models are not fair evaluators. In: ANNUAL MEETING OF THE ASSOCIATION FOR COMPUTATIONAL LINGUISTICS, 62., 2024, Bangkok. **Anais** [...]. v. 1: Long Papers. [S. l.]: ACL, 2024. p. 9440-9450. DOI 10.18653/v1/2024.acl-long.511.
Disponível em: https://aclanthology.org/2024.acl-long.511/. Acesso em: 31 jul. 2026.

- O ranking produzido pelo juiz LLM pode ser invertido apenas mudando a ordem em que as respostas candidatas aparecem no prompt — o viés de posição é forte o bastante para os autores o descreverem como "hackear" a avaliação (resumo).
- Propõe um arcabouço de calibração em três partes (resumo): calibração por múltiplas evidências (o juiz escreve a evidência antes de pontuar), calibração balanceada de posição (agregar os resultados das duas ordens) e calibração com humano no laço.

**Números citáveis:** com o ChatGPT como avaliador, o Vicuna-13B foi feito vencer o próprio ChatGPT em **66 de 80** consultas de teste apenas por ordenação (resumo).

**Cabe em:** metodologia — é a citação que legitima trocar as posições e agregar as duas ordens no protocolo de julgamento — e discussão.

**Nota:** o veículo é ACL 2024 (artigo longo), apesar do preprint de 2023 (arXiv:2305.17926). Não cite como 2023.

## 5.4 Liu et al. — G-Eval (desenho de prompt de juiz estruturado)

**[REVISADO POR PARES — EMNLP 2023]**

LIU, Yang et al. G-Eval: NLG evaluation using GPT-4 with better human alignment. In: CONFERENCE ON EMPIRICAL METHODS IN NATURAL LANGUAGE PROCESSING, 2023. **Anais** [...]. [S. l.]: ACL, 2023. p. 2511-2522. DOI 10.18653/v1/2023.emnlp-main.153.
Disponível em: https://aclanthology.org/2023.emnlp-main.153/. Acesso em: 31 jul. 2026.

- G-Eval combina cadeia de raciocínio com um paradigma de preenchimento de formulário: o juiz recebe os passos de avaliação e preenche um formulário estruturado de notas, em vez de emitir veredicto livre (resumo). **É a citação padrão para um prompt de juiz em formato de rubrica estruturada como o `judge.md` deste repo.**
- Avaliado em sumarização e geração de diálogo, supera métricas automáticas anteriores em correlação com julgamento humano (resumo).
- Os próprios autores sinalizam que avaliadores baseados em LLM podem ser enviesados a favor de texto gerado por LLM (resumo) — útil como limitação declarada.

**Números citáveis:** correlação de Spearman de **0,514** com julgamento humano na tarefa de sumarização usando GPT-4 como base (resumo).

**Cabe em:** fundamentação teórica (arte prévia em julgamento estruturado) e metodologia (desenho do prompt de rubrica).

## 5.5 Dubois et al. — AlpacaEval com controle de comprimento (viés de verbosidade)

**[PREPRINT arXiv — COLM 2024 indicado no campo de comentários, não confirmado em anais]**

DUBOIS, Yann; GALAMBOSI, Balázs; LIANG, Percy; HASHIMOTO, Tatsunori B. **Length-controlled AlpacaEval**: a simple way to debias automatic evaluators. [S. l.]: arXiv, 2024. Preprint. arXiv:2404.04475.
Disponível em: https://arxiv.org/abs/2404.04475. Acesso em: 31 jul. 2026.

- A preferência por resposta longa é um confundidor que sobrevive nos avaliadores automáticos mesmo após outras melhorias (resumo).
- Propõe correção estatística e não de prompt: ajustar um modelo linear generalizado sobre as preferências do anotador e prever a preferência contrafactual com diferença de comprimento zero (resumo).

**Números citáveis:** a correlação de Spearman com o LMSYS Chatbot Arena sobe de **0,94 para 0,98** após o controle de comprimento (resumo).

**Cabe em:** discussão (**confundidor plausível e específico deste experimento**: se a arquitetura supervisor produz respostas mais longas que a de agente único, parte de qualquer vantagem no juiz pode ser verbosidade) e metodologia (registrar o comprimento das respostas como variável de controle).

**Ressalva:** o campo de comentários do arXiv indica COLM 2024, mas a página de anais não pôde ser acessada. Trate como preprint, salvo verificação própria.

## 5.6 Gu et al. — levantamento sobre LLM-as-a-judge

**[PREPRINT arXiv — NÃO REVISADO]**

GU, Jiawei et al. **A survey on LLM-as-a-judge**. [S. l.]: arXiv, 2024 (v6: out. 2025). Preprint. arXiv:2411.15594.
Disponível em: https://arxiv.org/abs/2411.15594. Acesso em: 31 jul. 2026.

- Organiza a questão central da área em torno de três alavancas (resumo): melhorar consistência, mitigar vieses e adaptar a cenários variados de avaliação.
- Posiciona o julgamento por LLM como escalável, barato e consistente frente à anotação humana, afirmando que a confiabilidade exige desenho deliberado e não pode ser presumida (resumo).

**Cabe em:** fundamentação teórica — serve como citação única para estabelecer que LLM-as-judge é prática estabelecida e sistematizada.

**Ressalva:** preprint, sem veículo. O valor é a taxonomia, não números.

## 5.7 Gurram — confiabilidade do juiz em cenário agêntico (hedge das limitações)

**[PREPRINT arXiv — NÃO REVISADO, autor único, em avaliação]**

GURRAM, Bhaskar. **Evaluating tool-using language agents**: judge reliability, propagation cascades, and runtime mitigation in AgentProp-Bench. [S. l.]: arXiv, abr. 2026. Preprint. arXiv:2604.16706.
Disponível em: https://arxiv.org/abs/2604.16706. Acesso em: 31 jul. 2026.

- Argumenta que a avaliação automatizada de agentes que usam ferramentas é menos confiável do que se costuma supor, com julgamento por substring/casamento exato ficando perto do acaso frente à anotação humana (resumo).
- Um comitê de três juízes LLM alcança apenas concordância moderada com humanos nesse cenário agêntico — notavelmente mais fraca que os ~80%+ relatados para julgamento de chat aberto (resumo).

**Números citáveis** (todos do resumo): julgamento por substring com kappa de Cohen = **0,049** (nível do acaso); comitê de três LLMs kappa = **0,432** (moderado); probabilidade de propagação de erro de parâmetro para resposta final ≈ **0,62**.

**Cabe em:** discussão (limitação) e metodologia (motiva verificar manualmente uma subamostra).

**RESSALVA FORTE:** preprint de autor único, em avaliação, sem peso institucional. **Use apenas como ressalva na seção de limitações, nunca como afirmação que sustente uma conclusão.** Dito isso, o achado sobre julgamento por substring é diretamente relevante: o `eval/runner.py` deste repo hoje decide aprovação por `expected_outcome_contains`, que é exatamente julgamento por substring. Isso precisa ser reconhecido como ameaça à validade de construto ou substituído.

---

# Tema 6 — Custo, latência e tokens como métricas de avaliação

## 6.1 Liang et al. — HELM (eficiência como dimensão de primeira classe)

**[REVISADO POR PARES — TMLR 2023]** — *melhor citação para legitimar os desfechos secundários*

LIANG, Percy et al. Holistic evaluation of language models. **Transactions on Machine Learning Research**, [S. l.], 2023. arXiv:2211.09110.
Disponível em: https://arxiv.org/abs/2211.09110. Acesso em: 31 jul. 2026.

- O compromisso metodológico central do HELM é a avaliação multimétrica: sete métricas — acurácia, calibração, robustez, justiça, viés, toxicidade e **eficiência** — são medidas para cada cenário central, em vez de só acurácia, precisamente para que dimensões não relacionadas à acurácia não sejam negligenciadas e para tornar visíveis os compromissos (resumo; métricas enumeradas na seção 1.1). **É o precedente mais forte de que relatar eficiência ao lado de acurácia é prática legítima e padrão.**
- Eficiência é tratada como dimensão própria, com definição, dividida em eficiência de treino e eficiência de inferência (seção de eficiência).
- Argumenta contra usar tempo bruto observado como métrica de eficiência, porque confunde propriedades do modelo com hardware, implementação e condições do sistema, e usa em vez disso um tempo de inferência idealizado/denoised para comparabilidade entre modelos.

**Números citáveis:** as sete métricas são medidas em 16 cenários centrais, com cobertura completa em 87,5% das vezes (resumo).

**Cabe em:** fundamentação teórica e metodologia (justifica os desfechos secundários deste artigo).

**Ressalva metodológica útil:** a própria metodologia do HELM alerta que latência de relógio medida em infraestrutura compartilhada é ruidosa. Reconheça isso ao reportar latência. Confiança MÉDIA no número exato da seção de eficiência (4.9) — se for citar a seção, confira; alternativamente cite como "a seção de eficiência".

## 6.2 Kapoor et al. — agentes de IA que importam

**[REVISADO POR PARES — TMLR 2025]** — *citação central do desenho de avaliação deste artigo*

KAPOOR, Sayash; STROEBL, Benedikt; SIEGEL, Zachary S.; NADGIR, Nitya; NARAYANAN, Arvind. AI agents that matter. **Transactions on Machine Learning Research**, [S. l.], 2025. arXiv:2407.01502. DOI 10.48550/arXiv.2407.01502.
Disponível em: https://arxiv.org/abs/2407.01502. Acesso em: 31 jul. 2026.

- Tese central (resumo; seção 2, "AI agent evaluations must be cost-controlled"): benchmarks de agentes que otimizam só acurácia produzem agentes desnecessariamente complexos e caros, e o custo precisa ser tratado como dimensão controlada da avaliação.
- Recomenda visualizar o compromisso acurácia-custo como **curva de Pareto** em vez de placar unidimensional (seção 2.2), e mostra que a avaliação bidimensional muda as conclusões que se tiraria (seção 2.3).
- Recomenda que benchmarks relatem custo em dólares junto com acurácia, **relatem contagens de tokens de entrada e saída para que os resultados possam ser recalculados quando os preços mudarem**, e relatem variância entre execuções repetidas. Isso mapeia diretamente nos desfechos secundários deste artigo e justifica reportar tokens **e** dinheiro, não apenas um dos dois.
- Demonstra otimização conjunta de custo e acurácia como objetivo de projeto, não só convenção de relato (seção 3; montagem HotPotQA em 3.1, resultados em 3.2).

**Números citáveis:** para acurácia substancialmente semelhante, o custo pode variar em quase **duas ordens de grandeza** entre desenhos de agente (afirmação de destaque, seção 2). Linhas de base simples são melhorias de Pareto sobre agentes do estado da arte nos 164 problemas do HumanEval, com **cada agente executado cinco vezes** e relato de acurácia média e custo total médio (legenda da Figura 1). Otimização conjunta no HotPotQA: ~53% menos custo variável com acurácia semelhante no GPT-3.5, ~41% no Llama-3-70B (seção 3.2, confiança MÉDIA).

**Cabe em:** fundamentação teórica (por que eficiência pertence a um experimento com agentes), metodologia (protocolo de 5 execuções com relato da média; relatar tokens e dólares) e discussão (**se a arquitetura supervisor ganhar em acurácia e perder em custo, é este o enquadramento que transforma isso em achado, e não em fracasso**).

**Nota de verificação:** a condição TMLR 2025 foi confirmada por registro no dblp; o OpenReview bloqueou acesso automatizado. Os pares individuais de acurácia/custo da Figura 1 têm confiança MÉDIA — releia antes de imprimir valores específicos.

## 6.3 Chen, Zaharia & Zou — FrugalGPT

**[PREPRINT arXiv]** — a alegação de publicação em TMLR 2024 circula em fontes secundárias e **não pôde ser verificada**; trate como preprint

CHEN, Lingjiao; ZAHARIA, Matei; ZOU, James. **FrugalGPT**: how to use large language models while reducing cost and improving performance. [S. l.]: arXiv, 2023. Preprint. arXiv:2305.05176.
Disponível em: https://arxiv.org/abs/2305.05176. Acesso em: 31 jul. 2026.

- Estabelece o custo como restrição de projeto de primeira ordem para aplicações com LLM, notando que os preços por token entre APIs comerciais diferem em cerca de duas ordens de grandeza (resumo).
- Organiza a redução de custo em três famílias de estratégia (resumo): adaptação de prompt, aproximação de LLM e cascata de LLM. Útil se o artigo discutir por que um supervisor roteando para especialistas mais baratos poderia ser racional em custo.

**Números citáveis:** iguala o melhor LLM único (GPT-4) com até **98%** de redução de custo, ou supera a acurácia do GPT-4 em **4%** com custo equivalente (resumo).

**Cabe em:** fundamentação teórica (projeto de sistemas com LLM sensível a custo) e discussão.

## 6.4 Stanford HAI — AI Index 2025 (contexto do custo de inferência)

**[RELATÓRIO TÉCNICO INSTITUCIONAL — NÃO REVISADO]**

STANFORD INSTITUTE FOR HUMAN-CENTERED ARTIFICIAL INTELLIGENCE. **The 2025 AI Index Report**: research and development. Stanford: Stanford HAI, 2025.
Disponível em: https://hai.stanford.edu/ai-index/2025-ai-index-report/research-and-development. Acesso em: 31 jul. 2026.

- O custo de inferência para um dado nível de capacidade cai de forma acentuada, razão pela qual um experimento deve relatar contagem de tokens junto do custo em dólares — cifras em dólar envelhecem rápido. É a ponte para a recomendação de 6.2 de relatar tokens.

**Números citáveis:** consultar um modelo com desempenho equivalente ao GPT-3.5 (64,8 no MMLU) caiu de **US$ 20,00 por milhão de tokens em nov. 2022 para US$ 0,07 por milhão em out. 2024** (Gemini-1.5-Flash-8B), redução superior a 280 vezes. Localização: seção intitulada "AI models become increasingly cheaper to use". Também relatado: custo de hardware de ML caindo ~30% ao ano e eficiência energética melhorando ~40% ao ano.

**Cabe em:** discussão (contextualiza os números de custo deste artigo como fotografia de um momento) ou introdução.

**Ressalva:** relatório institucional, não revisado por pares. Foi verificada apenas a edição 2025; pode existir edição 2026.

## 6.5 NVIDIA — definições operacionais de latência

**[RELATÓRIO TÉCNICO DE LABORATÓRIO — NÃO REVISADO / documentação de fornecedor]**

NVIDIA CORPORATION. **A comprehensive guide to NIM LLM latency-throughput benchmarking**: metrics. Documentação técnica. [S. l.: s. n.], [s. d.].
Disponível em: https://docs.nvidia.com/nim/benchmarking/llm/latest/metrics.html. Acesso em: 31 jul. 2026.

- Fornece definições operacionais adotáveis literalmente na metodologia, cada uma sob seu próprio título de seção: **Time to First Token** (tempo entre o envio da consulta e o primeiro token não vazio, incluindo enfileiramento, *prefill* e latência de rede); **End-to-End Request Latency** (envio até resposta completa, com `e2e_latency = TTFT + tempo de geração`); **Inter-Token Latency** (intervalo médio entre tokens consecutivos, calculado como `(e2e_latency − TTFT) / (total_output_tokens − 1)`, também chamado tempo por token de saída); **Tokens Per Second**; **Requests Per Second**.
- Registra que prompts mais longos inflam o TTFT porque o cache KV precisa ser construído antes do início da geração — **relevante direto para este artigo**, já que a arquitetura supervisor envia prompts mais longos que o agente único.

**Cabe em:** metodologia (definir com precisão o que "latência" significa neste experimento).

**Ressalva:** documentação de fornecedor, sem data, não revisada. Em termos ABNT, trate como documento eletrônico / manual técnico. Não foi encontrada alternativa revisada por pares para definições de latência nesta pesquisa; MLPerf Inference e a documentação do vLLM não foram verificados.

---

# Lacunas declaradas

Em vez de preencher com fonte fraca, registro o que **não** existe no material levantado.

1. **Não foi encontrado nenhum estudo revisado por pares que compare, cabeça a cabeça, um supervisor multi-agente contra um agente único com tool calling, com contabilidade completa de custo.** Os mais próximos são 2.2 (paridade com economia para o agente único, mas é preprint e os fluxos não têm forma de supervisor) e 1.4 (supervisor vence, mas é preprint e **não tem braço de agente único**). Essa lacuna é, ela mesma, justificativa citável para este experimento, e deve ser declarada na introdução.
2. **Não foi encontrado paper revisado por pares que varra o número de ferramentas (10 → 25 → 50 → 100) num modelo de fronteira e publique uma curva limpa de acurácia.** O BFCL não fornece isso: sua categoria "multiple function" usa 2-4 candidatas. Afirmar o contrário é sobreafirmação. Enquadre como motivação.
3. **Nada de utilizável surgiu de DeepSeek, Moonshot AI (Kimi), Z.AI (GLM), Alibaba (Qwen), MiniMax, Meta, NVIDIA (fora das definições de latência em 6.5) ou Google DeepMind sobre a pergunta específica de arquitetura multi-agente versus agente único.** As publicações desses laboratórios tratam de capacidade de modelo e de benchmark, não da economia dessa escolha arquitetural. Não vale inflar a lista de referências com eles só para cumprir a lista de alvos do ticket.
4. **A concordância juiz-humano medida em 5.1 vem de chat aberto, não de trajetórias agênticas.** O único material encontrado que ataca essa lacuna (5.7) é preprint de autor único. Declare a lacuna nas limitações.
5. **Latência quase não é reportada nos benchmarks de agentes.** Entre todas as fontes do tema 4, só o τ-Knowledge (4.3) publica duração por tarefa contra sucesso; τ-bench e τ²-bench reportam custo em dólares e nenhum reporta latência. Como este artigo roda modelo local e não paga API, a latência é justamente o desfecho secundário mais informativo — e é onde há menos precedente. Combine 6.5 (definições operacionais) com 4.3 (precedente de plotagem) e declare que a prática ainda não está consolidada.
6. **Armadilha de citação a evitar:** o τ-bench é rotineiramente citado como preprint porque o PDF da v1 no arXiv ainda traz "Preprint. Under review." e o campo de comentários está vazio. **Ele foi publicado no ICLR 2025.** Citá-lo como preprint enfraquece gratuitamente a fundamentação deste artigo — é uma das poucas fontes revisadas por pares diretamente sobre agentes de atendimento com ferramentas.

# Não verificadas — não citar

Estas apareceram em busca e **não foram confirmadas na fonte**. Nenhuma conta para o mínimo de fontes. Não as inclua no artigo com base neste documento.

- **OpenAI, "A practical guide to building agents"** (PDF, cdn.openai.com, abr. 2025). Lead genuinamente relevante — descreve o padrão "manager" e o padrão de *handoff* descentralizado. O PDF de 7 MB não permitiu extração de texto, então redação, paginação e autoria não puderam ser confirmadas. Se quiser usá-la, abra o PDF manualmente e fixe as páginas.
- Corpo do texto de arXiv:2502.08788 (fonte 2.4): inacessível por todas as rotas tentadas. Cite só o resumo.
- Texto completo do BFCL (3.6) e de "Lost in the Middle" (3.7): PDFs inacessíveis. Citações em nível de resumo e do blog oficial apenas.
- Percentuais do arranjo S1 do MT-Bench e a célula do Chatbot Arena em 5.1: leituras inconsistentes. Reconfira nas Tabelas 5 e 6 antes de imprimir.
- Alegação de que o FrugalGPT saiu em TMLR 2024: não confirmada em página primária.
- Preprints de baixo perfil localizados mas **não recomendados** (existem, mas são de autores desconhecidos, sem veículo, e desnecessários dado o material acima): arXiv:2605.24660 (*How many tools should an LLM agent see?*) e arXiv:2606.06284 (*ToolChoiceConfusion*). Registrados aqui para que ninguém os reencontre e os suponha mais fortes do que são. Nota relevante do primeiro: ele argumenta que listas curtas podem ser **curtas demais**, ou seja, não sustenta uma leitura ingênua de "menos é sempre melhor".
- Citadas em buscas mas nunca acessadas, portanto todos os detalhes são não confirmados: "MCP Server Architecture Patterns for LLM-Integrated Applications" (2606.30317), "The 99% Success Paradox" (2605.18857), ToolMATH (2602.21265), Mem2ActBench (2601.19935). **O número "7-85% de degradação", que circula bastante, não foi rastreado até uma fonte verificável — não o coloque no artigo.**
- **Veículo do τ²-bench (4.2):** existe fórum no OpenReview (`LGmO9VvuP5`) que não pôde ser acessado (barreira antibot, API 403). Não foi possível confirmar nem negar aceitação. **Não alegue veículo** — cite como preprint até verificar você mesmo.
- Valores por k da Figura 4 do τ-bench: são gráfico, não estão impressos no texto. Só a afirmação textual (pass^1 > 60% e pass^8 < 25% para o gpt-4o em τ-retail) é citável. Os valores tabulados por k do README oficial servem, mas para modelos posteriores e com o aviso do próprio repositório de que aquelas tarefas não são atualizadas.
- Divergência interna do τ-bench: Tabela 2 informa 35,2 e Tabela 3 informa 33,2 para gpt-4o em airline. Se citar as duas, sinalize.
- Definições internas de métrica do CRMArena (4.4): só resumo e página de anais foram lidos. Para métricas, cite 4.5.
- Não perseguidos nesta rodada: PandaLM, JudgeBench, MLPerf Inference, documentação do vLLM, τ³-bench (mencionado pelo README do τ-bench como sucessor, não investigado), MultiWOZ, AgentBench, WorkBench, MINT, ToolTalk.

# Ganchos para o repositório

Onde a literatura toca o código deste repo, para uso na metodologia:

- `eval/runner.py` decide `passed` por conjunção de casamento exato de intenção, casamento de escalonamento e `expected_outcome_contains` (substring). **Nuance a não simplificar:** o τ-bench também usa substring — mas só no componente **r_output**, sempre multiplicado pelo **r_action**, que é comparação objetiva de estado final de banco (4.1, §3). O critério atual deste repo tem apenas o lado do texto, sem o lado do estado. Ou seja, o que 5.7 mede perto do acaso é o julgamento por substring **isolado**, que é exatamente o caso aqui. Duas saídas: acrescentar verificação de estado final (as ferramentas de escrita do repo — `pay_invoice`, `block_card`, `request_limit_increase` — dão base para isso) ou declarar a limitação como ameaça à validade de construto.
- A conjunção atual mistura três construtos num só booleano: classificação de intenção, decisão de escalonamento e conteúdo da resposta. O τ-bench separa em dois fatores explícitos e multiplica. Vale explicitar a fórmula do critério de sucesso no artigo, seja qual for a escolha.
- `prompts/judge.md` já é um juiz de rubrica estruturada com saída JSON, o que corresponde ao paradigma de preenchimento de formulário de 5.4 (G-Eval). Falta, para ficar defensável: troca de posições (5.3), avaliação guiada por referência (5.1, seção 3.4) e relato de concordância com uma subamostra anotada por humano (5.1).
- `eval/eval_set.jsonl` tem 15 casos e `runner.py` roda **uma vez por caso**, sem repetição. Isso não permite pass^k nem estimativa de variância. Precedentes citáveis para corrigir: ao menos 3 tentativas por tarefa (4.1, §5), 4 tentativas (4.2, 4.3), 5 execuções com relato de média e custo médio (6.2, Fig. 1). Com 15 casos e 4 tentativas são 60 execuções por braço, 120 no total — viável na RTX 3060 e suficiente para reportar pass^1 e pass^4.
- Nenhuma métrica de latência, tokens ou custo é coletada hoje pelo `runner.py`. Antes de rodar o experimento, instrumente: TTFT e latência ponta a ponta (definições em 6.5), tokens de entrada e de saída separados (6.2 exige a separação para o resultado ser recalculável) e contagem de chamadas de ferramenta (4.3 usa isso como eixo de eficiência).
- O `runner.py` fixa `customer_id` e `customer_document` para todos os casos, e não há simulador de usuário — cada caso é de turno único. Todos os benchmarks do tema 4 são multi-turno com usuário simulado, e 4.5 mostra queda de ~58% para ~35% ao passar de turno único a multi-turno. Declare o turno único como escolha de escopo e como ameaça à validade externa.
- Os dois braços compartilham o mesmo modelo base local, ou seja, o caso homogêneo que 2.2 encontra em paridade e que 2.4 aponta como o mais fraco para multi-agente. Vale declarar como hipótese esperada, não como surpresa.
- Nomes e descrições de ferramentas precisam ser idênticos entre os braços, senão a qualidade da redação vira confundidor (3.5, 3.9).
