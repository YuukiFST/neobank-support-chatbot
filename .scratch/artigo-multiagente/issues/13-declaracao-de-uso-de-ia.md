# 13 — Como declarar o uso de IA como auxiliar de pesquisa

Type: research
Status: resolved
Blocked by: —

## Question

O autor quer declarar que usou IA como auxiliar de pesquisa, mesmo sem exigência da professora.
Falta saber **o que** declarar, **onde** no artigo, e **com quanto detalhe**.

Contexto do uso real, que a declaração precisa cobrir com honestidade:

- Levantamento bibliográfico feito por agente, com verificação manual das fontes pelo autor.
- Investigação técnica sobre modelos e hardware feita por agente.
- Planejamento do experimento estruturado com apoio de agente.
- Rascunho de texto com apoio de agente, reescrito pelo autor.
- O próprio objeto de estudo é um sistema de agentes — o que torna a transparência ainda mais relevante.

## O que investigar

1. **Norma brasileira.** Portaria CNPq nº 2.664/2026 e Deliberação Unicamp CONSU-A-005/2026 já foram levantadas em `research/04-marcadores-de-ia.md`. Verificar o que exigem literalmente, e levantar o que existe de CAPES, MEC e das universidades de maior porte.
2. **Norma internacional de referência.** COPE, ICMJE e as políticas de Elsevier, Springer, IEEE e ACM. Interessa especialmente o consenso de que **IA não pode ser listada como autora** e de que a responsabilidade pelo conteúdo é integralmente do autor humano.
3. **Onde a declaração entra.** Nota de rodapé na primeira página, seção de metodologia, seção própria antes das referências, ou agradecimentos. Qual a prática dominante e o que cada veículo recomenda.
4. **Granularidade.** Basta dizer que houve uso, ou é preciso nomear ferramenta, versão, data e finalidade de cada uso? Há diferença entre uso para revisão de texto, para levantamento bibliográfico e para geração de conteúdo?
5. **Risco de declarar demais.** Existe evidência de que declaração detalhada prejudique a avaliação? Se não houver evidência, dizer que não há em vez de especular.
6. **Onde a ABNT entra.** A NBR 6022 ou a NBR 14724 preveem algum elemento onde essa declaração caiba? Se não preveem, dizer isso.

## Entrega

Documento em `research/06-declaracao-de-ia.md`, em português, contendo:

- O que cada norma ou política exige, com citação e URL.
- Recomendação de onde colocar no artigo, com justificativa.
- **Três modelos de texto prontos**, em português, para copiar e adaptar: um mínimo, um intermediário e um detalhado, cada um cobrindo o uso real descrito acima.
- Lista do que **não** fazer: listar IA como autora, atribuir a ela responsabilidade pelo conteúdo, ou usar fórmula vaga que não informa nada.

## Answer

Resolvido em 2026-07-31. Documento em `research/06-declaracao-de-ia.md`, com os três modelos de texto prontos para colar no Google Docs.

**Nada obriga o autor hoje.** Nenhuma norma alcança aluno de graduação em trabalho de disciplina.

- A Portaria CNPq nº 2.664/2026 (DOU de 11.03.2026, edição 47, seção 1, página 4), Art. 9º, I, "c", exige declarar "a ferramenta utilizada e a finalidade" em qualquer fase da pesquisa. Mas o Art. 4º limita o alcance a fomento e a usuários das plataformas do CNPq, **incluindo o Lattes** — o que provavelmente já alcança o autor.
- Achado relevante: o Art. 30 lista apenas os arts. 6º, 7º e 8º como infração. O Art. 9º **não tem gatilho sancionatório próprio**. Não afirmar, no artigo ou fora dele, que omitir gera sanção.
- A Deliberação Unicamp CONSU-A-005/2026, Art. 3º, VI, é a única norma brasileira vinculante que fixa formato — "nota de rodapé, seção específica ou forma equivalente" — e vale só na Unicamp.
- A UFSC RN 217/2025/CUn, Art. 7º, XII, torna a omissão má conduta **apenas onde a declaração for expressamente exigida**.
- CAPES, MEC, UnB, UFRGS e a própria ABNT: nada. USP, UFMG, UFRJ e UFRRJ: recomendação, não exigência.

**Onde colocar: subseção numerada ao fim do Método**, no formato `3.5 Uso de ferramentas de inteligência artificial`.
Justificativa: o uso foi de processo de pesquisa, não de revisão de texto, e é para a seção de Métodos que COPE, Springer, ACM, SciELO e UFRJ direcionam esse tipo de uso.

**A ABNT não tem lugar para isso.** Verificado no texto integral da NBR 6022:2018 e da NBR 14724:2024: zero ocorrências de "artificial", "declaração" e "ferramenta" nas duas.
A âncora normativa para criar a subseção é a NOTA do Esquema 1 da 6022, que deixa a nomenclatura dos títulos dos elementos textuais a critério do autor.
Os Agradecimentos da 6022 §5.3.5 não servem: são texto sucinto aprovado pelo periódico e vêm **depois** das referências.

**Granularidade.** Nenhuma das seis políticas internacionais consultadas exige versão nem data — é achado negativo verificado, não omissão da pesquisa.

**Risco de declarar.** Existe penalidade reputacional por declarar (Schilke e Reimann, 2025, θ = 0,81), mas ser flagrado sem declarar custa o dobro (d = 1,66).
E não há nenhuma evidência de que declaração detalhada seja pior que declaração mínima.
Conclusão prática: declarar compensa, e detalhar não piora.
