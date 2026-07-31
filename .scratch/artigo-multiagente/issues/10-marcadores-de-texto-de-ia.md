# 10 — Marcadores linguísticos de texto gerado por IA, em português acadêmico

Type: research
Status: resolved
Blocked by: —

## Question

Quais palavras, construções e padrões estruturais denunciam texto gerado por modelo de linguagem em português acadêmico, e qual a alternativa correta para cada um?

Motivo: o artigo será rascunhado com apoio de agente e reescrito na voz do autor.
Um texto que carrega os tiques do modelo levanta suspeita de autoria mesmo quando o conteúdo é original — e a suspeita, em trabalho acadêmico, custa tão caro quanto o problema real.

## Escopo da investigação

1. Vocabulário sobre-representado em saída de LLM, com evidência quantitativa quando existir (estudos que mediram frequência de palavras em corpora antes e depois de 2023). Em inglês e, principalmente, em português.
2. Construções sintáticas típicas: paralelismo de três itens, abertura por oração concessiva, o par "não apenas X, mas Y", antítese vazia, hedging repetitivo, frase de fechamento que resume o que acabou de ser dito.
3. Padrões estruturais: parágrafos de tamanho uniforme, listas onde o gênero pede prosa, cabeçalho a cada dois parágrafos, conclusão que não conclui.
4. Marcadores específicos de texto acadêmico em português: conectivos de transição usados em excesso, voz passiva sem motivo, adjetivação avaliativa ("robusto", "abrangente", "significativo" sem número ao lado).
5. Pontuação e tipografia: travessão longo, aspas curvas, emoji, negrito disperso no meio do parágrafo.
6. O que os detectores de texto gerado realmente medem, e por que a taxa de falso positivo deles é alta em texto de autor não nativo em inglês — relevante para o autor saber a que se expõe.

## Fontes a priorizar

Estudos revisados por pares e preprints sobre detecção de texto gerado e sobre deriva lexical em corpora científicos; guias de estilo de periódicos e de editoras; políticas de uso de IA de universidades brasileiras e de periódicos.
Evitar listas de blog sem método — só entram se marcadas como opinião.

## Entrega

Documento em `research/04-marcadores-de-ia.md`, em português, contendo:

- Tabela de termos e construções a evitar, com a alternativa recomendada ao lado e a evidência que sustenta cada linha.
- Seção separada para o que é mito: padrões que circulam como "prova de IA" sem evidência, para o autor não se autossabotar removendo escrita legítima.
- Checklist final aplicável ao artigo antes da entrega.

Consultar também a skill local `no-ai-slop` em `C:\Users\tisao\.claude\skills\no-ai-slop\` e incorporar o que ela já cobre, sem duplicar.

## Answer

Resolvido em 2026-07-31. Documento em `research/04-marcadores-de-ia.md`, 530 linhas, 14 seções, com cada linha das tabelas ancorada em fonte e grau de confiança declarado.
Base: 16 fontes revisadas por pares, 22 documentos institucionais ou normativos, 4 preprints, 2 de fornecedor, 1 de opinião, 1 jornalística.

**Os marcadores com evidência mais forte, em ordem:**

1. Verbos e adjetivos de estilo sem número ao lado — `crucial`, `fundamental`, `robusto`, `abrangente`, `significativo`, `aprofundar-se em`, `ressaltar`. Kobak et al. (Science Advances, 2025) mediram que 66% das palavras em excesso em 2024 são verbos e 14% adjetivos.
2. Nominalização no lugar do verbo ("foi realizada a análise" em vez de "analisamos"): 1,5 a 2 vezes a taxa humana.
3. Oração reduzida de gerúndio no arremate da frase ("..., evidenciando a relevância"): 2 a 5 vezes a taxa humana.
4. Adjetivação avaliativa sem número que a sustente.
5. Frase-resumo de fechamento no padrão "Em conclusão...".
6. Ausência total de marcador epistêmico: a taxa cai de 0,06 no texto humano para 0,00 no GPT-4. É o traço humano mais barato de recuperar — assumir incerteza onde ela existe.
7. Uniformidade de parágrafo, de frase e de seção.

**Três achados que contrariam o próprio ticket e viraram a seção de mitos:**

- LLMs usam **menos** conectivos que humanos (0,36 contra 0,57). "Excesso de conectivos" não é marcador de IA.
- LLMs **sub-usam** voz passiva, a cerca de metade da taxa humana. O ticket supunha o contrário.
- O GPT-4 tem diversidade lexical **maior** que a humana (MTLD 108,91 contra 95,72). "Vocabulário pobre" não é marcador.

**Dois alertas de consequência prática:**

- **Não existe estudo de deriva lexical em corpus acadêmico em português** — nem em espanhol, francês ou alemão. Toda a tabela de vocabulário em português está marcada como inferência transposta do resultado anglófono, não como fato medido. Usar com juízo.
- **Simplificar o texto para "parecer humano" piora a situação**: o falso positivo dos detectores sobe de 5,19% para 56,65%. A estratégia certa é escrever com conteúdo específico e voz própria, não escrever mais simples.

**Achado normativo brasileiro, novo e acionável:** a Portaria CNPq nº 2.664/2026 e a Deliberação Unicamp CONSU-A-005/2026 exigem **declaração explícita de uso de IA** em trabalho acadêmico. Isso entra no ticket 06.
