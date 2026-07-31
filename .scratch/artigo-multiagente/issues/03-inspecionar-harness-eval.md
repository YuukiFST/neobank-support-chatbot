# 03 — O que o harness de avaliação atual já faz

Type: task
Status: open
Blocked by: —

## Question

O que `eval/eval_set.jsonl` e `eval/runner.py` já medem, e o que falta para servirem ao experimento do artigo?

Fatos já conhecidos do charting: o dataset tem 15 casos; existe `prompts/judge.md`, indicando LLM-as-judge já implementado.

A levantar:

1. Formato exato de cada caso no JSONL: campos, expectativa de resposta, expectativa de tool, expectativa de rota.
2. Cobertura dos 9 intents pelos 15 casos — quantos casos por intent, quais intents ficam descobertos.
3. Cobertura bilíngue (português e inglês) no dataset.
4. O que `runner.py` calcula hoje: acerta o quê, reporta o quê, grava onde.
5. Se latência, tokens de entrada e saída, e chamadas de tool já são instrumentados. Se não, onde entram.
6. Como `judge.md` define sucesso hoje, e se essa definição serve como desfecho primário do artigo.
7. Quão acoplado o runner está à arquitetura multi-agente — ou seja, quanto trabalho é apontá-lo para um arm de agente único.

## Formato da entrega

Relatório curto no ticket com referências `arquivo:linha`, mais uma lista do que precisa ser construído para o experimento.

## Answer

<!-- preencher na resolução -->
