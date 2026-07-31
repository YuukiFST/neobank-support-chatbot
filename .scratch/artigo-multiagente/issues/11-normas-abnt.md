# 11 — Normas ABNT aplicáveis a este artigo

Type: research
Status: resolved
Blocked by: —

## Question

Quais normas ABNT regem um artigo científico de 5 a 7 páginas, e o que exatamente cada uma exige na prática?

## Escopo da investigação

Normas provavelmente aplicáveis, a confirmar:

- NBR 6022 — artigo em publicação periódica científica: estrutura, elementos pré-textuais, textuais e pós-textuais.
- NBR 6023 — referências: formato por tipo de fonte. Interessa especialmente o que não é livro: artigo de anais de congresso, preprint em repositório, documentação de software, página web, relatório técnico. Esses são a maioria das fontes deste artigo.
- NBR 10520 — citações: direta curta, direta longa, indireta, citação de citação; sistema autor-data versus numérico.
- NBR 6024 — numeração progressiva das seções.
- NBR 6028 — resumo.
- NBR 6034 — índice, se aplicável.
- Regras de apresentação gráfica: margens, fonte, entrelinhamento, paginação.
- Apresentação de tabelas: a ABNT remete às Normas de Apresentação Tabular do IBGE. O artigo terá tabelas de resultados, então isso importa.
- Distinção entre tabela e quadro, e entre figura e gráfico — erro comum e fácil de evitar.

## Ressalva metodológica obrigatória

As normas ABNT são **documentos pagos** e não estão disponíveis livremente na íntegra.
Guias de bibliotecas universitárias são fonte **secundária**: úteis, comuns, e frequentemente desatualizados ou divergentes entre si.

Regra para este ticket: toda regra registrada deve dizer de onde veio e qual o grau de confiança.
Quando dois guias divergirem, registrar a divergência em vez de escolher em silêncio.
Nunca apresentar paráfrase de guia como se fosse o texto da norma.

## Entrega

Documento em `research/05-normas-abnt.md`, em português, contendo:

- Uma seção por norma, com o que ela exige na prática e um exemplo aplicado a este artigo.
- Modelos de referência prontos para os tipos de fonte que este artigo usa de fato: artigo de anais, preprint arXiv, documentação de software, página web institucional, relatório técnico de empresa.
- Modelos de citação no corpo do texto para os casos que vão aparecer: citação indireta, citação direta curta, citação de dado numérico, citação de fonte sem autoria pessoal.
- Regras de tabela e figura, com um exemplo montado a partir dos resultados previstos deste experimento.
- Checklist de conformidade aplicável antes da entrega.
- Lista explícita do que não foi possível verificar em fonte confiável.

## Answer

Resolvido em 2026-07-31. Documento em `research/05-normas-abnt.md`, 1331 linhas, 16 seções, incluindo modelos prontos para copiar, exemplo de tabela montado com os resultados previstos deste experimento, estrutura de seções para 5 a 7 páginas e checklist de conformidade.

**Normas aplicáveis, nas versões vigentes:** NBR 6022:2018 (estrutura do artigo), **NBR 6023:2025** (referências, 3ª edição de 21.05.2025), **NBR 10520:2023** (citações), NBR 6024:2012 (seções), **NBR 6028:2021** (resumo), e as Normas de Apresentação Tabular do IBGE, 3ª edição de 1993, para tabelas.

**Descartadas, com justificativa:** NBR 6034 (índice remissivo) e NBR 6027 (sumário) são normas de trabalho acadêmico e não constam entre os elementos que a 6022 lista para artigo.
A NBR 14724:2024 não se aplica formalmente — o escopo dela é tese, dissertação e TCC — mas acaba usada por analogia, porque a 6022 §6.1 delega o projeto gráfico "a critério do editor". Sem editor, o autor decide, e deve declarar o que adotou.

**Três divergências entre guias, registradas em vez de resolvidas em silêncio:**

1. **Caixa-alta na citação.** A NBR 10520:2023 §6.1.1.1 exige `(Silva, 2019)`. Guias universitários publicados entre 2020 e 2025 ainda ensinam `(SILVA, 2019)`, que é a regra da versão cancelada de 2002. Seguir a norma vigente.
2. **Gráfico e figura.** A USP trata figura como termo genérico que engloba gráfico; a NBR 14724 §5.8 lista os dois como itens paralelos de uma lista aberta. A norma não arbitra — o autor escolhe e mantém a escolha coerente.
3. **Espaçamento entre linhas.** A 6022 pede simples; a 14724 pede 1,5. Guias que aplicam a 14724 a um artigo importam o 1,5 indevidamente.

**Duas zonas cinzentas de consequência direta para este artigo:**

- A NBR 6023:2025 **não tem categoria para preprint** — a palavra não aparece uma única vez na norma — **nem para documentação de software**. Nenhum guia brasileiro cobre arXiv.
- A maioria das fontes deste artigo é exatamente disso: preprint do arXiv, documentação de software e relatório técnico de empresa. O documento registra as opções concorrentes para cada caso e declara a recomendação como inferência, não como regra normativa.

**Alerta operacional:** o gerador MORE, da UFSC, ainda opera na NBR 6023:2018. Referência gerada por ele precisa de conferência manual.
