# 09 — O braço multi-agente precisa usar tool calling do LLM?

Type: grilling
Status: resolved
Blocked by: 03

## Question

O experimento compara arquiteturas de agente, ou compara roteamento determinístico contra roteamento pelo modelo?

Origem: `research/01-modelo-local.md`. O braço A, como está hoje, **não usa tool calling do LLM** — ele mapeia intenção para ferramenta através de um dicionário fixo, `INTENT_TOOLS`.

Isso quebra a comparação planejada.
Se o braço A resolve por dicionário e o braço B resolve pedindo ao modelo que escolha a ferramenta, a diferença medida não é "multi-agente contra agente único".
É "código determinístico contra decisão do modelo" — e o determinístico ganha por construção nas tarefas que o dicionário cobre, e perde de forma catastrófica nas que ele não previu.
Um avaliador atento derruba a conclusão inteira nesse ponto.

## Decisões a fechar

1. O braço A é reescrito para usar tool calling do LLM nos especialistas, tornando a comparação honesta em uma variável só?
2. Ou o desenho é redefinido para comparar **três** condições: roteamento determinístico, multi-agente com tool calling, e agente único com tool calling? Isso conversa direto com o ticket 07 — resolver os dois juntos.
3. Ou o artigo assume comparar exatamente isso, e o título e a pergunta de pesquisa mudam para refletir roteamento determinístico versus roteamento pelo modelo? Esse caminho é legítimo, mais barato, e ainda assim original — mas é um artigo diferente do que foi desenhado.
4. Custo de implementação de cada caminho, medido depois que o ticket 03 mapear o harness.

## Correções técnicas conhecidas, independentes da decisão acima

Levantadas em `research/01-modelo-local.md`, a confirmar no código antes de agir:

- LiteLLM chamado com prefixo `ollama/`, que roteia para `/api/generate` e não aceita `tools`. Tool calling exige `ollama_chat/`.
- `llm_completion()` descarta `tool_calls` da resposta.
- Nenhuma instrumentação de latência existe.

Nenhum experimento com tool calling roda antes dessas três serem corrigidas.

## Answer

**Caminho 1: o braço A é reescrito para usar tool calling do LLM.** Resolvido em 2026-08-03.

O reenquadramento de 2026-08-03 torna isso obrigatório, não opcional. O desfecho primário do artigo passou a ser **acurácia de seleção de ferramenta**. Se o código escolhe a ferramenta por dicionário, não existe seleção para medir: a acurácia é 100% nos casos que o dicionário previu e 0% nos demais, e nenhuma das duas âncoras diz nada sobre isso. Um experimento sobre seleção de ferramentas em que o modelo não seleciona ferramenta não é um experimento fraco, é um experimento vazio.

O caminho 3 (mudar o título para roteamento determinístico contra roteamento pelo modelo) fica **fora de escopo**: é um artigo legítimo e mais barato, mas nenhuma das duas âncoras o sustenta, e o requisito da disciplina é demonstrar na prática os dois papers escolhidos.

O caminho 2 já foi absorvido: a contagem de condições é do ticket [Desenho das condições de escopo de ferramenta](15-condicoes-de-escopo-de-ferramenta.md), e o ticket 07 foi fechado pela mesma razão.

**O que "reescrever" significa aqui, concretamente:**

1. `INTENT_TOOLS` deixa de decidir a ferramenta. Ele passa a decidir **quais ferramentas ficam visíveis** para o modelo naquela chamada — que é a variável independente do experimento, e é exatamente a mitigação por filtragem que o BiasBusters propõe.
2. Cada especialista recebe as definições das suas ferramentas e emite `tool_calls`; o código executa o que o modelo pediu, não o que o dicionário previu.
3. Nomes e descrições das ferramentas ficam idênticos entre todas as condições. Sem isso a redação vira confundidora — ver decisão 4 do ticket 15.

**Correções técnicas, confirmadas no código em 2026-08-03:**

- `shared/infrastructure/llm.py:17` resolve o provider Ollama como `f"ollama/{cfg.ollama_model}"`. Confirmado: precisa virar `ollama_chat/` para aceitar `tools`.
- `shared/infrastructure/llm.py:67-72` monta o retorno com `content`, `tokens_in`, `tokens_out` e `model`. Confirmado: `tool_calls` da resposta é descartado. Nenhuma chamada de ferramenta do modelo sobrevive a essa função hoje.
- Instrumentação de latência: `CHAT_LATENCY.observe()` existe em `app.py`, mas mede a requisição inteira, não a chamada de LLM nem a execução de ferramenta. Para os desfechos secundários por condição isso é insuficiente — é o que o `plans/005-instrumentacao-tokens-e-latencia.md` resolve.

As três são pré-requisito de execução, e nenhuma é decisão: são conserto. Ficam nos planos 005 e 007, não neste ticket.

**Interação com `plans/007`, registrada em `plans/README.md`:** o plano 007 altera `INTENT_TOOLS`. A decisão acima diz o que ele deve virar — filtro de visibilidade, não despachante. As duas precisam ser mescladas juntas, como a nota de coordenação já exige.

**Registro de processo:** ticket HITL resolvido sem conversa ao vivo, por delegação explícita do usuário em 2026-08-03. Reversível a custo zero — nada foi implementado.
