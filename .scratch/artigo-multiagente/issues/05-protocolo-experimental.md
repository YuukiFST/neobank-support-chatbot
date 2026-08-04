# 05 — Protocolo experimental

Type: grilling
Status: open
Blocked by: 04, 08, 09, 14, 15, 16

## Question

Qual o protocolo exato do experimento, escrito no nível de detalhe que permite outra pessoa reproduzir?

Decisões a fechar:

1. O que é mantido idêntico entre os dois arms: modelo, temperatura, seed, prompts de domínio, tools disponíveis, dados do banco, ordem dos casos.
2. Qual é exatamente o arm B — um agente único com todas as tools e um system prompt consolidado, ou variantes. Como o prompt do arm B é derivado dos prompts existentes sem favorecer nenhum arm.
3. Número de repetições por caso e justificativa (LLM é estocástico; uma passada só não sustenta conclusão).
4. Tamanho final do dataset: os 15 casos atuais bastam, ou precisa ampliar. Se ampliar, quem escreve os casos novos e como o gabarito é definido sem viés.
5. Ordem de execução e isolamento entre casos (estado do banco, memória de conversa, cache).
6. O que é registrado por execução: saída bruta, rota tomada, tools chamadas, tokens, latência, timestamps.
7. Como o custo é estimado, já que o modelo roda local (custo em tokens equivalentes de API, ou custo de energia/tempo de GPU) — decidir e justificar.
8. Critério de descarte de execução (timeout, erro de infraestrutura) e como isso é reportado.

## Duas ameaças que o STORM identificou como fatais para este desenho

Origem: `research/03-storm-controversia.md`.

**9. Orçamento de compute não igualado.**
Se o arm multi-agente faz 3 a 5 chamadas ao modelo e o arm único faz 1 ou 2, o experimento mede orçamento de tokens, não arquitetura.
Esta é a crítica central da literatura recente contra trabalhos pró-multi-agente, e não tem defesa depois do fato.
Decidir: rodar um arm de controle com compute igualado (por exemplo, agente único com auto-consistência em k amostras, consumindo tokens equivalentes), ou reportar o resultado explicitamente como comparação a custo desigual.

**10. Esforço de prompt assimétrico.**
O prompt do supervisor foi iterado ao longo do projeto; um prompt de arm único escrito às pressas perde por falta de trabalho, não por arquitetura.
Decidir o protocolo que garante simetria: mesmo número de iterações de refino em cada arm, refino cego contra um conjunto de desenvolvimento separado do conjunto de teste, e registro de quantas iterações cada arm recebeu.

**11a. Quantização como variável de confusão.**
Levantado em `research/01-modelo-local.md`: comprimir o modelo degrada seletivamente tool calling multi-turno, que é a capacidade sob teste.
A quantização fica fixa e declarada entre os braços.
Como o Qwen3.5-9B cabe nos 12 GB até em Q8_0, existe a opção de rodar Q4 como condição de operação e Q8 como controle — decidir se isso cabe no orçamento de execuções e nas 5 a 7 páginas.

**11b. Fragilidade a formato de prompt.**
A família Qwen oscila de 14 a 18 pontos no BFCL V4 só com mudança de formatação do prompt.
Os dois braços usam prompts diferentes por construção, então parte da diferença medida pode ser sensibilidade a formato, não arquitetura.
Decidir como isso é controlado ou, no mínimo, declarado nas limitações.

**11c. O sistema é de turno único, e o τ-bench não é.**
Verificado em 2026-07-31: `services/agent_api/interface/app.py:234` monta o estado com uma única mensagem por requisição, e o grafo é compilado sem checkpointer.
Não existe memória entre turnos.
O τ-bench, adotado como referência de protocolo no ticket 04, avalia tarefas **multi-turno**.
Decidir: ou o experimento se restringe a tarefas de turno único e declara isso como limitação e como desvio do protocolo de referência, ou implementar memória de conversa vira pré-requisito — o que aumenta o escopo e muda o custo de tokens por turno.

**11. Contaminação de latência por VRAM.**
Se os especialistas forem instâncias separadas do modelo que não cabem simultaneamente em 12 GB, a latência medida é troca de modelo na VRAM, não custo de arquitetura.
Decidir: uma única instância servindo todos os agentes, e verificar isso no ticket de modelo local.

## Answer

<!-- preencher na resolução -->
