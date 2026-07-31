# 09 — O braço multi-agente precisa usar tool calling do LLM?

Type: grilling
Status: open
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

<!-- preencher na resolução -->
