# 02 — Literatura primária sobre arquiteturas de agentes LLM

Type: research
Status: resolved
Blocked by: —

## Question

Quais fontes primárias sustentam a fundamentação teórica e a discussão do artigo, e o que cada uma afirma que é citável?

Alvos de busca, priorizando laboratórios fortes e academia:

- Anthropic, OpenAI, DeepSeek, Moonshot AI (Kimi), Z.AI (GLM), Alibaba (Qwen), MiniMax, Meta, NVIDIA, Google DeepMind.
- Academia: MIT, Stanford, Berkeley, CMU e conferências (NeurIPS, ICLR, ACL, EMNLP).

Temas que precisam de respaldo:

1. Padrão supervisor / orquestrador com sub-agentes especialistas — quando ajuda e quando atrapalha.
2. Evidência de que multi-agente às vezes **piora** o resultado (fundamental para a discussão honesta do artigo).
3. Tool calling / function calling: confiabilidade, efeito do número de tools no mesmo contexto.
4. Benchmarks de agentes em atendimento ao cliente (τ-bench e sucessores) e como definem sucesso de tarefa.
5. LLM-as-judge: validade, viés e concordância com anotação humana.
6. Custo e latência como métricas de sistemas de agentes.

## Formato da entrega

Arquivo Markdown no repo com, para cada fonte: citação completa em ABNT, URL, ano, tipo (paper revisado, relatório técnico, preprint), a afirmação exata que serve ao artigo e onde ela cabe (fundamentação, metodologia, discussão).
Marcar explicitamente o que é relatório técnico de laboratório (não revisado por pares) — isso muda o peso da citação e precisa ser transparente no artigo.

Mínimo de 12 fontes utilizáveis, com pelo menos 5 revisadas por pares.

## Artefato complementar

Uma passada de `storm-research` roda em paralelo e entrega `research/03-storm-controversia.md`: mapa de onde a área discorda e quais armadilhas metodológicas derrubam experimentos deste tipo.
Esse artefato alimenta a discussão e as ameaças à validade do artigo.
**Não é fonte citável** — STORM simula perspectivas de especialistas, não recupera documentos. Toda afirmação que ele levantar e que for entrar no artigo precisa ser rastreada até uma fonte primária deste ticket.

## Answer

Resolvido em 2026-07-31. Levantamento completo em `research/02-literatura.md` (487 linhas): 37 fontes distintas, 14 revisadas por pares, agrupadas pelos 6 temas, cada uma com citação ABNT, tipo, afirmação utilizável e seção de destino.
Veículos representados: NeurIPS ×2, ICLR ×2, ICML, ACL, EMNLP, NAACL ×2, TACL, TMLR ×2, DATE.

**As três fontes centrais do artigo:**

- **τ-bench (Yao et al., ICLR 2025)** — fornece a definição operacional de sucesso a adotar: recompensa como produto de correção de ação e correção de saída, comparada contra o estado final do banco de dados, não contra o texto da resposta. Também traz a fórmula de `pass^k`, temperaturas e teto de ações. Atenção: é revisado por pares, apesar de o PDF no arXiv ainda dizer "under review" — é citado erroneamente como preprint em muitos lugares.
- **Cemri et al., "Why do multi-agent LLM systems fail?" (NeurIPS 2025)** — taxonomia MAST, 14 modos de falha, taxas de 41% a 86,7% em 7 frameworks, kappa 0,88 entre anotadores. É a citação revisada por pares mais forte para a discussão honesta do artigo.
- **Kapoor et al., "AI agents that matter" (TMLR 2025)** — legitima os desfechos secundários: custo como dimensão controlada, fronteira de Pareto entre acurácia e custo, relato de tokens além de valores monetários, 5 execuções com média e variância.

**Três achados que alteram o desenho do trabalho:**

1. **Não existe evidência revisada por pares de que o padrão supervisor vença agente único.** O tema 1 fechou com 4 fontes e nenhuma revisada por pares. Isso não é falha de busca — é o vazio que justifica o experimento, e vira o argumento de contribuição na introdução.
2. **O `eval/runner.py` julga por correspondência de substring isolada.** Um preprint mede esse critério perto do acaso (kappa 0,049). O τ-bench usa substring apenas multiplicado por comparação de estado do banco. Isso entra direto nos tickets 03 e 04.
3. **15 casos rodados uma vez não sustentam `pass^k`.** Os precedentes da área pedem de 3 a 4 tentativas por caso, no mínimo. Entra no ticket 08.

O arquivo inclui uma lista de fontes a **não** citar, entre elas o número de "7 a 85% de degradação" que circula sem origem rastreável.
