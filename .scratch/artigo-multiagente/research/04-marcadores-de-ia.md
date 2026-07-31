# 04 — Marcadores linguísticos de texto gerado por IA, em português acadêmico

**Pergunta.**
Quais palavras, construções e padrões estruturais denunciam texto gerado por modelo de linguagem em português acadêmico, e qual a alternativa correta para cada um?

**Uso pretendido.**
Documento de consulta para reescrever, na voz do autor, um artigo de 5–7 páginas em ABNT rascunhado com apoio de agente.
Não é lista de proibições estéticas: cada linha das tabelas traz a evidência que a sustenta, e quando não há evidência isso está escrito.

---

## Legenda de ancoragem

Use a marcação de cada afirmação antes de repassá-la ao artigo.

- `[F]` — **fato documentado**, ancorado em estudo revisado por pares ou documento normativo primário consultado nesta pesquisa.
- `[F-pre]` — ancorado em **preprint** (arXiv/SciELO Preprints), sem revisão por pares até onde foi verificado.
- `[F-inst]` — ancorado em **documento institucional oficial** (política de editora, guia de periódico, norma técnica).
- `[F-vendor]` — número medido, mas por **fornecedor comercial de detector**, sem metodologia publicada nem revisão por pares. Vale como indício, nunca como evidência.
- `[OP]` — **opinião**, incluindo opinião de especialista identificado. Não é medição.
- `[INF]` — **inferência minha**, derivada de um `[F]` mas não medida diretamente. Toda a tabela de vocabulário em português cai aqui, pelo motivo explicado na seção 2.
- `[X]` — **procurado e não encontrado**. Resultado válido e importante: significa que a afirmação circula sem base verificável.

---

## 1. Resumo executivo — os 10 marcadores mais fortes em português

Ordenados por força da evidência, não por frequência percebida.

| # | Marcador | Força da evidência |
|---|---|---|
| 1 | Verbos e adjetivos de *estilo* super-representados: `crucial`, `fundamental`, `abrangente`, `robusto`, `significativo`, `aprofundar-se em`, `destacar`, `ressaltar`, `evidenciar` sem número ao lado | `[F]` para o inglês (Kobak et al., 2025); `[INF]` para o português |
| 2 | **Densidade nominal**: nominalizações no lugar de verbos (`a realização da análise` em vez de `analisamos`) | `[F]` — 1,5–2× a taxa humana (Reinhart et al., PNAS 2025); 1,06 → 1,73 (Herbold et al., 2023) |
| 3 | **Orações reduzidas de gerúndio/particípio** empilhadas no fim da frase (`…, demonstrando a importância de…`) | `[F]` — 2–5× a taxa humana (Reinhart et al., PNAS 2025) |
| 4 | **Adjetivação avaliativa sem número ao lado** (`resultados robustos`, `análise abrangente`, `ganho significativo` sem p-valor) | `[F]` parcial — 66% das *excess words* de 2024 são verbos e 14% adjetivos, isto é, palavras de estilo e não de conteúdo (Kobak et al., 2025); `[F]` para a prescrição em português (Yoshida, 2006) |
| 5 | **Frase-resumo de fechamento** que repete o que acabou de ser dito (`Em conclusão, …`) | `[F]` — ChatGPT produziu conclusão com abertura idêntica em todos os ensaios do corpus (Herbold et al., 2023) |
| 6 | **Ausência de marcador epistêmico**: o texto nunca hesita, nunca admite limite | `[F]` — marcadores epistêmicos: 0,06 (humano) → 0,00 (ChatGPT-4) (Herbold et al., 2023) |
| 7 | **Uniformidade**: parágrafos de tamanho parecido, frases de comprimento parecido, seções de peso parecido | `[F]` parcial — "LLMs struggle to match human stylistic variation" (Reinhart et al., PNAS 2025); densidade lexical uniforme entre níveis (Silva & Rottava, 2024) |
| 8 | **Negrito disperso, bullets e cabeçalhos onde o gênero pede prosa** | `[F-vendor]` — negrito 43× acima do baseline humano (Pangram); `[F-pre]` — some por completo quando se instrui "sem formatação" (Freeburg, 2026) |
| 9 | **Travessão longo no estilo americano** (`palavra—palavra`, sem espaços), em texto que deveria usar vírgula, parênteses ou dois-pontos | `[F-pre]` + `[OP]` — frequência relativa mais que dobrou em abstracts de ecologia 2021→2025 (Keck, 2025, dados abertos, não revisado); baseline humano se sobrepõe ao de vários modelos |
| 10 | **Antítese vazia** `não apenas X, mas também Y` / `não se trata de X, e sim de Y` | `[F-vendor]` — 3× o baseline humano (Pangram); `[X]` para estudo revisado por pares |

Os itens 1 a 7 sobrevivem a escrutínio.
Os itens 8 a 10 são reais, mas a evidência é fraca — não reescreva um parágrafo bom só por causa deles.

---

## 2. Estado da evidência: existe estudo em português? Não.

**A resposta honesta, e ela importa mais que qualquer lista.**

Procurei, em português e em inglês, por um estudo que replicasse em corpus acadêmico lusófono a metodologia de *excess vocabulary* (Kobak) ou de estimativa de fração modificada por LLM em nível de corpus (Liang), comparando frequências antes e depois de 2023 em abstracts do SciELO, de periódicos brasileiros ou portugueses.

**`[X]` Nenhum estudo desse tipo foi encontrado, em português.**
Também não foi encontrado equivalente em espanhol, francês ou alemão.
A literatura de deriva lexical por LLM é, até onde esta pesquisa alcançou, essencialmente monolíngue-inglesa: PubMed, arXiv e Scopus em inglês.

O que existe em português é **adjacente, não equivalente**:

| Trabalho | O que mede | O que **não** mede |
|---|---|---|
| Candido, Barbosa, Martins & Costa (2025), WICS/SBC, DOI [10.5753/wics.2025.8692](https://sol.sbc.org.br/index.php/wics/article/view/35937) — 50 manuscritos, 5 detectores, 3 modelos `[F]` | desempenho de **detectores** sobre texto científico em português | frequência de palavras em corpus real publicado |
| Silva & Rottava (2024), *Texto Livre* 17, DOI [10.1590/1983-3652.2024.47836](https://www.scielo.br/j/tl/a/crx3yywCw3LSxtjtdv44mDC/) — 2.991 textos, 706.401 palavras, 5 línguas incluindo português `[F]` | densidade lexical de textos **gerados** pelo ChatGPT em português (50,83% no A1, 54,31% no A2), praticamente uniforme entre níveis CEFR | deriva no corpus acadêmico publicado |
| MULTITuDE — Macko et al., EMNLP 2023, [aclanthology.org/2023.emnlp-main.616](https://aclanthology.org/2023.emnlp-main.616/) — 74.081 textos, 11 línguas, **português incluído** `[F]` | detecção multilíngue em texto **jornalístico** | texto acadêmico em português |
| M4GT-Bench (ACL 2024) e SemEval-2024 Task 8 — 9 línguas | detecção multilíngue | **português está ausente** dessas duas |

**Consequência prática para o artigo.**
Toda lista de "palavras que denunciam IA em português" que circula na internet — inclusive a deste documento — é **inferência sobre um resultado medido em inglês**, não medição em português.
Se o artigo precisar afirmar algo sobre português, a formulação defensável é: *"não há, até onde localizamos, estudo de deriva lexical em corpus acadêmico em português; os achados disponíveis são anglófonos"*.
Isso é uma contribuição, não uma lacuna embaraçosa.

### O que foi medido, em inglês

- **Kobak, González-Márquez, Horvát & Lause (2025)**, *Science Advances* 11(27), DOI [10.1126/sciadv.adt3813](https://www.science.org/doi/10.1126/sciadv.adt3813), preprint [arXiv:2406.07016](https://arxiv.org/abs/2406.07016), código em [berenslab/llm-excess-vocab](https://github.com/berenslab/llm-excess-vocab). `[F]`
  Mais de 15 milhões de abstracts do PubMed, 2010–2024.
  Método análogo ao de *excesso de mortalidade*: a frequência esperada para 2024 é extrapolada de 2021–2022, e comparada à observada. Não usa detector nem corpus rotulado.
  Estimativa: **pelo menos 13,5% dos abstracts de 2024** foram processados com LLM, "chegando a 40% em alguns subcorpora".
  Palavras com maior razão de frequência em 2024: `delves` (r ≈ 28 na versão mais recente do preprint; r = 25,2 na v1), `underscores`, `showcasing`.
  Maior *gap* absoluto: `potential`, `findings`, `crucial`.
  **O achado estrutural é mais útil que a lista**: em 2024 as palavras em excesso são majoritariamente **verbos (66%) e adjetivos (14%)** — palavras de *estilo*; nos picos anteriores (COVID, zika, ebola) eram majoritariamente **substantivos** — palavras de *conteúdo*.
  Ou seja: o rastro do LLM aparece em **como** se diz, não em **o que** se diz.
  *Atenção ao citar*: os valores numéricos exatos diferem entre versões do preprint e a versão publicada. Cite a versão que você efetivamente consultar.

- **Liang, Izzo, Zhang, Lepp, Cao et al. (2024)**, ICML 2024, [arXiv:2403.07183](https://arxiv.org/abs/2403.07183). `[F]`
  Pareceres de conferências de IA. Fração do texto substancialmente modificada por LLM: **EMNLP 2023 = 16,9%**, ICLR 2024 = 10,6%, NeurIPS 2023 = 9,1%, CoRL 2023 = 6,5%. Controle pré-ChatGPT: NeurIPS 2022 = 1,9%.
  Adjetivos com maior salto de probabilidade: `meticulous` 34,7×, `intricate` 11,2×, `commendable` 9,8×.

- **Bao, Zhao, Mao & Zhang (2025)**, *Scientometrics*, preprint [arXiv:2505.12218](https://arxiv.org/abs/2505.12218). `[F]`
  823.798 abstracts do arXiv. Depois do ChatGPT: **sobem** as palavras preferidas por LLM, a complexidade lexical e o sentimento; **caem** a complexidade sintática, a coesão e a legibilidade.
  Achado diretamente relevante para um autor brasileiro: **a adoção é maior entre autores com menor proficiência em inglês**.

- **Reinhart, Markey, Laudenbach, Pantusen, Yurko, Weinberg & Brown (2025)**, *PNAS* 122, e2422455122, preprint [arXiv:2410.16107](https://arxiv.org/abs/2410.16107). `[F]`
  Corpora paralelos humano/LLM, 66 features do tagset de Biber.
  Super-usado por LLM: orações participiais presentes **2–5×**; nominalizações **1,5–2×**; orações `that` em posição de sujeito **2,6×**; coordenação frasal **1,9×**.
  Sub-usado: **voz passiva sem agente ≈ 50% da taxa humana**; *downtoners*.
  Conclusão dos autores: o *instruction tuning* treina os modelos num estilo "informacionalmente denso, pesado em substantivos".
  *Os multiplicadores acima vêm do texto completo na versão arXiv; o resumo do PNAS não os traz.*

- **Herbold, Hautli-Janisz, Heuer et al. (2023)**, *Scientific Reports* 13:18617, DOI [10.1038/s41598-023-45644-9](https://pmc.ncbi.nlm.nih.gov/articles/PMC10616290/). `[F]`
  270 redações, 111 professores, 658 avaliações.

  | Feature | Humano | ChatGPT-3.5 | ChatGPT-4 |
  |---|---|---|---|
  | Palavras por sentença | 18,60 | 20,31 | 19,57 |
  | Nominalizações | 1,06 | 1,56 | **1,73** |
  | Marcadores epistêmicos | 0,06 | 0,02 | **0,00** |
  | Marcadores discursivos / conectivos | **0,57** | 0,52 | **0,36** |
  | Diversidade lexical (MTLD) | 95,72 | 75,68 | **108,91** |

  Duas linhas dessa tabela derrubam crenças muito difundidas. Veja a seção 8 (Mitos).

---

## 3. Tabela A — Vocabulário

**Aviso obrigatório.** A coluna "Evidência" separa o que foi medido do que é transposição.
Nenhuma palavra em português desta tabela foi medida em corpus acadêmico lusófono — ver seção 2.

| Evite | Por quê | Coloque no lugar | Evidência |
|---|---|---|---|
| `crucial`, `fundamental`, `essencial`, `imprescindível` (como adjetivo avaliativo) | `crucial` é uma das três palavras com maior *gap* absoluto de frequência em abstracts de 2024; é a palavra que o LLM mais usa para dizer "isto importa" sem dizer por quê | diga **por que** importa, ou corte: `a latência determina se o usuário abandona a sessão` | `[F]` Kobak et al. 2025 (inglês) · `[OP]` Sabbatini, 2024, aponta `crucial` como a palavra que mais chama atenção em português |
| `aprofundar-se em`, `mergulhar em`, `explorar a fundo` | tradução direta de `delve`, a palavra com maior razão de excesso em 2024 (r ≈ 28 — entre `ebola` em 2015 e `zika` em 2017 em magnitude) | `analisamos`, `medimos`, `comparamos` — o verbo que descreve o que você de fato fez | `[F]` Kobak et al. 2025 · `[INF]` para o português |
| `robusto`, `abrangente`, `significativo` sem número ao lado | adjetivos de estilo, não de conteúdo; `significativo` sem p-valor é ambíguo entre o sentido estatístico e o coloquial | `robusto` → `o resultado se mantém nos três seeds`; `abrangente` → `cobre 9 dos 9 intents`; `significativo` → `p = 0,03` ou `+12 pontos percentuais` | `[F]` 66% das *excess words* de 2024 são verbos, 14% adjetivos, contra 79,2% substantivos no pico COVID (Kobak et al. 2025) · `[F]` Yoshida (2006) prescreve evitar "excesso de verborragia, rebuscamento, erudição e gongorismo" |
| `meticuloso`, `criterioso`, `louvável`, `notável` | `meticulous` 34,7×, `commendable` 9,8×, `intricate` 11,2× em pareceres pós-ChatGPT | descreva o procedimento: `cada trace foi anotado por dois avaliadores (κ = 0,88)` | `[F]` Liang et al., ICML 2024 (inglês) · `[INF]` para o português |
| `intrincado`, `multifacetado`, `dinâmico`, `inovador`, `transformador`, `disruptivo`, `poderoso`, `envolvente`, `fascinante` | família de adjetivos genéricos que não restringem nada: qualquer objeto pode receber qualquer um deles | corte o adjetivo e mantenha o substantivo, ou substitua por um fato | `[OP]` Sabbatini (UFPE), 2024 · `[F]` parcial via Kobak et al. 2025 para `intricate` |
| `destacar`, `ressaltar`, `evidenciar`, `sublinhar` como verbo de arremate (`o que ressalta a importância de…`) | tradução de `underscores`/`showcasing`, entre as maiores razões de excesso de 2024; a construção finge explicar e não explica | diga a consequência concreta: `…, o que reduz o custo por conversa de US$ 0,04 para US$ 0,01` | `[F]` Kobak et al. 2025 · também catalogado como "análise superficial" na skill local `no-ai-slop` |
| `panorama`, `cenário`, `âmbito`, `no que tange a`, `no que diz respeito a` | equivalentes de `realm`/`landscape`/`when it comes to`; são preenchimento de posição sintática | `em`, `sobre`, `para` — ou reescreva a frase sem a moldura | `[OP]` skill local `no-ai-slop`, §Words to cut · `[X]` estudo em português |
| `vale ressaltar que`, `é importante notar que`, `cabe destacar que`, `é fundamental compreender que` | abertura que adia a informação; se o que vem depois importa, ele se sustenta sozinho | corte a moldura e comece pela afirmação | `[OP]` Sabbatini, 2024, lista exatamente `É importante notar que…` e `Vale ressaltar que…` · `[OP]` skill local `no-ai-slop` |
| `em suma`, `em síntese`, `em conclusão`, `de modo geral`, `por fim` abrindo o último parágrafo | ver marcador #5 | comece o parágrafo final pela afirmação que só ele pode fazer | `[F]` Herbold et al. 2023: todos os ensaios do ChatGPT abriam a conclusão da mesma forma |
| `insight` | anglicismo que o modelo usa por default em português | `achado`, `constatação`, `conclusão` | `[OP]` Sabbatini, 2024 |

### Como usar esta tabela sem se autossabotar

`crucial`, `significativo` e `abrangente` são palavras legítimas do português acadêmico.
O marcador não é a palavra: é a palavra **sem o número ou o mecanismo ao lado**.
`A diferença foi significativa (p = 0,01)` está correto. `Os resultados foram significativos` não diz nada.

---

## 4. Tabela B — Construções sintáticas

| Evite | Por quê | Coloque no lugar | Evidência |
|---|---|---|---|
| **Nominalização** onde cabe verbo: `foi realizada a análise dos dados`, `procedeu-se à avaliação` | os LLMs usam nominalizações a 1,5–2× a taxa humana; é o traço sintático mais bem documentado | `analisamos os dados`, `avaliamos` | `[F]` Reinhart et al., PNAS 2025 · `[F]` Herbold et al. 2023 (1,06 → 1,73) |
| **Oração reduzida de gerúndio/particípio no arremate**: `…, demonstrando a relevância da abordagem`, `…, evidenciando o potencial da técnica` | orações participiais a 2–5× a taxa humana; a construção simula explicação | ponto final, e uma frase nova com o fato: `A abordagem cortou a latência mediana de 4,2 s para 1,8 s.` | `[F]` Reinhart et al., PNAS 2025 · `[OP]` skill local `no-ai-slop`, §Superficial analysis |
| **Tríade** (`X, Y e Z` em posição de argumento, três itens sempre) | ritmo de três é a cadência default do modelo | use dois itens, ou quatro, ou o número que os dados exigem — e verifique se os três não são sinônimos | `[F-vendor]` Pangram: 19 vs 5 por 10.000 palavras (4×) · `[X]` estudo revisado por pares |
| **Antítese vazia**: `não apenas X, mas também Y`; `não se trata de X, e sim de Y`; `mais do que X, é Y` | a negação não carrega informação: só serve de rampa retórica para Y | afirme Y direto: em vez de `não é apenas uma questão de custo, mas de arquitetura`, escreva `a arquitetura, e não o custo, determina o resultado` | `[F-vendor]` Pangram: 3 vs 1 por 10.000 palavras · `[OP]` skill local `no-ai-slop`, §Binary contrasts |
| **Hedging empilhado**: `pode potencialmente contribuir de alguma forma para` | o modelo empilha atenuadores em vez de escolher um grau de certeza | escolha um: `contribui`, `pode contribuir` ou `não testamos se contribui` | `[F]` parcial, por contraste: os LLMs **sub-usam** *downtoners* específicos e **não usam** marcadores epistêmicos de primeira pessoa (0,00 em Herbold et al. 2023) — o hedging deles é vago, não pessoal |
| **Ausência total de marcador epistêmico**: o texto nunca diz "não sabemos", "não testamos", "a amostra é pequena demais para" | humanos: 0,06; ChatGPT-4: **0,00** | inclua os limites reais do seu experimento, com o mesmo detalhe dos resultados. Uma seção de limitações honesta é o marcador humano mais forte que existe | `[F]` Herbold et al. 2023 |
| **Frase-resumo de fechamento** que recapitula o parágrafo anterior | o leitor acabou de ler | termine no último fato concreto, ou numa consequência que ainda não foi dita | `[F]` Herbold et al. 2023 · `[OP]` skill local `no-ai-slop`, §Summary-recap endings |
| **Ciclagem de sinônimos**: `o agente… o sistema… a ferramenta… a solução`, tudo referindo a mesma coisa | o modelo varia o termo por estilo; texto científico exige termo fixo | repita o mesmo termo. Em ABNT, consistência terminológica é requisito, não pobreza de vocabulário | `[OP]` skill local `no-ai-slop`, §Synonym cycling · `[F]` compatível com Yoshida (2006), que prescreve texto "simples, claro, preciso e conciso" |
| **Abertura por concessiva genérica**: `Embora existam diversas abordagens, …` | preenche a posição inicial sem nomear as abordagens | nomeie: `LangGraph e AutoGen resolvem X de formas opostas: …` | `[OP]` skill local `no-ai-slop` · `[X]` estudo específico |
| **Revelação por dois-pontos**: `O detalhe que faz funcionar: um segundo agente avalia.` | cadência de post, não de artigo | frase comum: `O que faz funcionar é a avaliação por um segundo agente.` | `[OP]` skill local `no-ai-slop`, §Colon reveals |

---

## 5. Tabela C — Padrões estruturais

| Evite | Por quê | Coloque no lugar | Evidência |
|---|---|---|---|
| **Parágrafos de tamanho uniforme** (todos com 4–5 linhas) | os LLMs não reproduzem a variação estilística humana; a uniformidade é o resíduo disso | deixe um parágrafo com duas linhas quando o ponto é curto, e um com dez quando o argumento precisa | `[F]` "LLMs struggle to match human stylistic variation" (Reinhart et al., PNAS 2025) · `[F]` densidade lexical praticamente constante entre níveis CEFR, incluindo português (Silva & Rottava, 2024) |
| **Lista com marcadores onde o gênero pede prosa** | artigo em ABNT é prosa argumentativa; a lista quebra a cadeia de raciocínio e esconde a ausência de conexão lógica entre os itens | converta em parágrafo com conectivo real, ou em tabela numerada se os itens forem paralelos e comparáveis | `[F-vendor]` bullets 9× o baseline humano (Pangram) · `[F-pre]` formatação markdown desaparece sob instrução de prosa (Freeburg, 2026) |
| **Cabeçalho a cada dois parágrafos** | fragmenta o argumento em fichas | um cabeçalho por unidade de argumento; num artigo de 5–7 páginas, a estrutura ABNT (Introdução, Método, Resultados, Discussão, Conclusão) já basta | `[F-vendor]` cabeçalhos `#` 23× o baseline humano (Pangram) · `[OP]` skill local `no-ai-slop`, §Formatting slop |
| **Conclusão que repete a introdução** | é o modo default do modelo de terminar um texto | a conclusão deve dizer algo que só é possível dizer **depois** dos resultados: o que mudou na sua crença, o que o experimento não decidiu, o que faria diferente | `[F]` Herbold et al. 2023 (estrutura rígida, conclusões de abertura idêntica) |
| **Seções de peso simétrico** (Método, Resultados e Discussão com 1 página cada) | o artigo real tem um centro de gravidade | dê mais espaço ao que você mediu e menos ao que você contextualizou | `[INF]` derivado de Reinhart et al. 2025; não medido em nível de seção |
| **Revisão de literatura que lista sem confrontar** (`Autor A afirma X. Autor B afirma Y. Autor C afirma Z.`) | o modelo enfileira, não contrapõe | organize por controvérsia: quem discorda de quem, e com que evidência | `[INF]` · alinhado com o material já produzido em `03-storm-controversia.md` deste repositório |

---

## 6. Tabela D — Marcadores próprios do português acadêmico

Esta é a seção onde é mais fácil errar, porque três das crenças mais repetidas **não se sustentam**. Elas estão na seção 8.

| Evite | Por quê | Coloque no lugar | Evidência |
|---|---|---|---|
| **Adjetivação avaliativa sem número** (`resultados robustos`, `melhora expressiva`, `ganho considerável`) | é o vício que a própria literatura brasileira de redação científica nomeia | número, intervalo ou mecanismo | `[F]` Yoshida (2006), *J Vasc Bras* 5(4), DOI [10.1590/S1677-54492006000400002](https://www.scielo.br/j/jvb/a/TNcPWS84VC7bR3whQ8J343D/?lang=pt): não contaminar o texto "com excesso de verborragia, rebuscamento, erudição e gongorismo" |
| **Voz passiva sem motivo** (`foi observado que`, `foram coletados os dados`) | prescrição explícita da literatura brasileira. **Não é marcador de IA** — ver seção 8 | `observamos que`, `coletamos os dados`. Mantenha a passiva quando o agente for irrelevante ou desconhecido | `[F]` Yoshida (2006): "reescrevendo trechos de forma mais simples e direta (evitar voz passiva)" · `[F]` Reinhart et al. 2025: LLMs **sub-usam** passiva sem agente (≈50% da taxa humana) |
| **Inversão sintática, trocadilho e metáfora** em texto científico | prescrição explícita | ordem direta; a metáfora só entra se for o objeto de estudo | `[F]` Yoshida (2006): "Deve-se evitar inversões de frases, trocadilhos e metáforas" |
| **Tempo verbal e pessoa oscilantes** entre seções | inconsistência é sinal de colagem de trechos de origens diferentes — inclusive de origens diferentes do agente | padronize antes de entregar. A recomendação brasileira mais citável é passado simples e terceira pessoa do singular | `[F]` Yoshida (2006): "padronizando o tempo verbal (preferencialmente no passado simples) e a pessoa (preferencialmente terceira pessoa do singular)" |
| **Resumo em tópicos ou com mais de um parágrafo** | a norma pede parágrafo único e frases concisas afirmativas | um parágrafo; primeira frase significativa, explicando o tema; 100–250 palavras para artigo de periódico, 150–500 para trabalho acadêmico | `[F-inst]` ABNT NBR 6028. Extensões e prescrições conforme resenhas da norma; a norma em si é paga e não foi consultada no original — ver ressalva na seção 8 |
| **Conectivo de transição em toda abertura de parágrafo** (`Além disso`, `Ademais`, `Nesse sentido`, `Dessa forma`, `Por conseguinte`) | o problema real não é a quantidade: é o conectivo que **não descreve a relação lógica de fato existente**. `Além disso` entre dois parágrafos que não se somam é ruído | mantenha o conectivo quando a relação é real e nomeie-a corretamente (`porque`, `apesar de`, `em contrapartida`); corte quando o parágrafo se sustenta sozinho | `[F]` **contra o senso comum**: LLMs usam **menos** marcadores discursivos que humanos (0,36 vs 0,57 — Herbold et al. 2023). Ver seção 8, mito #1 |

---

## 7. Tabela E — Pontuação e tipografia

| Evite | Por quê | Coloque no lugar | Evidência |
|---|---|---|---|
| **Travessão longo no estilo americano**, colado (`o resultado—que surpreendeu—foi`) | (a) a frequência relativa de travessão em abstracts científicos mais que dobrou entre 2021 e 2025; (b) o uso colado é convenção tipográfica **inglesa**, não portuguesa | em português: par de vírgulas, parênteses, dois-pontos, ou travessão **em par e com espaços**, na função de aparte | `[F-pre]` Keck (2025), 10.000 abstracts de ecologia via OpenAlex, dados e código abertos, **não revisado por pares** — [pieceofk.fr](https://www.pieceofk.fr/the-rise-of-the-em-dash-in-ecology-abstracts/) · `[F]` uso normativo: Cunha & Cintra, *Nova Gramática do Português Contemporâneo*, via [Ciberdúvidas/ISCTE-IUL](https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/o-uso-do-travessao-e-da-virgula/31103) — o travessão marca mudança de interlocutor ou isola palavra/frase, "com função semelhante à dos parênteses e normalmente em par" |
| **Negrito no meio do parágrafo** | maior discrepância isolada já medida entre texto humano e de IA | itálico para termo técnico estrangeiro (norma ABNT); nada para ênfase — a ênfase vem da posição da informação na frase | `[F-vendor]` Pangram: 65 vs 2 por 10.000 palavras (43×) · `[F-pre]` Freeburg (2026): desaparece por completo sob instrução de "sem formatação" |
| **Emoji** | em artigo em ABNT, dispensa justificativa | remova | `[F-vendor]` cuidado com a generalização: emoji **em geral** aparece só 2× acima do baseline humano; o sinal está em classes específicas (✅ a 167×). Humanos usam mais rostos |
| **Aspas curvas “ ”** em vez de retas | heurística de plataforma, **não** achado linguístico | irrelevante para o artigo: use o padrão do seu editor de texto e seja consistente. Em português, aspas angulares « » também são legítimas | `[X]` nenhum estudo encontrado. Aspas curvas são artefato de autocorreção de editor, e o Word as produz sozinho |
| **Excesso de listas numeradas dentro do corpo do texto** | ver Tabela C | prosa | `[F-vendor]` + `[F-pre]` como acima |

### O que a norma brasileira realmente diz sobre travessão

`[F]` **O Acordo Ortográfico de 1990 não regula pontuação.**
Verificação direta das Bases I a XXI ([Wikisource](https://pt.wikisource.org/wiki/Acordo_Ortogr%C3%A1fico_da_L%C3%ADngua_Portuguesa_(1990))): o Acordo trata de alfabeto, acentuação, hífen, apóstrofo, maiúsculas, divisão silábica. **Nenhuma Base trata de travessão ou de espaçamento de travessão.**
Portanto, qualquer afirmação do tipo "o Novo Acordo manda usar travessão sem espaços" é falsa. O Acordo trata de **hífen**, que é outro sinal.

`[X]` Não foi localizada fonte normativa brasileira (ABL, ABNT, Manual de Redação da Presidência) que prescreva a presença ou ausência de espaço em torno do travessão.
O uso com espaços é **prática editorial brasileira observada**, não norma escrita. Escreva assim no artigo, se precisar mencionar.

### Ressalva importante sobre o travessão como marcador

`[F-pre]` Freeburg, E. M. (2026), "The Last Fingerprint: How Markdown Training Shapes LLM Prose", [arXiv:2603.27006](https://arxiv.org/abs/2603.27006) — **preprint de autor único independente, sem revisão por pares**.
Mede travessões por 1.000 palavras em 12 modelos.
O dado que importa aqui é o **baseline humano: 3,23 por 1.000 palavras, com faixa de 0,33 a 17,12 em oito ensaios publicados**.
Essa faixa humana engloba quase todos os modelos medidos.
**Conclusão prática: o travessão isolado não discrimina nada.** Trate-o como sintoma de revisão apressada, não como prova. E nunca acuse ninguém — nem se defenda — com base nele.

---

## 8. MITOS — o que circula como "prova de IA" e não se sustenta

Esta seção existe para o autor não remover escrita legítima.

### Mito 1 — "IA usa conectivos em excesso"

`[F]` **Falso, ou ao menos não sustentado pela medição disponível.**
Herbold et al. (2023), *Scientific Reports*, mediram marcadores discursivos em 270 redações: humanos **0,57**, ChatGPT-3.5 **0,52**, ChatGPT-4 **0,36**.
O ChatGPT-4 usa **significativamente menos** conectivos que humanos.

O que é super-usado é **densidade nominal**, não conectivo.
Se o seu texto tem muitos `Além disso`, o problema é que o conectivo não descreve a relação real — problema de escrita, não assinatura de IA.
**Não corte conectivos corretos para "parecer humano".** Você vai deixar o texto pior e não vai reduzir suspeita nenhuma.

### Mito 2 — "IA abusa da voz passiva"

`[F]` **Invertido.**
Reinhart et al. (2025), *PNAS*: LLMs **sub-usam** voz passiva sem agente, a cerca de **50% da taxa humana**.
Passiva em excesso é vício de escrita acadêmica **humana** — e a literatura brasileira já pedia para evitá-la em 2006 (Yoshida).
Corrija a passiva porque ela torna o texto pior, não porque ela denuncia IA. São dois argumentos distintos e o segundo é falso.

### Mito 3 — "IA tem vocabulário pobre / baixa diversidade lexical"

`[F]` **Vale para modelos antigos, não para os atuais.**
MTLD em Herbold et al. (2023): ChatGPT-3.5 = 75,68 (abaixo do humano), humano = 95,72, **ChatGPT-4 = 108,91 (acima do humano)**.
Bao et al. (2025), *Scientometrics*, apontam na mesma direção: depois do ChatGPT, a complexidade **lexical** dos abstracts **subiu** — o que caiu foi a complexidade **sintática**, a coesão e a legibilidade.
Vocabulário rico não é prova de nada.

### Mito 4 — "A ABNT exige impessoalidade / proíbe primeira pessoa"

`[X]` **Não confirmado.**
A única prescrição ABNT sobre pessoa verbal que foi possível rastrear a uma cláusula específica é a da **NBR 6028**, e ela vale **apenas para o resumo**.
A NBR 14724 trata de estrutura e apresentação (elementos pré-textuais, margens, fonte, paginação), não de pessoa verbal.
Para a NBR 6022 (artigo científico), nenhuma prescrição de voz ou pessoa foi localizada.
Há literatura acadêmica que trata a impessoalidade obrigatória como **convenção institucional dos manuais universitários**, não como norma: Oliveira & Vidal (2020), *New Trends in Qualitative Research*, DOI [10.36367/ntqr.2.2020.182-195](https://publi.ludomedia.org/index.php/ntqr/article/view/83), argumentam que a rigidez impessoal é obstáculo à clareza. `[F]`
**Regra prática:** siga a convenção da sua área e do seu orientador. Não invoque "a ABNT exige" sem citar a cláusula — porque provavelmente ela não existe.

*Ressalva de honestidade:* as normas ABNT são pagas e **não foram consultadas no original** nesta pesquisa; os textos citados vêm de resenhas secundárias. Antes de citar cláusula da NBR 6028 ou 14724 no artigo, consulte a norma pela biblioteca da sua instituição. Há indícios `[X]` de que a NBR 6028:2021 rebaixou a terceira pessoa de exigência a recomendação, mas isso **não foi confirmado no texto da norma**.

### Mito 5 — "Travessão longo é prova de IA"

Ver seção 7. `[F-pre]` O baseline humano (0,33 a 17,12 por 1.000 palavras) se sobrepõe a quase toda a faixa dos modelos.
Escritores humanos usam travessão. O sinal, se existe, é estatístico e de corpus — não serve para um documento individual.

### Mito 6 — "Emoji é sinal certo de IA"

`[F-vendor]` Emoji **em geral** aparece apenas ~2× acima do baseline humano.
O sinal real está em símbolos específicos de checklist (✅) e em bullets decorativos, típicos de renderização de chat.
Num artigo em ABNT o ponto é irrelevante: não use emoji porque o gênero não comporta, não porque denuncia IA.

### Mito 7 — "Existe uma lista definitiva de frases de IA em português"

`[X]` **Não existe estudo revisado por pares que meça colocações multipalavra** (`it is important to note`, `plays a crucial role`, `não apenas X mas também Y`) em corpus de LLM.
A literatura revisada mede **palavras isoladas** (Kobak) ou **features gramaticais** (Reinhart).
Os únicos números sobre construções vêm da **Pangram**, fornecedor comercial de detector, com metodologia não publicada — [pangram.com/supporting-evidence](https://www.pangram.com/supporting-evidence). `[F-vendor]`
As listas que circulam em blogs em português ([iatendencias](https://iatendencias.com/pt/aplicacoes-de-ia/quais-palavras-denunciam-textos-de-ia-descubra-como-identificar-textos-gerados-por-ia/), [TargetHD](https://www.targethd.net/as-palavras-que-denunciam-um-texto-escrito-pelo-chatgpt/), [Exame](https://exame.com/carreira/o-erro-que-faz-seu-texto-parecer-escrito-por-chatgpt-veja-como-evitar/)) são `[OP]` **opinião sem método**. Não cite nenhuma delas como evidência no artigo.
A exceção de melhor qualidade é o post de **Marcelo Sabbatini (UFPE)**, [marcelo.sabbatini.com](https://www.marcelo.sabbatini.com/texto-chocho-como-identificar-escrita-ia/), dez/2024 — ainda `[OP]`, mas de autor identificado e credenciado, coautor de guia sobre IA publicado pela Intercom.

### Mito 8 — "A hipótese do `delve` está provada"

`[OP]` A explicação de que `delve` vem de anotadores de RLHF na Nigéria, onde a palavra é comum no inglês formal, foi publicada por **Alex Hern no *The Guardian* (newsletter TechScape, 16/04/2024)**, [theguardian.com](https://www.theguardian.com/technology/2024/apr/16/techscape-ai-gadgest-humane-ai-pin-chatgpt).
`[X]` Nenhum estudo revisado por pares testa essa causalidade. É **especulação jornalística plausível**, não achado.
Kobak et al. **não mencionam** a hipótese.

### Mito 9 — "Escrita polida e sem erros levanta suspeita"

`[F]` Esse é o mito mais perigoso, porque tem o efeito **inverso** do esperado.
Liang et al. (2023), *Patterns*:

- **enriquecer** o vocabulário de um ensaio de não nativo derruba a taxa de falso positivo dos detectores de **61,3% para 11,6%**;
- **simplificar** o vocabulário de ensaios de estudantes nativos americanos faz a taxa de falso positivo **subir de 5,19% para 56,65%**.

Ou seja: texto mais simples e mais previsível é **mais** sinalizado como IA, não menos — porque simplicidade é exatamente o que a perplexidade baixa mede.
Escrever pior para "parecer humano" é uma estratégia que se volta contra o autor.

*(Os pares 61,3% → 11,6% vêm da versão publicada em Patterns; a versão arXiv registra 61,22% → 11,77%. A diferença é de arredondamento entre versões.)*

---

## 9. Detectores: o que medem, e a que o autor se expõe

### O que eles medem

`[F-inst]` **Perplexidade** — o quanto um modelo de língua consideraria previsível a sequência de palavras do documento. Texto de LLM tende a baixa perplexidade porque foi gerado maximizando probabilidade.
`[F-inst]` **Burstiness** — o quanto a perplexidade **varia** ao longo do documento. Humanos alternam trechos previsíveis e imprevisíveis; o modelo mantém nível constante.
Definições do próprio GPTZero: [gptzero.me](https://gptzero.me/news/perplexity-and-burstiness-what-is-it/). `[F-inst]`
A empresa declara no mesmo texto que, **desde o outono de 2023, não usa mais perplexidade e burstiness** como critério: migrou para arquitetura de aprendizado profundo, e as duas métricas passaram a ser **um** dos sete indicadores do modelo.
Ou seja, o vocabulário que circula em blogs ("o detector mede burstiness") já descreve uma geração anterior de ferramentas.

Os métodos acadêmicos por trás disso são dois:

- `[F]` **DetectGPT** — Mitchell, Lee, Khazatsky, Manning & Finn, ICML 2023, [arXiv:2301.11305](https://arxiv.org/abs/2301.11305).
  Premissa: texto amostrado de um LLM tende a ocupar regiões de **curvatura negativa** da função de log-probabilidade do modelo. Perturba o texto e compara. Elevou a detecção de notícias falsas do GPT-NeoX 20B de 0,81 para 0,95 de AUROC.
- `[F]` **Binoculars** — Hans et al., [arXiv:2401.12070](https://arxiv.org/abs/2401.12070).
  Razão entre perplexidade e **cross-perplexidade** entre dois modelos (observador e executor). Reportam detectar mais de 90% das amostras do ChatGPT a uma taxa de falso positivo de 0,01%, sem treino em dados do ChatGPT.
  *Ressalva:* esse desempenho é medido em condições de laboratório, com textos não editados, em inglês, e sem paráfrase adversária. Ver a linha sobre *humanizers* na tabela abaixo.

Nenhum detector "lê" o texto. Todos estimam uma probabilidade a partir de estatística de superfície. Não há marca d'água nos modelos comerciais que o estudante vai usar.

### Por que erram

| Achado | Número | Fonte |
|---|---|---|
| Sete detectores classificaram erradamente como IA ensaios TOEFL escritos por **humanos não nativos em inglês** | **falso positivo médio de 61,3%**; **19,8%** dos ensaios sinalizados por **todos** os sete; **97,8%** sinalizados por ao menos um | `[F]` Liang, Yuksekgonul, Mao, Wu & Zou (2023), *Patterns* 4(7):100779, DOI [10.1016/j.patter.2023.100779](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/) |
| Os mesmos detectores classificaram corretamente ensaios de estudantes americanos do 8º ano | acurácia quase perfeita — falso positivo médio de **5,19%** | idem |
| Reescrever o ensaio do não nativo pedindo vocabulário mais sofisticado | falso positivo cai de **61,3% para 11,6%** | idem |
| Reescrever o ensaio do nativo pedindo vocabulário mais simples | falso positivo **sobe de 5,19% para 56,65%** | idem |
| 14 ferramentas testadas (12 públicas + Turnitin e PlagiarismCheck) | "as ferramentas de detecção disponíveis não são nem acuradas nem confiáveis"; viés sistemático a classificar como humano; técnicas de ofuscação (edição manual, tradução automática, paráfrase) pioram muito o desempenho | `[F]` Weber-Wulff et al., *International Journal for Educational Integrity*, v. 19, art. 26, 2023, DOI 10.1007/s40979-023-00146-z, preprint [arXiv:2306.15666](https://arxiv.org/abs/2306.15666) |
| Ferramentas "humanizadoras" e paráfrase adversária derrotam detectores | 19 humanizers testados: "muitos detectores existentes falham em detectar texto humanizado". Paráfrase guiada pelo próprio detector reduz a métrica T@1%FPR em média **87,88%** (até −98,96% contra o Fast-DetectGPT) | `[F-pre]` Masrour, Emi & Spero, [arXiv:2501.03437](https://arxiv.org/abs/2501.03437), 2025 · `[F]` Cheng et al., NeurIPS 2025, [arXiv:2506.07001](https://arxiv.org/abs/2506.07001) |
| A própria OpenAI aposentou seu classificador | nota adicionada ao anúncio em 20/07/2023: retirado "devido à sua baixa taxa de acurácia". No anúncio original a ferramenta identificava corretamente **26%** do texto de IA e rotulava erradamente **9%** do texto humano como IA | `[F-inst]` parcial — [openai.com](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/). A página bloqueou acesso automatizado; os 26% aparecem em múltiplas fontes secundárias e os 9% **não** puderam ser confirmados no documento oficial |
| O Turnitin admite falso positivo maior no nível de sentença | ~**4%** em nível de sentença, contra 1% em nível de documento; por isso a ferramenta deixou de exibir score abaixo de 20% | `[F-inst]` parcial — posts oficiais do Turnitin, 2023; **as páginas bloquearam acesso automatizado, número não verificado na fonte** |
| Cinco detectores sobre **texto científico em português** gerado por ChatGPT, Gemini e DeepSeek | ZeroGPT foi o mais preciso, **mas produziu falsos positivos em texto humano**; os demais tiveram alta taxa de falso positivo, baixa sensibilidade ao português ou resultados inconsistentes | `[F]` Candido, Barbosa, Martins & Costa (2025), WICS/SBC, DOI [10.5753/wics.2025.8692](https://sol.sbc.org.br/index.php/wics/article/view/35937) |
| A Vanderbilt University desativou o detector de IA do Turnitin | a taxa de 1% de falso positivo declarada pelo Turnitin implicaria ~**750 dos 75.000** trabalhos de 2022 rotulados erradamente | `[F-inst]` [Vanderbilt Brightspace](https://www.vanderbilt.edu/brightspace/2023/08/16/guidance-on-ai-detection-and-why-were-disabling-turnitins-ai-detector/), 16/08/2023. Citam também o viés contra falantes não nativos e a falta de transparência metodológica |

### O que isso significa para um estudante brasileiro

`[INF]`, mas com base sólida nos números acima:

1. Você escreve em português, que é ainda **menos** coberto pelos detectores que o inglês. O principal benchmark multilíngue que virou *shared task* (SemEval-2024 Task 8 / M4GT) **não inclui português**. A cobertura existente (MULTITuDE) é de texto jornalístico, de 2023, com geradores já defasados.
2. O risco de **falso positivo** contra você é real e não é controlável por qualidade de escrita — e a estratégia intuitiva (simplificar o texto) **aumenta** o risco.
3. A defesa que funciona não é linguística, é **documental**: versões do arquivo com histórico (Google Docs, Git, OneDrive), notas de leitura, dados brutos, scripts, logs do experimento. Um histórico de revisão com 40 commits é prova; "meu texto não parece IA" não é.
4. Não use detector no próprio texto para decidir o que reescrever. Você estará otimizando para uma métrica ruidosa, e piorando o artigo no caminho.

---

## 10. O que declarar, e onde

Isso não é marcador linguístico, mas resolve o problema que os marcadores só disfarçam: **uso declarado não levanta suspeita de autoria.**

### Internacional

| Instância | Exigência | Fonte |
|---|---|---|
| **COPE** | IA não pode ser listada como autora — não pode assumir responsabilidade pelo trabalho, não é entidade legal, não declara conflito de interesse nem gere licenças. Autores que usaram IA devem divulgar **na seção de Materiais e Métodos** ou equivalente, dizendo qual ferramenta e como | `[F-inst]` COPE, fev/2023, DOI 10.24318/cCVRZBms, [publicationethics.org](https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools) — a página bloqueou acesso automatizado; DOI verificado |
| **ICMJE** | Chatbots não podem ser autores, "porque não podem ser responsáveis pela acurácia, integridade e originalidade do trabalho". O uso deve ser divulgado **na carta de submissão E no manuscrito**: nos **agradecimentos** se foi assistência de escrita, nos **métodos** se foi coleta, análise ou geração de figuras. O autor responde por revisar e editar o resultado — "a IA pode gerar saída de aparência autoritativa que é incorreta, incompleta ou enviesada" — e por garantir ausência de plágio | `[F-inst]` [icmje.org](https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html) |
| **Elsevier** | Permitido: melhorar linguagem, clareza e legibilidade de texto **escrito pelos autores**; resumir literatura; organizar conteúdo. Proibido: gerar seções sem contribuição intelectual genuína; fabricar ou alterar dados, resultados ou referências. Exige seção própria **antes das referências**: *"Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"*, com o modelo: *"During the preparation of this work the author(s) used [NOME DA FERRAMENTA] in order to [MOTIVO]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content."* IA não pode ser autor | `[F-inst]` [elsevier.com](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) |
| **Springer Nature** | LLMs não satisfazem os critérios de autoria. Uso deve ser documentado na **seção de Métodos**. **Exceção relevante**: revisão de estilo assistida por IA (legibilidade, gramática, ortografia, pontuação, tom) sobre texto humano **não precisa ser declarada** | `[F-inst]` parcial — [springernature.com](https://www.springernature.com/gp/policies/editorial-policies) e [nature.com](https://www.nature.com/nature-portfolio/editorial-policies/ai); as páginas exigiram autenticação, conteúdo não verificado na fonte |
| **Taylor & Francis** | IA não pode ser autora; obrigatório reconhecer o uso **com nome completo da ferramenta e versão, como e por que foi usada**; proibido gerar conteúdo que substitua responsabilidades centrais do pesquisador, inclusive resumos. Orientação expandida em 12/06/2024 | `[F-inst]` [newsroom da T&F](https://newsroom.taylorandfrancisgroup.com/expanded-guidance-on-ai-application-for-authors-editors-and-reviewers/) |
| **Wiley** | IA não é capaz de iniciar pesquisa original sem direção humana, não tem personalidade jurídica nem titularidade de copyright → não pode ser autora. Divulgação obrigatória na submissão (propósito, se influenciou argumentos-chave, como o autor verificou), **exceto** para ortografia, gramática e edição geral | `[F-inst]` [authors.wiley.com](https://authors.wiley.com/ethics-guidelines/index.html) |

### Brasil — o que efetivamente vale

| Instância | Exigência | Fonte |
|---|---|---|
| **CNPq — Portaria nº 2.664, de 6/03/2026** (Política de Integridade na Atividade Científica) | **O documento normativo federal mais forte hoje.** Não proíbe IA generativa, mas exige declaração "qualquer que seja o tipo de IAG e a fase do desenvolvimento da pesquisa, especificando a ferramenta utilizada e a finalidade". Veda "a submissão de conteúdo gerado por IAG como se fosse de autoria humana". O autor é "integralmente responsável pelo conteúdo final, inclusive por eventuais plágios ou imprecisões geradas pela ferramenta". E: "o uso da inteligência artificial na elaboração de pareceres científicos não é recomendado" | `[F-inst]` [gov.br/cnpq](https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica) |
| **Unicamp — Deliberação CONSU-A-005/2026, de 31/03/2026** | Art. 3º, VI: "o uso da IA Generativa em trabalhos acadêmicos, relatórios, artigos, documentos administrativos ou qualquer outra produção intelectual **deve ser declarado explicitamente, por meio de nota de rodapé, seção específica ou forma equivalente**". Art. 3º, II: a contribuição intelectual principal e a forma final devem ser de autoria humana. **Não menciona detectores de IA** | `[F-inst]` [pg.unicamp.br](https://www.pg.unicamp.br/norma/32327/0) |
| **UFMG — Comissão Permanente de IA** | "Requerer transparência dos estudantes no uso de IA em trabalhos acadêmicos, com inclusão de **apêndices detalhando o papel das ferramentas utilizadas**." Não menciona detectores | `[F-inst]` [ufmg.br/ia/recomendacoes](https://www.ufmg.br/ia/recomendacoes/) |
| **UFRJ** | Atualização das Diretrizes de Integridade Acadêmica (CTEP) + Recomendações sobre uso de IA (CRIA), em consulta até 15/04/2026: autoria reconhecida apenas a quem contribuiu intelectualmente de forma substancial; responsabilidade final vinculada à autoria humana; IA restrita a funções auxiliares com verificação crítica. Não tratam de detectores | `[F-inst]` [conexao.ufrj.br](https://conexao.ufrj.br/2026/03/ufrj-atualiza-diretrizes-de-integridade-academica-e-propoe-recomendacoes-sobre-o-uso-de-inteligencia-artificial/) |
| **USP** | Guia de Boas Práticas Científicas, 3ª ed. (Pró-Reitoria de Pesquisa e Inovação, 2026), atualizado para exigir uso responsável, declaração do uso e responsabilidade humana pelo conteúdo | `[F-inst]` parcial — existência e escopo confirmados por [notícia institucional](https://site.fo.usp.br/noticias/diretrizes-do-cnpq-e-guias-da-usp-reforcam-integridade-e-transparencia-no-uso-de-ia/); o PDF não foi lido, não cite página ou artigo |
| **SciELO** | Guia de uso de ferramentas e recursos de IA na Rede SciELO (14/09/2023): apenas humanos podem ser autores; declarar na seção de **Materiais e Métodos** qual ferramenta e como foi usada; uso de chatbot em pareceres deve ser explicitado | `[F-inst]` [scielo.org](https://www.scielo.org/pt-br/sobre-o-scielo/metodologias-e-tecnologias/guia-de-uso-de-ferramentas-e-recursos-de-inteligencia-artificial-na-comunicacao-de-pesquisas-na-rede-scielo/) e [blog oficial](https://blog.scielo.org/blog/2023/08/30/inteligencia-artificial-e-a-comunicacao-da-pesquisa/) |
| **Periódicos brasileiros — panorama** | Dos 200 principais periódicos da área interdisciplinar da CAPES: **20,5%** mencionam IA generativa nas diretrizes de preparação de artigos, **7,5%** no processo de avaliação por pares, **6%** em ambos | `[F]` Gomes & Mendes (2025), *Encontros Bibli*, DOI [10.5007/1518-2924.2025.e103488](https://www.scielo.br/j/eb/a/SJk53dtyBBfVq583TJhtGTz/?format=html&lang=pt) |
| **Associações científicas brasileiras** | De 33 associações e 50 periódicos analisados, **nenhuma associação** tinha posicionamento explícito e apenas **3 de 50 periódicos (6%)** tinham diretrizes formais até junho de 2023 | `[F]` Lopes et al. (2024), DOI [10.14571/brajets.v17.n2.623-648](https://doi.org/10.14571/brajets.v17.n2.623-648), via [SciELO em Perspectiva](https://blog.scielo.org/blog/2025/10/10/o-paradoxo-da-transparencia-no-uso-de-ia-generativa-na-pesquisa-academica/) |

**Lacunas verificadas `[X]`:** não foi encontrada política institucional pública da **UnB** sobre IA em trabalhos acadêmicos; nem posicionamento oficial da **ABEC Brasil**; nem **norma ABNT** sobre citação ou declaração de uso de IA.
O **PL 2338/2023** (marco legal da IA) foi aprovado no Senado e remetido à Câmara em 17/03/2025 — trata de transparência e identificação de conteúdo sintético, mas nenhum artigo aplicável a autoria acadêmica pôde ser verificado; **não cite número de artigo dele**.

**Padrão que emerge das normas brasileiras.** `[INF]`
Nenhuma delas proíbe o uso. Todas exigem **declaração explícita** e **responsabilidade humana pelo conteúdo final**.
Nenhuma das quatro políticas universitárias verificadas (Unicamp, UFMG, UFRJ, USP) menciona detectores de IA como instrumento de verificação.
Isso é coerente com a seção 9: as instituições que estudaram o assunto sabem que os detectores não sustentam uma acusação.

**Paradoxo da transparência.** `[F]` Schilke & Reimann (2025), DOI [10.1016/j.obhdp.2025.104405](https://doi.org/10.1016/j.obhdp.2025.104405), citados pelo blog do SciELO: declarar o uso de IA **reduz sistematicamente a credibilidade percebida** do trabalho.
Isto é um fato a considerar, não uma licença para omitir. A omissão, se descoberta, custa mais.

**Recomendação `[INF]`:** verifique a política do periódico, do curso e da sua universidade **antes** de escrever, não depois.
Ordem de precedência prática: norma da sua universidade → política do periódico ou do evento → Portaria CNPq 2.664/2026, se houver qualquer vínculo com fomento do CNPq → modelo da Elsevier como default na ausência das anteriores.
Na ausência de qualquer política (o caso majoritário no Brasil, pelos números da tabela), declare mesmo assim e mantenha o histórico de versões.

---

## 11. Checklist final — aplicar antes de entregar

Cada item é verificável em minutos. Ordem de execução recomendada.

### Passada 1 — busca literal no arquivo (Ctrl+F)

- [ ] `crucial`, `fundamental`, `essencial` — cada ocorrência tem um número, um mecanismo ou uma consequência ao lado? Se não, corte.
- [ ] `robusto`, `abrangente`, `significativo`, `expressivo`, `considerável` — idem. `significativo` só fica se houver teste estatístico.
- [ ] `ressaltar`, `destacar`, `evidenciar`, `sublinhar`, `demonstrar` como verbo de arremate — substitua pela consequência concreta.
- [ ] `vale ressaltar`, `é importante notar`, `cabe destacar`, `nesse sentido`, `dessa forma`, `no que tange` — corte a moldura, mantenha a afirmação.
- [ ] `não apenas … mas também`, `mais do que … é`, `não se trata de … e sim` — afirme só o segundo termo.
- [ ] `em suma`, `em síntese`, `em conclusão`, `por fim`, `de modo geral` — a conclusão diz algo novo ou repete a introdução?
- [ ] `aprofundar`, `mergulhar`, `explorar a fundo`, `panorama`, `cenário`, `insight` — substitua pelo verbo do que você fez.
- [ ] Travessão `—` — cada ocorrência: vírgula, parênteses ou dois-pontos serviriam melhor? Se ficar, use em par e com espaços.
- [ ] Negrito e emoji no corpo do texto — remova. Itálico só para termo estrangeiro.

### Passada 2 — sintaxe

- [ ] Toda oração começada por gerúndio ou particípio no fim de frase (`…, demonstrando…`, `…, evidenciando…`): vire frase própria com o fato.
- [ ] Toda nominalização com verbo suporte (`foi realizada a análise`, `procedeu-se à avaliação`): vire verbo (`analisamos`, `avaliamos`).
- [ ] Toda enumeração de exatamente três itens: os três são realmente distintos, ou dois são sinônimos?
- [ ] Termos técnicos: o mesmo objeto é chamado sempre pelo mesmo nome? Nenhuma ciclagem de sinônimos.
- [ ] Tempo verbal e pessoa: consistentes em todas as seções?

### Passada 3 — estrutura

- [ ] Meça o número de linhas de cada parágrafo. Se todos ficarem em 4–6 linhas, o texto está uniforme demais — funda dois e parta outro.
- [ ] Cada lista com marcadores: o gênero pede prosa? Converta, ou transforme em tabela numerada se os itens forem comparáveis.
- [ ] Nenhum cabeçalho cobrindo menos de dois parágrafos.
- [ ] A conclusão traz pelo menos uma afirmação que só é possível depois dos resultados.
- [ ] Existe uma seção de limitações **específica** do seu experimento — com números da sua amostra, não com genéricos como "estudos futuros poderão aprofundar".

### Passada 4 — o teste do humano

- [ ] Há pelo menos um trecho onde você admite um limite, uma dúvida ou um resultado que contrariou sua expectativa? Se não há, o texto tem 0,00 marcador epistêmico — a assinatura do ChatGPT-4 em Herbold et al. (2023).
- [ ] Toda afirmação factual tem fonte citada e verificável? Nenhuma referência foi conferida apenas pelo título?
- [ ] Você conferiu, uma a uma, que todas as referências existem e dizem o que você afirma que dizem? (Este é o item mais importante da lista inteira.)
- [ ] Leia dois parágrafos em voz alta. Soam como você falando com um colega, ou como um relatório neutro?

### Passada 5 — procedimento

- [ ] Histórico de versões preservado (Git, Google Docs, OneDrive) desde o rascunho.
- [ ] Você leu a política da **sua universidade** sobre IA em trabalhos acadêmicos. Se for Unicamp, a declaração explícita é obrigatória por deliberação do Conselho Universitário; se for UFMG, a recomendação pede apêndice detalhando o papel das ferramentas.
- [ ] Declaração de uso de IA redigida, no formato exigido pela universidade ou pelo periódico; na ausência de política, no modelo da Elsevier, em seção própria antes das referências.
- [ ] Se houver qualquer vínculo com fomento do CNPq, a declaração especifica **a ferramenta e a finalidade, em cada fase da pesquisa** em que ela foi usada (Portaria 2.664/2026).
- [ ] Dados brutos, scripts e logs do experimento arquivados e referenciados.
- [ ] Você **não** rodou o texto em detector para decidir o que reescrever.

---

## 12. Relação com a skill local `no-ai-slop`

A skill em `C:\Users\tisao\.claude\skills\no-ai-slop\` (`SKILL.md` + `eval.md`) já cobre, para escrita em inglês e para gêneros não acadêmicos, um catálogo de padrões que este documento não repete: *binary contrasts*, *throat-clearing openers*, *faux-insight setups*, *colon reveals*, *superficial analysis*, *importance puffery*, *weasel attribution*, *fake-strong verbs*, *synonym cycling*, *negative listing*, *dramatic fragmentation*, *rhetorical setups*, *fake-profound kickers*, *summary-recap endings*, *formatting slop* e o uso de travessão.
As linhas deste documento que vieram de lá estão marcadas `[OP] skill local no-ai-slop` — ela é catálogo editorial bem construído, não estudo, e as tabelas acima só a citam onde não há medição melhor.

Três diferenças de escopo importam para o artigo:

1. A skill é escrita para prosa em inglês com voz pessoal. **Um artigo em ABNT tem outras restrições**: consistência terminológica obrigatória, impessoalidade convencional na área, estrutura fixa. Não aplique a instrução "preserve edge, humor e profanidade" a um artigo científico.
2. A skill proíbe `robust`, `delve`, `meticulous`, `intricate` e afins **por padrão**. Em português acadêmico, a regra correta não é banir a palavra: é exigir número ou mecanismo ao lado dela.
3. A skill não trata de detectores, políticas editoriais nem de norma tipográfica em português. Isso é escopo exclusivo deste documento.

---

## 13. Bibliografia consultada

**Revisados por pares (13)**

1. Kobak, D.; González-Márquez, R.; Horvát, E.-Á.; Lause, J. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. *Science Advances*, v. 11, n. 27, 2025. DOI 10.1126/sciadv.adt3813. https://www.science.org/doi/10.1126/sciadv.adt3813
2. Liang, W. et al. Monitoring AI-Modified Content at Scale: A Case Study on the Impact of ChatGPT on AI Conference Peer Reviews. *ICML 2024*. https://arxiv.org/abs/2403.07183
3. Reinhart, A. et al. Do LLMs write like humans? Variation in grammatical and rhetorical styles. *PNAS*, v. 122, e2422455122, 2025. https://arxiv.org/abs/2410.16107
4. Herbold, S. et al. A large-scale comparison of human-written versus ChatGPT-generated essays. *Scientific Reports*, v. 13, 18617, 2023. DOI 10.1038/s41598-023-45644-9. https://pmc.ncbi.nlm.nih.gov/articles/PMC10616290/
5. Liang, W.; Yuksekgonul, M.; Mao, Y.; Wu, E.; Zou, J. GPT detectors are biased against non-native English writers. *Patterns*, v. 4, n. 7, 100779, 2023. DOI 10.1016/j.patter.2023.100779. https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/
6. Weber-Wulff, D. et al. Testing of detection tools for AI-generated text. *International Journal for Educational Integrity*, 2023. https://arxiv.org/abs/2306.15666
7. Bao, T.; Zhao, Y.; Mao, J.; Zhang, C. Examining linguistic shifts in academic writing before and after the launch of ChatGPT. *Scientometrics*, 2025. https://arxiv.org/abs/2505.12218
8. Macko, D. et al. MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark. *EMNLP 2023*. https://aclanthology.org/2023.emnlp-main.616/
9. Candido, L. S.; Barbosa, C. A. de M.; Martins, L. G.; Costa, E. J. H. Análise de Ferramentas de Detecção de IA para Textos Científicos em Português Gerados por ChatGPT, Gemini e DeepSeek. *WICS/SBC*, 2025. DOI 10.5753/wics.2025.8692. https://sol.sbc.org.br/index.php/wics/article/view/35937
10. Gomes, R. de A.; Mendes, T. A. Um panorama das diretrizes relacionadas ao uso de inteligência artificial nos principais periódicos da área interdisciplinar da CAPES. *Encontros Bibli*, 2025. DOI 10.5007/1518-2924.2025.e103488
11. Mitchell, E.; Lee, Y.; Khazatsky, A.; Manning, C. D.; Finn, C. DetectGPT: Zero-Shot Machine-Generated Text Detection using Probability Curvature. *ICML 2023*. https://arxiv.org/abs/2301.11305
12. Hans, A. et al. Spotting LLMs With Binoculars: Zero-Shot Detection of Machine-Generated Text. https://arxiv.org/abs/2401.12070
13. Cheng, Y. et al. Adversarial Paraphrasing: A Universal Attack for Humanizing AI-Generated Text. *NeurIPS 2025*. https://arxiv.org/abs/2506.07001

**Revisados por pares — normativos de estilo em português (3)**

14. Yoshida, W. B. A redação científica. *Jornal Vascular Brasileiro*, v. 5, n. 4, 2006. DOI 10.1590/S1677-54492006000400002. https://www.scielo.br/j/jvb/a/TNcPWS84VC7bR3whQ8J343D/?lang=pt
15. Silva, A. M. da; Rottava, L. Densidade lexical em textos gerados pelo ChatGPT. *Texto Livre*, v. 17, 2024. DOI 10.1590/1983-3652.2024.47836. https://www.scielo.br/j/tl/a/crx3yywCw3LSxtjtdv44mDC/
16. Oliveira, P. de T.; Vidal, M. E. B. Impersonality and passivity in academic manuals. *New Trends in Qualitative Research*, 2020. DOI 10.36367/ntqr.2.2020.182-195. https://publi.ludomedia.org/index.php/ntqr/article/view/83

**Institucionais e normativos — internacionais (7)**

17. COPE. Authorship and AI tools — position statement, fev/2023. DOI 10.24318/cCVRZBms. https://publicationethics.org/guidance/cope-position/authorship-and-ai-tools
18. ICMJE. Defining the Role of Authors and Contributors — §Artificial Intelligence-Assisted Technology. https://www.icmje.org/recommendations/browse/roles-and-responsibilities/defining-the-role-of-authors-and-contributors.html
19. Elsevier. Generative AI policies for journals. https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals
20. Springer Nature. Editorial policies — AI. https://www.springernature.com/gp/policies/editorial-policies
21. Taylor & Francis. Expanded guidance on AI application for authors, editors and reviewers, 12/06/2024. https://newsroom.taylorandfrancisgroup.com/expanded-guidance-on-ai-application-for-authors-editors-and-reviewers/
22. Wiley. Ethics guidelines — AI. https://authors.wiley.com/ethics-guidelines/index.html
23. Vanderbilt University. Guidance on AI detection and why we're disabling Turnitin's AI detector, 16/08/2023. https://www.vanderbilt.edu/brightspace/2023/08/16/guidance-on-ai-detection-and-why-were-disabling-turnitins-ai-detector/

**Institucionais e normativos — Brasil (6)**

24. CNPq. Portaria nº 2.664, de 6 de março de 2026 — Política de Integridade na Atividade Científica. https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-em-acao/cnpq-publica-portaria-que-institui-politica-de-integridade-na-atividade-cientifica
25. Unicamp. Deliberação CONSU-A-005/2026, de 31/03/2026. https://www.pg.unicamp.br/norma/32327/0
26. UFMG. Comissão Permanente de Inteligência Artificial — Recomendações. https://www.ufmg.br/ia/recomendacoes/
27. UFRJ. Diretrizes de Integridade Acadêmica (CTEP) e Recomendações sobre uso de IA (CRIA), 2026. https://conexao.ufrj.br/2026/03/ufrj-atualiza-diretrizes-de-integridade-academica-e-propoe-recomendacoes-sobre-o-uso-de-inteligencia-artificial/
28. USP. Guia de Boas Práticas Científicas, 3ª ed., Pró-Reitoria de Pesquisa e Inovação, 2026. https://site.fo.usp.br/noticias/diretrizes-do-cnpq-e-guias-da-usp-reforcam-integridade-e-transparencia-no-uso-de-ia/
29. SciELO. Guia de uso de ferramentas e recursos de Inteligência Artificial na comunicação de pesquisas na Rede SciELO, 14/09/2023. https://www.scielo.org/pt-br/sobre-o-scielo/metodologias-e-tecnologias/guia-de-uso-de-ferramentas-e-recursos-de-inteligencia-artificial-na-comunicacao-de-pesquisas-na-rede-scielo/

**Normativos de língua portuguesa (2)**

30. Acordo Ortográfico da Língua Portuguesa (1990), Bases I–XXI. https://pt.wikisource.org/wiki/Acordo_Ortogr%C3%A1fico_da_L%C3%ADngua_Portuguesa_(1990)
31. Ciberdúvidas da Língua Portuguesa (ISCTE-IUL), consultório: o uso do travessão e da vírgula (cita Cunha & Cintra, *Nova Gramática do Português Contemporâneo*, p. 662-663). https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/o-uso-do-travessao-e-da-virgula/31103

**Preprints e dados não revisados (4)**

32. Freeburg, E. M. The Last Fingerprint: How Markdown Training Shapes LLM Prose. arXiv:2603.27006, 2026. *Autor único independente, sem revisão por pares.* https://arxiv.org/abs/2603.27006
33. Keck, F. The rise of the em dash in ecology abstracts, 2025. *Blog com dados e código abertos, sem revisão por pares.* https://www.pieceofk.fr/the-rise-of-the-em-dash-in-ecology-abstracts/
34. Yakura, H. et al. Empirical evidence of Large Language Model's influence on human spoken communication. arXiv:2409.01754. *Preprint.* https://arxiv.org/abs/2409.01754
35. Masrour, H.; Emi, B.; Spero, M. DAMAGE: Detecting Adversarially Modified AI Generated Text. arXiv:2501.03437, 2025. *Preprint / workshop.* https://arxiv.org/abs/2501.03437

**Fornecedor comercial — indício, não evidência (2)**

36. Pangram. Supporting evidence. *Metodologia não publicada.* https://www.pangram.com/supporting-evidence
37. GPTZero. Perplexity and Burstiness: What is it? https://gptzero.me/news/perplexity-and-burstiness-what-is-it/

**Opinião de autor identificado (1)**

38. Sabbatini, M. (UFPE). Texto "chocho": como identificar a escrita da IA?, dez/2024. https://www.marcelo.sabbatini.com/texto-chocho-como-identificar-escrita-ia/

**Jornalismo — hipótese não validada (1)**

39. Hern, A. TechScape: How cheap, outsourced labour in Africa is shaping AI English. *The Guardian*, 16/04/2024. https://www.theguardian.com/technology/2024/apr/16/techscape-ai-gadgest-humane-ai-pin-chatgpt

**Skill local**

40. `no-ai-slop` — `C:\Users\tisao\.claude\skills\no-ai-slop\SKILL.md` e `eval.md`.

---

## 14. Ressalvas desta pesquisa

- Nenhuma norma ABNT foi consultada no texto original (são pagas). Todas as prescrições de NBR 6028 / 14724 / 6022 citadas vêm de fontes secundárias e estão marcadas como tal. **Confirme pela biblioteca da sua instituição antes de citar cláusula.**
- Os números de Reinhart et al. (multiplicadores por feature) vêm do texto completo da versão arXiv; o resumo do PNAS não os traz.
- Os valores de razão de frequência de Kobak et al. diferem entre versões do preprint e a versão publicada. Cite a versão que consultar.
- Alguns itens localizados apenas por busca (*Learned Publishing* 2026, *Machine Learning and Knowledge Extraction* 2026) não foram verificados no texto e por isso **não** foram usados como base de nenhuma linha das tabelas.
- Nenhum estudo de deriva lexical em corpus acadêmico em português foi encontrado. Se um existir e tiver escapado à busca, ele derruba a seção 2 — verifique antes de afirmar a lacuna no artigo.
- Sites que bloquearam acesso automatizado e cujo conteúdo, portanto, veio de fontes secundárias: OpenAI (nota de descontinuação do classificador e a taxa de 9% de falso positivo), Turnitin (taxa de falso positivo em nível de sentença), COPE (texto integral do position statement), Springer Nature (política de IA), Cell Press. Estão marcados como parciais no corpo do documento.
- Os PDFs das normas ABNT, do Manual de Redação da Presidência da República e do guia do SciELO não puderam ser lidos pela ferramenta usada. Onde o conteúdo deles aparece, veio de páginas institucionais em HTML ou de resenhas secundárias.
- Alegações que foram procuradas e **não** confirmadas, e que portanto não devem ser repetidas: falso positivo de detectores contra autores neurodivergentes (nenhum estudo revisado por pares localizado; o número de "50%" atribuído a Stanford/UMD não é rastreável); universidades além da Vanderbilt que tenham desativado detectores com documento oficial verificável.
