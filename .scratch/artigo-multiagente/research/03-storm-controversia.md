# STORM — Mapa de controvérsia e autocrítica

**Tópico.**
Arquiteturas multi-agente com LLM (supervisor + sub-agentes especialistas) versus agente único com tool calling em sistemas de atendimento ao cliente: o ganho de qualidade compensa o custo em latência, tokens e complexidade?

**Papel do leitor (usado na fase 3).**
Estudante de graduação escrevendo artigo científico de 5–7 páginas em ABNT, que vai rodar experimento controlado no próprio chatbot de suporte bancário (LangGraph, supervisor + especialistas, RAG, 9 intents, modelo local em RTX 3060 12 GB).
Desfecho primário: sucesso de tarefa. Secundários: latência, tokens, custo.

**Método.**
Stanford STORM (NAACL 2024), 4 fases em sequência: varredura multi-perspectiva → mapa de contradições → briefing de síntese → peer review do próprio briefing.

**Legenda de ancoragem.**
- `[F]` = ancorado em fonte primária consultada nesta sessão (paper, blog de engenharia, release oficial).
- `[F-sec]` = ancorado em fonte secundária (síntese de busca, post de terceiros resumindo um primário). Confirmar no primário antes de citar em ABNT.
- `[R]` = raciocínio do modelo, não ancorado. Vale como argumento, não como evidência citável.

**Aviso de escopo.**
Este documento NÃO é lista bibliográfica (outro agente cobre isso) e não toca `02-literatura.md`.
O produto aqui é: onde a área discorda, com a evidência de cada lado; quais armadilhas metodológicas derrubam experimentos desse tipo; e o que uma banca atacaria.

---

## FASE 1 — Varredura multi-perspectiva

### 1.1 Praticante (constrói e opera agentes em produção)

**Posição central.**
Multi-agente resolve um problema de *engenharia de contexto*, não de inteligência: quando o prompt do agente único fica com 40 ferramentas e 9 políticas de domínio, ele começa a errar seleção de ferramenta e a ignorar instruções do meio do contexto.
Dividir em especialistas é a forma barata de manter cada janela de contexto pequena e cada conjunto de ferramentas curto — o ganho vem da redução de escopo por chamada, não da "colaboração" entre agentes.

**Evidência mais forte.**
- A Anthropic reporta que seu sistema de pesquisa multi-agente (Opus 4 líder + Sonnet 4 subagentes) superou o Opus 4 single-agent em **90,2%** no eval interno de pesquisa (identificar todos os membros de conselho de empresas de TI do S&P 500). `[F]`
- O mesmo texto afirma que o uso de tokens sozinho explica ~**80% da variância** de desempenho no BrowseComp, com escolha de modelo e chamadas de ferramenta explicando o resto. `[F]`
- Modelos pequenos degradam justamente em seleção de ferramenta quando o número de ferramentas cresce; a orquestração multi-estágio é a mitigação recomendada na prática. `[F-sec]`
- Na Berkeley Function-Calling Leaderboard, modelos pequenos despencam em multi-turn: xLAM-2-3b-fc-r 65,74% geral vs **55,62% multi-turn**; Qwen3-4B 62,04% geral vs **35,25% multi-turn**. `[F-sec]`

**O que só esta voz diria.**
Ninguém em produção escolhe arquitetura por acurácia média — escolhe por *depurabilidade*.
Multi-agente ganha adoção porque quando quebra você sabe QUAL especialista quebrou; o agente único monolítico quebra como uma caixa preta de 8 mil tokens.
Esse é o benefício real e ele nunca aparece no eixo Y de nenhum benchmark.

---

### 1.2 Acadêmico (lê e produz literatura revisada por pares)

**Posição central.**
A literatura revisada por pares é muito menos entusiasmada que os blogs de engenharia: quando o orçamento computacional é controlado, a vantagem multi-agente encolhe ou desaparece.
O consenso emergente 2025–2026 é que grande parte do ganho reportado é *compute confundido com arquitetura*.

**Evidência mais forte.**
- **MAST** (Cemri et al., arXiv 2503.13657, NeurIPS 2025 Datasets & Benchmarks): 1.600+ traces anotados em 7 frameworks MAS, taxonomia de **14 modos de falha** em 3 categorias; concordância entre anotadores **κ = 0,88**; **41,8%** das falhas são de *system design* (papéis ambíguos, decomposição ruim, condição de parada ausente), não de capacidade do modelo. `[F-sec, primário verificável no arXiv]`
- **Tran & Kiela**: sob orçamento igual de *thinking tokens*, agentes únicos igualam ou superam MAS em raciocínio multi-hop (Qwen3, DeepSeek-R1-Distill-Llama, Gemini 2.5); argumento formal via **Data Processing Inequality** — mensagem repassada de um agente a outro só pode perder informação, nunca ganhar. `[F-sec]`
- **"The Illusion of Multi-Agent Advantage"** (arXiv 2606.13003): CoT com Self-Consistency supera 6 frameworks MAS automáticos (DyLAN, MAS-Zero, ADAS, AFlow, MaAS, MAS-Orchestra) "frequentemente com acurácia maior a menos de **10% do custo computacional**"; ganhos dos MAS automáticos são marginais (DyLAN +4,3pp a 2,5× custo; MAS-Oracle +6,0pp a 1,9× custo). `[F]`
- O mesmo paper documenta **colapso funcional**: os agentes chegam a consenso unânime imediato em ~**70%** dos casos com GPT-4o e **>90%** com GPT-5 — ou seja, o mecanismo de debate/verificação que justifica a arquitetura simplesmente não acontece; e o verificador exibe viés posicional escolhendo a saída anterior em **>45%** dos casos. `[F]`
- **τ-bench** (ICLR 2025), domínio de atendimento ao cliente: agentes de function calling de ponta resolvem <50% das tarefas e são **inconsistentes** — `pass^8 < 25%` no varejo, contra ~60% em tentativa única. `[F-sec]`

**O que só esta voz diria.**
O achado do "colapso de consenso" é mais devastador que qualquer número de acurácia: ele mostra que em boa parte dos MAS publicados **o mecanismo alegado nem sequer opera**.
Quando você mede o que a arquitetura *diz* fazer (debate, verificação cruzada) em vez do que ela *entrega* (score), descobre que muitos papers estão medindo o efeito de gastar mais tokens e chamando isso de coordenação.

---

### 1.3 Cético (acha que o mainstream multi-agente está errado)

**Posição central.**
Multi-agente é uma regressão de engenharia disfarçada de avanço: você troca um sistema com estado único e rastreável por um sistema distribuído com decisões implícitas conflitantes — e sistemas distribuídos são a categoria de software que a indústria levou 30 anos para aprender a operar.
O ganho reportado some assim que você iguala compute e controla estocasticidade.

**Evidência mais forte.**
- Cognition (Walden Yan, "Don't Build Multi-Agents"): dois princípios — *"compartilhe contexto, e compartilhe traces completos, não mensagens isoladas"* e *"ações carregam decisões implícitas, e decisões conflitantes geram resultados ruins"*. `[F]`
- Exemplo concreto do mesmo texto (Flappy Bird): subagente 1 constrói fundo de Super Mario, subagente 2 constrói um pássaro visualmente incompatível; o coordenador recebe trabalho impossível de combinar. `[F]`
- A própria Cognition afirma que o **Claude Code evita subagentes paralelos** — subtarefas apenas respondem perguntas, não executam trabalho independente. `[F]`
- Posição posterior da mesma empresa ("Multi-Agents: What's Actually Working"): multi-agente funciona quando **as escritas permanecem single-threaded** e os agentes extras contribuem *inteligência*, não *ações*. `[F-sec]`
- A própria Anthropic lista quando NÃO usar: tarefas em que todos os agentes precisam do mesmo contexto ou têm muitas dependências entre si; a maioria das tarefas de código; e reconhece que "agentes LLM ainda não são bons em coordenar e delegar em tempo real". `[F]`
- CrewAI consome ~**3× mais tokens e ~3× mais tempo** que LangChain para fazer uma única chamada de ferramenta (benchmark de 5 tarefas, 2.000 execuções). `[F-sec]`
- Em LangGraph, as chamadas de roteamento do supervisor responderam por **>30% do tempo total de resposta** em um estudo de caso; trocar para handoff direto (swarm) cortou ~**40%** do tempo fim-a-fim. `[F-sec]`

**O que só esta voz diria.**
O número de 90,2% da Anthropic é sobre **pesquisa breadth-first** — encontrar N fatos independentes em paralelo, onde a informação total excede uma janela de contexto.
Atendimento ao cliente é o *oposto* disso: uma conversa, um cliente, um estado de conta, dependências fortes entre passos, tudo cabendo folgado em uma janela.
Importar o número de 90,2% para justificar multi-agente em suporte é transplante de evidência entre domínios com estruturas de tarefa opostas — e é exatamente a falácia que o autor do próprio blog adverte contra. `[F para as duas metades; R para a conclusão]`

---

### 1.4 Economista (segue o dinheiro e os incentivos)

**Posição central.**
Toda a cadeia de valor da IA generativa é remunerada por token consumido, e multi-agente consome 15× mais tokens que chat — logo, existe um alinhamento de incentivos estrutural entre "multi-agente é o futuro" e a receita de quem publica essa afirmação.
Isso não torna a afirmação falsa, mas explica por que a evidência pró-multi-agente vem majoritariamente de blogs de engenharia de vendors e a evidência contra vem majoritariamente de papers com controle de orçamento.

**Evidência mais forte.**
- Sistemas multi-agente usam ~**15× mais tokens que chat**; agentes únicos, ~**4×** `[F]`. O delta 4×→15× é receita direta para o provedor de inferência.
- A própria Anthropic condiciona a viabilidade a "tarefas cujo valor seja alto o bastante para pagar pelo desempenho aumentado" `[F]` — ou seja, o vendor admite que a economia só fecha no topo da curva de valor.
- Gartner: **>40% dos projetos de IA agêntica serão cancelados até o fim de 2027**, por custo crescente, valor de negócio indefinido e controles de risco inadequados; o relatório cita "agent washing" (chatbot rebatizado de agente). `[F-sec]`
- MIT: ~**95% dos pilotos de GenAI corporativos** não entregam o ROI esperado; apenas 11–14% dos pilotos de agentes chegam a produção em escala. `[F-sec]`
- Klarna: substituiu ~700 atendentes, 2,3 milhões de chats no primeiro mês (fev/2024); em maio/2025 recontratou humanos, com o CEO admitindo que automação puxada por custo produz "qualidade menor". `[F-sec]`

**O que só esta voz diria.**
O experimento certo não é "multi-agente é melhor?" e sim "**quanto custa cada ponto percentual de sucesso de tarefa?**".
Um ganho de +5pp que custa 2,5× tokens e +1,8s de latência tem preço-sombra: em suporte bancário de alto volume, cada segundo adicional tem elasticidade de abandono, e cada ponto de sucesso evita um ticket humano cujo custo é conhecido.
Publicar o resultado como razão custo-benefício (ΔSucesso / ΔCusto e ΔSucesso / ΔLatência) é mais defensável e mais útil que publicar duas colunas de médias.

---

### 1.5 Historiador (já viu esse padrão)

**Posição central.**
"Vários especialistas cooperando num quadro-negro" não é ideia de 2024 — é a arquitetura *blackboard* dos anos 1970 (Hearsay-II, reconhecimento de fala, financiada pela ARPA), estendida no Distributed Vehicle Monitoring Testbed de Victor Lesser e consolidada como campo "multi-agent systems" nos anos 1990 (Lesser, Gasser, Wooldridge, Jennings).
O ciclo anterior terminou em inverno: vendors prometeram demais, sistemas não entregaram transformação, financiamento secou no fim dos anos 1980.

**Evidência mais forte.**
- Blackboard/Hearsay-II como primeira tentativa de integrar módulos "cooperantes" para problemas que nenhum especialista isolado resolvia. `[F-sec]`
- DVMT de Lesser como primeira MAS prática, com arquitetura blackboard para interpretação distribuída de sensores. `[F-sec]`
- O padrão de superpromessa de vendors → desilusão → corte de financiamento no fim dos 80/início dos 90 está documentado como o mecanismo do inverno anterior. `[F-sec]`
- Trabalhos de 2025 explicitamente ressuscitam blackboard para LLMs (arXiv 2507.01701), fechando o círculo. `[F-sec]`

**O que só esta voz diria.**
Nos dois ciclos, o mesmo erro de medição: a arquitetura foi avaliada por *demonstrações em tarefas escolhidas a dedo*, não por confiabilidade repetida sob distribuição realista.
O equivalente moderno do que matou o ciclo anterior está no τ-bench: `pass^1 ≈ 60%` parece produto; `pass^8 < 25%` é a mesma coisa medida honestamente. `[F-sec para os números; R para o paralelo]`
Historicamente, o que sobreviveu do blackboard não foi a "sociedade de agentes" — foi o *quadro-negro*: o estado compartilhado.
A previsão histórica é que sobreviva o estado compartilhado (contexto/memória bem engenheirados) e morra a metáfora antropomórfica de "equipe de especialistas".

---

## FASE 2 — Mapa de contradições

### 2.1 Onde exatamente a área discorda (os dois lados, com evidência de cada)

#### Clash 1 — "O ganho é da arquitetura" vs "O ganho é do compute"

| | Lado A: o ganho é real e arquitetural | Lado B: o ganho é compute disfarçado |
|---|---|---|
| Afirmação | Subagentes com janelas separadas escalam capacidade de raciocínio paralelo além do que uma janela comporta | Sob orçamento igual de tokens, a vantagem some; o que se mediu foi gasto, não coordenação |
| Evidência | +90,2% sobre single-agent no eval interno de pesquisa da Anthropic `[F]`; tokens explicam ~80% da variância no BrowseComp — apresentado como *justificativa* do design `[F]` | Tran & Kiela: single-agent iguala/supera MAS sob thinking-token budget igual, em 3 famílias de modelo `[F-sec]`; "Illusion of MAS Advantage": CoT-SC vence 6 frameworks MAS a <10% do custo `[F]` |
| Fraqueza do lado | Eval interno, não replicável por terceiros; tarefa é breadth-first search, o caso mais favorável possível ao paralelismo `[R]` | Benchmarks de raciocínio/QA, não de atendimento multi-turno com ferramentas e políticas de domínio `[R]` |

**Ponto crítico e pouco notado:** os dois lados usam o **mesmo fato** (tokens explicam ~80% da variância) como prova. `[F para o fato; R para a observação]`
Para o lado A é a razão de existir da arquitetura; para o lado B é a confissão de que a variável causal é orçamento, não topologia.
Esta é a contradição mais explorável do artigo, porque não exige escolher entre fontes — exige apenas apontar que a mesma medida sustenta interpretações opostas, e que só um experimento com **compute controlado** desempata.

#### Clash 2 — "Isolar contexto ajuda" vs "Isolar contexto é a causa das falhas"

| | Lado A: isolar contexto ajuda | Lado B: isolar contexto é o defeito |
|---|---|---|
| Afirmação | Janela menor + ferramentas menos numerosas por agente = menos erro de seleção e menos diluição de instrução | Todo handoff perde informação; decisões implícitas dos subagentes entram em conflito e o coordenador recebe trabalho incompatível |
| Evidência | Degradação de seleção de ferramenta em modelos pequenos conforme o nº de ferramentas cresce `[F-sec]`; queda de multi-turn na BFCL (Qwen3-4B: 62,04% → 35,25%) `[F-sec]` | Cognition: princípios de trace completo e decisões implícitas; exemplo Flappy Bird; Claude Code evita subagentes paralelos `[F]`; MAST: 41,8% das falhas são de design de sistema `[F-sec]`; argumento DPI (informação só se perde no repasse) `[F-sec]` |

**Síntese possível (não é meio-termo preguiçoso):** os dois lados podem estar certos porque falam de eixos diferentes — *tamanho do contexto por chamada* (ajuda) vs *fragmentação do contexto entre chamadas* (atrapalha). `[R]`
A arquitetura que ganha é a que reduz o primeiro sem aumentar o segundo: ferramentas/prompt condicionados à intenção **dentro de um agente único**, com estado compartilhado.
Isso é literalmente a leitura histórica do blackboard (§1.5) e a posição atual da Cognition (escritas single-threaded, agentes extras contribuem inteligência, não ações) `[F-sec]`.

#### Clash 3 — "MAS eleva modelos fracos" vs "MAS só funciona com modelo forte"

| | Lado A | Lado B |
|---|---|---|
| Afirmação | Decompor tarefa permite que modelos menores/baratos façam trabalho que sozinhos não fariam (líder caro + workers baratos) | MAS só produz ganho sobre base forte; sobre base fraca a coordenação custa mais do que rende |
| Evidência | Arquitetura Opus-4-líder + Sonnet-4-workers da Anthropic é exatamente esse desenho `[F]` | "Illusion": MAS só teve sucesso com modelos fortes, contradizendo diretamente a alegação de que MAS "eleva modelos fracos a desempenho de fronteira" `[F]`; quantização degrada **especificamente a geração de tool call**, tornando modelos quantizados inadequados para papel de worker `[F-sec]`; modelos <30B perdem 3–5% sob NVFP4 vs <2% em 200B+ `[F-sec]` |

**Este é o clash que decide o experimento do usuário.** `[R]`
Um modelo local quantizado em RTX 3060 12 GB está do lado exato onde o Lado B prevê que multi-agente *perde*: cada handoff do supervisor é uma tool call, e tool call é a capacidade que a quantização mais destrói.
Ou seja: a hipótese default para este hardware não é "multi-agente ganha um pouco", é **"multi-agente pode perder"** — e um resultado nulo ou negativo é cientificamente informativo, não um fracasso do trabalho.

#### Clash 4 — "Sucesso de tarefa é a métrica" vs "Consistência é a métrica"

Lado A (quase toda a literatura de MAS): reporta acurácia/pass@1 média. `[R]`
Lado B (τ-bench): `pass^k` — a fração de k tentativas independentes da *mesma* tarefa que **todas** dão certo; gpt-4o cai de ~60% (pass^1) para <25% (pass^8) no varejo. `[F-sec]`
Em atendimento bancário, o lado B é o relevante: um sistema que acerta 60% das vezes na mesma pergunta não é um produto, é uma loteria regulada. `[R]`

#### Clash 5 — "Especialização" vs "Ferramentaria" (a disputa que quase ninguém nomeia)

Lado A assume que "especialista" = agente com persona/prompt próprio.
Lado B observa que o efeito atribuído à persona pode vir inteiramente de **restringir o conjunto de ferramentas visíveis** — que é obtenível sem nenhum agente extra. `[R, com apoio indireto em `[F-sec]` sobre degradação por nº de ferramentas]`
Nenhum dos trabalhos consultados isola essas duas variáveis. Voltamos a isso em §2.5.

---

### 2.2 Qual perspectiva tem a evidência mais forte, e qual a mais fraca

**Mais forte: o Acadêmico.**
É o único lado com controle experimental explícito (orçamento de tokens igualado), com múltiplas famílias de modelo, com taxonomia validada por concordância entre anotadores (κ = 0,88) e com verificação do *mecanismo* e não só do resultado (colapso de consenso em ~70%/>90%, viés posicional >45%). `[F/F-sec]`
Um achado de mecanismo é epistemicamente superior a um achado de desempenho, porque explica quando o efeito deve ou não aparecer.

**Mais fraca: o Praticante.**
Seu argumento mais forte (depurabilidade, manutenibilidade) é real e é justamente o que **não tem medida publicada** — nenhuma das fontes consultadas quantifica custo de manutenção, tempo de diagnóstico de falha ou velocidade de iteração por arquitetura. `[R]`
E sua evidência quantitativa mais citada (90,2%) vem de eval interno não replicável, em domínio (pesquisa breadth-first) estruturalmente oposto ao atendimento.

**Menção honrosa em fragilidade: o Economista.**
Os números de Gartner (>40% cancelados) e MIT (95% sem ROI) são projeções/surveys de consultoria, não medições experimentais — servem para *contextualizar motivação* na introdução, jamais para sustentar uma conclusão metodológica. `[R]`
Uma banca que os veja na seção de resultados vai atacar.

---

### 2.3 A pergunta que resolveria a maior contradição

> **Com orçamento de compute rigorosamente igualado (mesmo total de tokens gerados, mesmo número de chamadas ao modelo, mesmo modelo base), a arquitetura supervisor+especialistas ainda produz sucesso de tarefa superior ao agente único — e, se produz, o ganho persiste quando se mede `pass^k` em vez de `pass^1`?**

Se a resposta for "não", tudo que a área chama de vantagem multi-agente é *scaling de inferência mal rotulado*, e o mesmo compute gasto em self-consistency dentro de um agente único rende mais. `[R, com suporte em `[F]` de "Illusion" e `[F-sec]` de Tran & Kiela]`
Se for "sim", a variável causal é isolamento de contexto e o campo tem um resultado arquitetural genuíno.
**Esta pergunta é diretamente respondível pelo experimento do usuário** e deveria ser a pergunta de pesquisa formal do artigo — é mais precisa e mais defensável que "multi-agente compensa?".

---

### 2.4 O que todas as perspectivas concordam (provavelmente verdadeiro — até os opositores confirmam)

1. **Multi-agente custa significativamente mais em tokens e latência.** Nenhum lado disputa isso; a Anthropic (proponente) publica os 15× como fato. `[F]`
2. **O ganho é condicional à estrutura da tarefa, não universal.** Proponentes limitam a tarefas paralelizáveis e independentes `[F]`; críticos mostram que fora dessa estrutura o ganho some `[F]`.
3. **A maior parte das falhas é de design, não de capacidade do modelo.** MAST: 41,8% em design de sistema `[F-sec]`; Cognition: decisões implícitas conflitantes `[F]`. Modelo maior não conserta.
4. **Modelos atuais coordenam mal entre si em tempo real.** Admitido explicitamente pelo lado proponente `[F]`.
5. **Confiabilidade repetida é muito pior que o desempenho de tentativa única.** `pass^8 < 25%` vs `pass^1 ≈ 60%` `[F-sec]`.
6. **Atendimento ao cliente é ambiente hostil a MAS clássico:** contexto compartilhado obrigatório, dependências fortes entre passos — exatamente a lista de contraindicações do próprio proponente `[F]`.

Estes 6 pontos são o material mais seguro para a fundamentação do artigo, porque sobrevivem ao contraditório. `[R]`

---

### 2.5 O que NENHUMA perspectiva abordou (o ponto cego do campo)

**(a) Ninguém separa as três variáveis que a palavra "multi-agente" mistura.** `[R]` — *o achado mais valioso deste documento.*
"Supervisor + especialistas" muda simultaneamente:
1. **compute** (mais chamadas, mais tokens),
2. **escopo de ferramentas por chamada** (cada especialista vê poucas tools),
3. **isolamento de contexto** (cada especialista não vê o histórico completo).
Toda a literatura consultada compara o pacote inteiro contra agente único, e depois atribui o resultado à "arquitetura".
Nenhum dos trabalhos consultados roda o braço que isola (2) de (3): **agente único, contexto completo, mas conjunto de ferramentas/prompt condicionado à intenção detectada**.
Sem esse braço, nenhum experimento — inclusive o do usuário — consegue dizer *por que* venceu quem venceu.

**(b) Ninguém trata falha assimétrica.** `[R]`
Em suporte bancário, errar "horário de funcionamento" e errar "bloqueio de cartão por fraude" não são o mesmo evento.
Todas as métricas consultadas são sucesso binário não ponderado por dano. Uma métrica de sucesso ponderada por severidade regulatória não aparece em nenhuma fonte.

**(c) Ninguém trata escalonamento correto como sucesso.** `[R]`
Em atendimento real, "reconheci que não sei e transferi para humano" é o comportamento certo, e a arquitetura multi-agente tem um lugar natural para isso (o supervisor).
Benchmarks tratam isso como falha ou o ignoram — o que pode estar *subestimando* sistematicamente o multi-agente na única dimensão em que ele teria vantagem estrutural.

**(d) Ninguém mede latência como restrição, só como custo.** `[R]`
Latência em atendimento tem limiar (abandono), não é linear. +1,5s pode ser irrelevante ou fatal dependendo de onde cai em relação ao limiar — e nenhuma fonte modela isso.

**(e) Ninguém mede o custo humano de manutenção.** `[R]`
O argumento mais forte do praticante (depurabilidade) não tem uma única medição publicada nas fontes consultadas.

---

### 2.6 Armadilhas metodológicas que derrubam experimentos deste tipo
*(esta subseção é a matéria-prima direta da seção "Ameaças à validade" do artigo)*

#### A. Comparação injusta entre braços (a mais letal, e a mais comum)

| # | Armadilha | Por que derruba | Controle |
|---|---|---|---|
| A1 | **Compute não igualado** | O braço multi-agente faz 3–5 chamadas ao LLM contra 1–2 do single. Se ele ganhar, você mediu orçamento, não arquitetura. É exatamente a crítica central de "Illusion of MAS Advantage" `[F]` e de Tran & Kiela `[F-sec]` | Reportar tokens e nº de chamadas por braço **como covariável**, e rodar um braço adicional de single-agent com self-consistency no mesmo orçamento do multi-agente |
| A2 | **Prompt de um braço mais trabalhado** | Você iterou meses no supervisor e escreveu o baseline single-agent em 20 minutos. O efeito medido é esforço de prompt engineering, não arquitetura. Nenhuma fonte consultada controla isso `[R]` | Congelar orçamento de iteração igual por braço (nº de rodadas de refino, mesmo conjunto de dev, mesmo autor), declarar isso no método, e versionar os dois prompts como anexo |
| A3 | **Ferramentas/RAG diferentes entre braços** | Se o especialista tem um retriever afinado e o single-agent usa o genérico, o braço não é "arquitetura" | Mesmo índice, mesmo `top_k`, mesmo embedder, mesmas descrições de ferramenta, mesmo prompt de sistema base |
| A4 | **Modelo base diferente** | Comparar líder forte + workers fracos contra single fraco confunde capacidade com topologia | Mesmo modelo, mesma quantização, mesmos parâmetros de decodificação em todos os papéis |

#### B. Dataset e poder estatístico

- **B1 — n pequeno demais.** Card et al. (EMNLP 2020, *With Little Power Comes Great Responsibility*): experimentos subdimensionados são a norma em NLP; a mediana de 100 itens em avaliações humanas já é insuficiente para detectar diferenças pequenas; o efeito colateral é que **as diferenças que aparecem como significativas ficam exageradas** (*effect size inflation*). `[F-sec]`
- **B2 — Cobertura de intent.** Com 9 intents e 15 casos, são ~1,7 casos por intent: impossível qualquer afirmação por intent, e uma única troca de resultado em um intent domina o total. `[R]`
- **B3 — Casos escolhidos pelo autor.** Se os casos vieram da sua cabeça, eles herdam o viés do sistema que você construiu. `[R]`
- **B4 — Ausência de casos adversariais/fora de distribuição.** Sem eles, você mede o caminho feliz — e é justamente fora do caminho feliz que MAS falha (MAST: erros de verificação e propagação de erro na cadeia) `[F-sec]`.

#### C. Estocasticidade não controlada

- **C1 — Uma execução por caso.** Sem repetição, você não distingue efeito de arquitetura de ruído de amostragem. τ-bench mostra o tamanho do problema: 60% → <25% quando se exige consistência em 8 tentativas `[F-sec]`.
- **C2 — Temperatura > 0 sem seed nem repetição.** `[R]`
- **C3 — Ausência de `pass^k`.** Reportar só a média esconde exatamente a propriedade que interessa em produção. `[F-sec]`
- **C4 — Usuário simulado por LLM também é estocástico.** Se o experimento tem multi-turno com usuário simulado, ele é uma segunda fonte de variância — τ-bench e τ²-bench existem por causa disso. `[F-sec]`

#### D. Juiz enviesado (LLM-as-judge)

- **D1 — Viés de posição:** trocar a ordem de apresentação em julgamento pareado desloca a acurácia em **>10 pontos** em julgamento de código. `[F-sec]`
- **D2 — Viés de verbosidade:** juízes preferem respostas longas/fluentes independentemente de substância. `[F-sec]` — **fatal aqui**, porque o braço multi-agente tende a produzir respostas mais longas e mais estruturadas (concatenação de especialistas + síntese do supervisor). O juiz pode estar premiando comprimento e você vai reportar como qualidade. `[R]`
- **D3 — Auto-preferência:** juízes reconhecem e preferem as próprias gerações, com correlação linear demonstrada entre auto-reconhecimento e auto-preferência (NeurIPS 2024, arXiv 2410.21819). `[F-sec]` — se o juiz for o mesmo modelo do sistema avaliado, o experimento está contaminado na raiz.
- **D4 — Concordância com humanos é modesta em domínio especializado:** 60–68% em domínios de expertise, subindo para >80% apenas quando calibrado e validado contra humanos. `[F-sec]` Domínio bancário é domínio especializado.
- **D5 — Viés posicional no verificador de MAS:** o próprio mecanismo de verificação interno do MAS escolhe a saída anterior em >45% dos casos. `[F]`

#### E. Hardware contaminando latência (crítico para RTX 3060 12 GB)

- **E1 — Troca de modelo na VRAM.** `[R, alta confiança]` Este é o confundidor mais perigoso e mais específico deste experimento. Se supervisor e especialistas forem instâncias/modelos distintos e não couberem juntos em 12 GB, cada handoff dispara descarregar/carregar peso ou offload para CPU. A latência medida vira **gestão de VRAM**, não arquitetura. Mitigação obrigatória: um único modelo base residente, especialistas = system prompts distintos sobre a mesma instância; e declarar isso explicitamente no método.
- **E2 — Cache de KV / prompt cache assimétrico.** Um braço reaproveita prefixo e o outro não → vantagem artificial. `[R]`
- **E3 — Warm-up e primeira execução.** Descartar rodadas de aquecimento; ordem de execução dos braços deve ser **intercalada ou randomizada**, nunca "todos do braço A, depois todos do braço B" (thermal throttling e estado de cache derivam ao longo do tempo). `[R]`
- **E4 — Ruído de máquina.** Processos de fundo, navegador, outro agente rodando. Registrar carga, temperatura de GPU e clocks; ou reportar mediana e p95 em vez de média.
- **E5 — Latência de rede zero é uma escolha, não neutralidade.** Rodando local, você elimina variância de rede — o que é bom para controle interno mas **limita a validade externa** para qualquer sistema em nuvem, onde o custo por handoff é maior. Declarar. `[R]`
- **E6 — "Custo" sem preço de token não é custo.** Rodando local, custo monetário direto ≈ 0. Ou você define custo como energia/tempo-de-GPU, ou você usa preços de tabela de um provedor como proxy e declara isso como estimativa contrafactual — misturar os dois é erro. `[R]`

#### F. Ameaças de validade de construto e externa

- **F1 — "Sucesso de tarefa" mal definido.** Precisa de rubrica escrita *antes* da coleta, com critérios verificáveis (a ação correta na ferramenta correta com os argumentos corretos), não julgamento holístico.
- **F2 — Generalização de um único chatbot, um único domínio, um único modelo.** Declarar como limitação; não escrever "arquiteturas multi-agente são/não são melhores", escrever "neste sistema, neste modelo, neste hardware".
- **F3 — Transplante de evidência entre domínios.** Usar o +90,2% da Anthropic (pesquisa breadth-first, contextos independentes) para motivar expectativa em atendimento (contexto compartilhado, dependências fortes) contradiz as contraindicações do próprio texto-fonte `[F]`.

---

## FASE 3 — Briefing de síntese

### 3.1 Resumo em um parágrafo (60 segundos, com nuance)

A área não discorda sobre os fatos, discorda sobre a atribuição causal.
Todo mundo concorda que sistemas supervisor+especialistas custam ~15× mais tokens que chat `[F]`, que a maior parte das suas falhas é de design e não de capacidade do modelo `[F-sec]`, e que o ganho depende da estrutura da tarefa.
A disputa é se o ganho observado vem da topologia ou simplesmente de gastar mais compute: quando o orçamento de tokens é igualado, o ganho encolhe ou inverte, e um agente único com self-consistency chega a vencer frameworks multi-agente automáticos com menos de 10% do custo `[F]`.
Pior para os proponentes, quando se inspeciona o mecanismo em vez do placar, os agentes concordam unanimemente e de imediato em ~70% (GPT-4o) a >90% (GPT-5) dos casos — o debate que justifica a arquitetura simplesmente não ocorre `[F]`.
Atendimento ao cliente é, pela lista do próprio proponente, o pior caso para MAS: contexto compartilhado obrigatório e dependências fortes entre passos `[F]`.
E há um agravante para modelos pequenos e quantizados: a quantização degrada especificamente a geração de tool call `[F-sec]`, que é exatamente o mecanismo pelo qual um supervisor roteia — ou seja, em hardware modesto a arquitetura multi-agente paga o custo onde é mais frágil.

### 3.2 Cinco achados-chave, ordenados por confiabilidade

**1. Multi-agente custa 3–15× mais em tokens/latência, sem disputa.**
Apoiam: Praticante, Acadêmico, Cético, Economista. Desafia: ninguém.
Base: 15× vs chat `[F]`; CrewAI ~3× tokens e ~3× tempo vs LangChain para uma tool call `[F-sec]`; roteamento de supervisor >30% do tempo de resposta em LangGraph `[F-sec]`.

**2. Boa parte do ganho reportado de MAS é compute não contabilizado.**
Apoiam: Acadêmico, Cético, Economista. Desafia: Praticante.
Base: "Illusion of MAS Advantage" (CoT-SC vence a <10% do custo) `[F]`; Tran & Kiela com thinking-token budget igual `[F-sec]`; e o próprio dado de que tokens explicam ~80% da variância `[F]`.

**3. As falhas de MAS são majoritariamente de design e não se resolvem com modelo maior.**
Apoiam: Acadêmico, Cético, Praticante (parcialmente). Desafia: ninguém frontalmente.
Base: MAST, 14 modos de falha, 41,8% em design de sistema, κ=0,88 `[F-sec]`; princípios da Cognition `[F]`.

**4. Desempenho de tentativa única superestima grosseiramente a confiabilidade em atendimento.**
Apoiam: Acadêmico, Historiador, Economista. Desafia: ninguém.
Base: τ-bench, `pass^1 ≈ 60%` → `pass^8 < 25%` no varejo `[F-sec]`.

**5. Em modelos pequenos/quantizados, a vantagem multi-agente é improvável e pode ser negativa.**
Apoiam: Acadêmico, Cético. Desafia: Praticante (argumenta que menos ferramentas por agente compensa).
Base: MAS só teve sucesso sobre modelos fortes `[F]`; quantização degrada tool call especificamente `[F-sec]`; colapso de multi-turn na BFCL (Qwen3-4B 62,04% → 35,25%) `[F-sec]`.
Este é o achado menos consolidado e o mais decisivo para o experimento — ver Fase 4.

### 3.3 Conexão escondida (só visível cruzando as 5 vozes)

O Praticante defende multi-agente por **depurabilidade**; o Acadêmico ataca multi-agente por **41,8% de falhas de design**; o Historiador observa que o que sobreviveu do blackboard foi o **estado compartilhado**, não a sociedade de agentes.
Cruzando os três: multi-agente é, na prática, um *substituto artesanal para observabilidade ausente*. `[R]`
Você não está comprando inteligência coletiva — está comprando *fronteiras nomeadas* que tornam o log legível, e pagando por isso em tokens, latência e 14 novos modos de falha.
Consequência prática: se você instrumentar bem o agente único (tracing por passo, log estruturado de cada tool call, rótulo de intent na trace), você captura o benefício real do multi-agente sem pagar o custo.
Isso reformula o debate inteiro de "qual arquitetura é mais inteligente" para "qual arquitetura é mais observável, e observabilidade pode ser obtida mais barato".

### 3.4 Insight acionável (para o estudante com este experimento específico)

**Mudança 1 — Reformule a pergunta de pesquisa para uma que seu experimento consegue responder.**
"Multi-agente compensa?" é grande demais para 15 casos e para uma RTX 3060.
Troque por: *"Sob orçamento de compute controlado e mesmo modelo base, o supervisor+especialistas melhora o sucesso de tarefa em relação ao agente único com tool calling, neste domínio de suporte bancário com 9 intents?"*
Isso é defensável, é a pergunta em aberto da área (§2.3) e é honesto quanto ao escopo.

**Mudança 2 — Rode 3 braços, não 2.** *(o mais importante, e o que diferencia o artigo)*
- **A**: agente único, todas as ferramentas visíveis, prompt único.
- **B**: supervisor + especialistas (seu sistema atual).
- **C**: agente único, **contexto completo**, mas com o conjunto de ferramentas e a instrução de política **condicionados ao intent detectado** (roteamento sem handoff).
O braço C custa pouco para implementar e isola a variável que a área inteira confunde (§2.5a): se C ≈ B, o ganho era de *escopo de ferramenta*, não de arquitetura multi-agente — e esse é um resultado publicável e original em escala de graduação.
Opcionalmente um braço **A+SC** (agente único com self-consistency no mesmo orçamento de tokens de B) para atacar a Contradição 1 diretamente.

**Mudança 3 — Corrija o n antes de rodar, não depois.**
Com 15 casos pareados e teste de McNemar exato, o **mínimo detectável** é 6 pares discordantes todos na mesma direção (p = 2×0,5⁶ ≈ 0,031); com 5 pares, p ≈ 0,0625 e não dá significância. `[R, cálculo padrão]`
Traduzindo: com 15 casos você só detecta uma diferença absoluta de **~40 pontos percentuais**. Nada abaixo disso é detectável, e a área discute diferenças de 4–6pp `[F]`.
Além disso, 12/15 = 80% tem IC 95% (Wilson) ≈ **[55%, 98%]** — uma barra de erro de 43 pontos. `[R, cálculo]`
Para detectar 15pp com 80% de poder em desenho pareado, a ordem de grandeza é **~100 casos pareados** (assumindo ~30% de discordância). `[R, fórmula de McNemar]`
Caminho realista sem inflar o dataset: **15 cenários × k repetições (k ≥ 5)**, reportando média por cenário e `pass^k`, com o cenário como unidade de análise e efeito aleatório de repetição — assim você compra poder em cima da estocasticidade em vez de fingir que ela não existe.
Se n grande for inviável, declare o estudo como **exploratório/piloto**, reporte intervalos de confiança em vez de p-valores, e faça disso uma escolha metodológica explícita — banca perdoa piloto assumido, não perdoa piloto disfarçado de confirmatório.

**Mudança 4 — Valide o juiz, com números.**
Anote **você mesmo** um subconjunto (mínimo ~30–50 respostas, estratificado por intent e por braço), calcule **Cohen's κ** entre você e o juiz, e reporte esse κ na metodologia.
Estudos de validação relatam κ na faixa de ~0,73–0,75 quando o processo é bom `[F-sec]`; concordância de 60–68% em domínio especializado é o cenário realista sem calibração `[F-sec]`.
Controles mínimos: (i) juiz **diferente** do modelo avaliado (evita auto-preferência `[F-sec]`); (ii) **randomizar a ordem** e/ou rodar nas duas ordens e reportar a discordância (viés de posição `[F-sec]`); (iii) **cegar o juiz** quanto ao braço — remover marcadores de "supervisor"/"especialista" do texto; (iv) **normalizar comprimento** ou reportar comprimento médio por braço como covariável, para desarmar o viés de verbosidade `[F-sec]`; (v) rubrica binária e verificável (ferramenta certa + argumentos certos + política respeitada) em vez de nota holística de 1–5.
Se quiser um degrau extra de rigor, cite Prediction-Powered Inference / PPI, que combina um pequeno conjunto anotado por humano com um grande conjunto julgado por LLM produzindo estimativa **não enviesada independentemente do perfil de erro do juiz** `[F-sec]` — mencionar isso na seção de método sinaliza maturidade metodológica mesmo que você use a versão simples (κ + subconjunto humano).

**Mudança 5 — Blinde a latência do hardware.**
Um único modelo base residente em VRAM; especialistas = system prompts sobre a mesma instância; declarar isso no método (§E1).
Intercalar a ordem dos braços, descartar warm-up, reportar **mediana e p95** além da média, registrar tokens de entrada/saída e nº de chamadas ao modelo por caso.
Custo: como você roda local, defina custo explicitamente (energia ou tempo-de-GPU) **ou** apresente uma estimativa contrafactual com preços de tabela, rotulada como tal.

**Mudança 6 — Escreva a seção de ameaças à validade a partir de §2.6.**
Ela é, em artigos de graduação, a seção que mais diferencia um trabalho bom de um trabalho aceitável — e a que a banca mais usa para calibrar se o autor entende o que fez.
Ordem sugerida: validade interna (A, C, E) → validade de construto (D, F1) → validade externa (F2, F3) → poder estatístico (B).

**Mudança 7 — Prepare-se para (e valorize) um resultado nulo ou negativo.**
Dado o Clash 3 (§2.1), a hipótese mais provável neste hardware é que multi-agente **não** ganhe, ou ganhe pouco a custo alto.
Enquadre isso desde a introdução como *hipótese de trabalho*, não como decepção: "verificar se o ganho reportado na literatura se sustenta em hardware de consumo com modelo quantizado" é uma pergunta legítima de replicação sob restrição — e a área precisa dessa resposta.

### 3.5 Pergunta de fronteira

**Quanto do ganho atribuído a arquiteturas multi-agente é explicado por três variáveis separáveis — compute adicional, redução do conjunto de ferramentas por chamada, e isolamento de contexto — quando cada uma é manipulada independentemente?**
Nenhum trabalho consultado faz esse desenho fatorial. `[R]`
Se a resposta for "compute + escopo de ferramentas explicam quase tudo", a topologia multi-agente é um artefato de engenharia e não um resultado arquitetural, e o campo inteiro precisa reescrever suas justificativas.

---

## FASE 4 — Peer review (autocrítica deste briefing)

### 4.1 Notas de confiança dos 5 achados (1–10)

| # | Achado | Nota | Justificativa |
|---|---|---|---|
| 1 | Multi-agente custa 3–15× mais | **9/10** | Confirmado por proponentes e opositores; números vêm do lado que tem incentivo em minimizá-los. Perde 1 ponto porque a razão exata depende fortemente de framework e de tarefa. |
| 2 | Boa parte do ganho é compute não contabilizado | **8/10** | Dois trabalhos independentes com controle explícito de orçamento, mais o mecanismo (colapso de consenso) verificado. Perde pontos porque ambos avaliam raciocínio/QA, não atendimento multi-turno com ferramentas, e porque um deles é muito recente (baixa exposição a replicação). |
| 3 | Falhas são de design, não de capacidade | **8/10** | Taxonomia com validação de anotação (κ=0,88) e n grande (1.600+ traces). Perde pontos porque a atribuição "design vs capacidade" é ela própria um julgamento de anotador. |
| 4 | pass^1 superestima confiabilidade | **9/10** | Métrica objetiva, benchmark aceito em conferência de primeira linha, domínio idêntico ao do usuário (atendimento). |
| 5 | Multi-agente é improvável/negativo em modelo pequeno quantizado | **5/10** | **O elo mais fraco.** É uma cadeia de três inferências, não uma medição direta — ver §4.2. |

### 4.2 Elo mais fraco

**Achado 5.**
A cadeia é: (i) quantização degrada tool call `[F-sec]` → (ii) supervisor roteia via tool call `[R]` → (iii) logo multi-agente sofre desproporcionalmente em hardware pequeno `[R]`.
O passo (i) vem de fonte secundária com números de contexto diferente (NVFP4 em modelos <30B), o passo (ii) é verdadeiro apenas se a implementação do usuário usar tool call para o handoff (LangGraph também permite roteamento por saída estruturada ou por classificador dedicado), e o passo (iii) nunca foi medido diretamente em nenhuma fonte consultada.
**O que verificaria:** exatamente o experimento do usuário, se ele instrumentar a taxa de acerto de *roteamento do supervisor* isoladamente (o supervisor escolheu o especialista correto?) como métrica intermediária, separada do sucesso final da tarefa.
Isso transforma a maior fraqueza deste briefing na contribuição mais original do artigo — porque preenche uma lacuna real da literatura consultada. Recomendação forte: adotar "acurácia de roteamento" como desfecho secundário adicional.

**Fragilidades secundárias declaradas:**
- Vários números vieram de sínteses de busca (`[F-sec]`) e não do PDF original. Antes de citar em ABNT, abrir o primário e conferir: MAST (arXiv 2503.13657), τ-bench (ICLR 2025), Tran & Kiela, Card et al. (EMNLP 2020), self-preference bias (arXiv 2410.21819).
- Os números de LangGraph supervisor (>30% do tempo, −40% com swarm) e de CrewAI (3× tokens) vêm de posts de engenharia/comparativos, não de papers revisados. Usar como ilustração, nunca como evidência central.
- Gartner e MIT são consultoria: motivação, não resultado.

### 4.3 Checagem de viés

**Voz superrepresentada: o Cético**, com o Acadêmico como cúmplice.
As fases 2 e 3 pendem claramente para "multi-agente provavelmente não compensa neste caso".
Parte disso é justificável (a evidência com controle de compute realmente está desse lado, e o pedido do usuário enfatizava explicitamente controvérsia e autocrítica), mas parte é viés de seleção: buscas por "por que MAS falha" retornam literatura crítica, e literatura crítica é mais publicável quando o hype é alto.

**Correções devidas ao lado pró-multi-agente, que este briefing subrepresentou:**
1. O caso favorável ao MAS é **real e reprodutível quando a tarefa tem estrutura decomponível**: no próprio "Illusion of MAS Advantage", no benchmark SMFR desenhado para exigir decomposição, o GPT-5 fez **57% com CoT-SC contra 96,5% com Expert-MAS** `[F]`. Ou seja, o paper mais crítico ao MAS contém a evidência mais forte a favor dele — quando a tarefa é a certa. O que ele nega é o valor dos frameworks *automáticos* de MAS, não do MAS bem desenhado à mão. **Este briefing quase deixou passar esse ponto, e ele é decisivo.**
2. Nove intents distintos em suporte bancário *são* uma estrutura decomponível conhecida a priori — o que coloca o caso do usuário mais perto do cenário favorável (Expert-MAS com decomposição dada) do que o tom geral deste documento sugere.
3. O argumento de depurabilidade do Praticante foi rebaixado por falta de medição, mas "não medido" não é "falso" — é uma lacuna da literatura, e o briefing o tratou como fraqueza da posição.

**Efeito líquido:** a hipótese do usuário (multi-agente ajuda) é mais defensável do que as fases 2–3 fazem parecer. O artigo não deve abrir assumindo derrota.

### 4.4 Perspectiva ausente (a 6ª voz que mudaria conclusões)

**O regulador / oficial de compliance bancário.**
Nenhuma das 5 vozes tratou de auditabilidade obrigatória, rastreabilidade de decisão, explicabilidade exigida por norma, ou responsabilidade por resposta errada em serviço financeiro.
Sob essa ótica, o cálculo inverte: uma arquitetura em que cada decisão tem um agente nomeado, um trace separado e uma fronteira de política explícita pode ser **exigida** independentemente de acurácia, latência ou custo.
Multi-agente deixaria de ser uma escolha de otimização e passaria a ser um requisito não funcional — e todo o debate "compensa?" viraria irrelevante.
Para o artigo, isso rende dois parágrafos fortes em "trabalhos futuros" e uma limitação honesta: o experimento otimiza sucesso/latência/custo, e não mede conformidade, auditabilidade ou responsabilização.

**Segunda voz ausente, menor: o usuário final.** Nenhuma perspectiva mediu satisfação percebida; o caso Klarna sugere que ela pode divergir das métricas técnicas `[F-sec]`.

### 4.5 Nota geral e a crítica que a banca vai fazer

**Nota deste briefing: B+.**
Forte em mapear a controvérsia com fontes dos dois lados, em identificar o confundidor central (compute vs topologia) e em derivar ameaças à validade acionáveis.
Perde nota por: dependência de fontes secundárias em vários números-chave; viés cético não corrigido até a §4.3; e por não ter procurado ativamente por trabalhos que comparem arquiteturas **especificamente em atendimento ao cliente multi-turno** — a lacuna mais próxima do experimento do usuário.
**Para chegar a A:** abrir os 5 primários listados em §4.2, e rodar uma busca dedicada a "MAS vs single-agent em customer support / task-oriented dialogue", que este documento não cobriu.

---

### 4.6 A crítica de banca a um experimento com 15 casos e LLM-as-judge sem validação humana
*(pedido explícito — escrito como a banca falaria, para o autor poder responder antes de ouvir)*

**Ataque 1 — Poder estatístico. O mais provável e o mais difícil de responder.**
"Com 15 casos, qual diferença mínima o seu desenho consegue detectar? Você fez análise de poder antes de coletar?"
Resposta necessária: McNemar exato exige ≥6 pares discordantes na mesma direção para p<0,05 → detectabilidade mínima ~40pp; e 12/15 tem IC 95% de ~[55%, 98%] `[R, cálculos]`.
Se a resposta for "não fiz", a banca conclui que qualquer diferença reportada é ou ruído ou efeito inflado — e Card et al. (2020) é a citação que ela vai usar contra você `[F-sec]`.
**Defesa possível:** assumir o estudo como piloto exploratório, reportar ICs e não p-valores, e usar repetições (k≥5) por cenário para recuperar poder.

**Ataque 2 — Validade do instrumento de medida.**
"Seu juiz é um LLM. Qual a concordância dele com um anotador humano? Você calculou κ? Em quantos itens?"
Sem número, o desfecho primário do artigo não tem instrumento validado — é o equivalente a publicar medições com uma balança nunca aferida.
A banca pode encerrar por aqui: *nenhuma conclusão sobre qualidade é sustentável*.
**Defesa possível:** subconjunto anotado por você (30–50 itens estratificados) + κ reportado + declaração de que κ na faixa 0,73–0,75 é o esperado em processos bem construídos `[F-sec]`.

**Ataque 3 — O juiz favorece o braço que produz mais texto.**
"O braço multi-agente gera respostas mais longas. Você controlou verbosidade? Cegou o juiz quanto ao braço? Randomizou a ordem?"
Viés de verbosidade e de posição são documentados, e o de posição chega a deslocar acurácia em >10pp `[F-sec]`.
Sem cegamento e randomização, a diferença medida pode ser inteiramente artefato do juiz.
**Defesa possível:** cegamento, dupla ordem, comprimento como covariável reportada.

**Ataque 4 — Auto-preferência.**
"O juiz é o mesmo modelo que gera as respostas?"
Se sim, há correlação demonstrada entre auto-reconhecimento e auto-preferência `[F-sec]` e o resultado é inutilizável.
**Defesa:** juiz de família diferente, declarado.

**Ataque 5 — Comparação justa entre braços.**
"Quanto tempo você passou refinando cada prompt? Os dois braços tiveram o mesmo orçamento de engenharia? O mesmo modelo, a mesma quantização, o mesmo RAG?"
Esta é a pergunta que mais frequentemente derruba a conclusão sem derrubar os dados — e o autor quase nunca tem a resposta documentada.
**Defesa:** protocolo de esforço igual declarado no método, prompts em anexo, mesmo índice/retriever/parâmetros.

**Ataque 6 — Compute confundido com arquitetura.**
"O braço multi-agente gastou 3× mais tokens. Você comparou contra um agente único usando o mesmo orçamento?"
É a crítica central da literatura de 2025–2026 `[F]` e não tem resposta se o braço não foi rodado.
**Defesa:** o braço A+SC (§3.4).

**Ataque 7 — Estocasticidade.**
"Quantas execuções por caso? Qual a temperatura? Qual o desvio-padrão? Você reportou pass^k?"
Uma execução por caso com temperatura > 0 significa que o experimento não é reproduzível nem por você mesmo. τ-bench é a citação que a banca vai usar `[F-sec]`.

**Ataque 8 — Cobertura e origem dos casos.**
"Com 9 intents e 15 casos, o que você pode afirmar sobre qualquer intent individual? Quem escreveu os casos? Há casos adversariais ou fora de distribuição?"
Resposta honesta: nada por intent; e se os casos são de autoria própria, há viés de construção a declarar.

**Ataque 9 — Latência em hardware compartilhado.**
"Os dois braços rodaram na mesma GPU, na mesma sessão, com o mesmo modelo residente? Houve recarga de modelo entre agentes? Você reportou p95 ou só média?"
Sem isso, a latência mede gestão de VRAM (§E1).

**Ataque 10 — Validade externa.**
"Isso vale para outro modelo, outro domínio, outra GPU?"
Resposta correta é "não sabemos", declarada na seção de limitações — e essa resposta, dada espontaneamente, costuma desarmar a pergunta.

**Leitura estratégica.** `[R]`
Uma banca de graduação raramente reprova por resultado fraco; reprova por **conclusão mais forte que o desenho**.
O artigo fica seguro se cada afirmação do abstract e da conclusão for enunciada dentro do escopo que 15–75 execuções em um único sistema sustentam, e se a seção de ameaças à validade **listar esses 10 ataques antes que a banca os faça**.
Antecipar a crítica converte cada uma dessas fraquezas de "erro do autor" em "limitação reconhecida" — que é a diferença entre nota baixa e nota alta com o mesmo experimento.

---

## Apêndice — Fontes consultadas nesta sessão

Primárias verificadas por fetch:
- Anthropic Engineering — *How we built our multi-agent research system*: https://www.anthropic.com/engineering/multi-agent-research-system
- Cognition — *Don't Build Multi-Agents* (Walden Yan): https://cognition.com/blog/dont-build-multi-agents
- *The Illusion of Multi-Agent Advantage*, arXiv 2606.13003: https://arxiv.org/html/2606.13003v2

Recuperadas via busca (abrir o primário antes de citar em ABNT):
- Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), arXiv 2503.13657 / NeurIPS 2025 D&B: https://arxiv.org/abs/2503.13657
- Yao et al., *τ-bench*, ICLR 2025: https://openreview.net/forum?id=roNSXZpUDN
- *τ²-Bench*, arXiv 2506.07982: https://arxiv.org/pdf/2506.07982
- Tran & Kiela, *Single-Agent LLMs Outperform Multi-Agent Systems... Under Equal Thinking Token Budgets*
- Card et al., *With Little Power Comes Great Responsibility*, EMNLP 2020: https://arxiv.org/pdf/2010.06595
- *Self-Preference Bias in LLM-as-a-Judge*, arXiv 2410.21819: https://arxiv.org/pdf/2410.21819
- *Validating LLM-as-a-Judge Systems under Rating Indeterminacy*, arXiv 2503.05965: https://arxiv.org/pdf/2503.05965
- *Statistically Reliable LLM-Based Ranking Evaluation via Prediction-Powered Inference*, arXiv 2606.05308: https://arxiv.org/abs/2606.05308
- *Noisy but Valid: Robust Statistical Evaluation of LLMs with Imperfect Judges*, arXiv 2601.20913: https://arxiv.org/pdf/2601.20913
- Cognition — *Multi-Agents: What's Actually Working*: https://cognition.com/blog/multi-agents-working
- Gartner (25/06/2025) — >40% dos projetos de IA agêntica cancelados até 2027: https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027
- *Exploring Advanced LLM Multi-Agent Systems Based on Blackboard Architecture*, arXiv 2507.01701: https://arxiv.org/html/2507.01701v1
- LangGraph supervisor vs swarm (overhead de roteamento): https://focused.io/lab/multi-agent-orchestration-in-langgraph-supervisor-vs-swarm-tradeoffs-and-architecture
- Klarna — reversão parcial da automação de atendimento (mai/2025): https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/
