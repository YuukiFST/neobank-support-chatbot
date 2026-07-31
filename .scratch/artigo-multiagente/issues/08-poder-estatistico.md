# 08 — Tamanho da amostra e teste estatístico

Type: grilling
Status: open
Blocked by: 04, 07

## Question

Quantos casos, quantas repetições, e qual teste estatístico sustentam a conclusão do artigo?

Graduado da névoa depois de `research/03-storm-controversia.md`, que trouxe os números que tornam a pergunta especificável.

## Restrições numéricas levantadas

- O dataset atual tem 15 casos.
- Com 15 casos pareados, o teste de McNemar exato exige cerca de 6 pares discordantes na mesma direção para chegar a p ≈ 0,031. Traduzindo: o desenho atual só detecta diferenças enormes, da ordem de 40 pontos percentuais, enquanto a literatura discute diferenças de 4 a 6 pontos.
- Um resultado de 12 acertos em 15 tem intervalo de confiança de Wilson a 95% aproximadamente entre 55% e 98% — largo demais para afirmar qualquer coisa.

Esses números precisam ser reconferidos na resolução, não aceitos de saída: vieram de um artefato STORM, que não é fonte citável.

## Decisões a fechar

1. Quantos cenários de teste no total, e quem os escreve sem viés a favor de um arm.
2. Quantas repetições por cenário. A saída sugerida pelo STORM é reportar `pass^k` com k ≥ 5, que mede consistência e não só acerto médio.
3. Qual teste: McNemar pareado, bootstrap sobre a diferença, ou intervalo de confiança sem teste de hipótese. Com amostra pequena, declarar honestamente que o estudo é exploratório pode ser mais defensável que forçar um p-valor.
4. Se o artigo assume ser exploratório: como isso é escrito na metodologia e nas limitações sem enfraquecer a contribuição.
5. Validação do juiz: o STORM sugere 30 a 50 casos anotados manualmente pelo autor, com kappa de concordância declarado. Confirmar o número e o limiar aceitável junto com o ticket 04.

## Answer

<!-- preencher na resolução -->
