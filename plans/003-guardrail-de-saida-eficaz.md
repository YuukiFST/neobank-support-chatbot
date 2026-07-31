# Plano 003: Fazer o guardrail de saída realmente bloquear a resposta

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- services/agent_api/interface/app.py services/agent_api/application/agent.py`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: MED — muda o contrato de streaming do endpoint `/chat`
- **Depende de**: `plans/002-ci-roda-todas-as-suites.md`
- **Categoria**: bug
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

O guardrail de saída é o controle de segurança principal do projeto e está **inerte**.
A resposta do especialista já foi transmitida ao cliente quando o guardrail roda, então o texto de bloqueio chega **anexado** à resposta violadora, não no lugar dela.

Na prática: o cliente lê o conteúdo que deveria ser bloqueado e, logo em seguida, lê "I'm sorry, I cannot provide that information."
Seis testes unitários exercitam esse guardrail e todos passam, porque testam a função pura e não o caminho real.

O mesmo defeito produz um segundo sintoma no caminho feliz: numa disputa de fraude, o cliente recebe a análise do especialista de risco seguida imediatamente do texto de escalação, concatenados na mesma bolha.

## Estado atual

O laço de streaming em `services/agent_api/interface/app.py:261-266` emite a resposta de **cada nó**, conforme cada um completa:

```python
                        if node_output.get("response"):
                            response_text = node_output["response"]
                            for i in range(0, len(response_text), 10):
                                chunk = response_text[i:i + 10]
                                yield f"data: {json.dumps({'type': 'token', 'data': chunk})}\n\n"
                            response_streamed = True
```

O nó de guardrail em `services/agent_api/application/agent.py:203-214`:

```python
async def node_guardrail_out(state: AgentState) -> dict:
    """Post-LLM guardrail: check response for leaks and advice."""
    response = state.get("response", "")
    result = guardrail_out(response, state.get("customer_document", ""))
    log.info("guardrail_out", passed=result.passed, reason=result.reason)

    if not result.passed:
        return {
            "response": "I'm sorry, I cannot provide that information. Let me connect you with a human agent.",
            "guardrail_out_result": {"passed": False, "reason": result.reason},
        }
    return {"guardrail_out_result": {"passed": True}}
```

Dois fatos que tornam a correção barata:

1. **O streaming atual já é falso.** `shared/infrastructure/llm.py:51` usa `litellm.acompletion` sem `stream=True`, e o laço acima fatia uma string **já completa** em pedaços de 10 caracteres.
   Não existe streaming token a token para preservar. Bufferizar não custa nada em experiência real.
2. O nó `escalation` (`agent.py:200`) também define `response`, e `risk_specialist → escalation` é uma aresta do grafo (`agent.py:284`) — é daí que vem a resposta dupla na disputa de fraude.

O front-end concatena todos os frames `token` (`frontend/app.py:101-103`), então herda o mesmo defeito.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Testes offline | `pytest tests/ -v -m "not requires_db"` | executa |
| Só e2e | `pytest tests/e2e -v` | passa ao final do plano |
| Lint | `ruff check .` | exit 0 |

## Escopo

**Em escopo**:

- `services/agent_api/interface/app.py` — apenas o gerador `event_stream`
- `tests/e2e/test_chat_flow.py` — novo teste de regressão
- `tests/unit/test_agent_graph.py` — teste do nó, se necessário

**Fora de escopo**:

- `services/agent_api/infrastructure/guardrails.py`. As heurísticas do guardrail têm problemas próprios (denylist só em inglês, três padrões de PII definidos e nunca usados), mas isso é outro plano. Aqui só se corrige **quando** o guardrail age, não **o que** ele detecta.
- Implementar streaming real de token via `stream=True`. É desejável e tem plano próprio; misturar as duas mudanças torna impossível revisar qualquer uma.
- `frontend/app.py` — ele se corrige sozinho quando o servidor parar de emitir respostas parciais.

## Fluxo git

- Branch: `advisor/003-guardrail-saida`
- Conventional Commits em inglês. Exemplo: `fix(chat): emit response only after output guardrail runs`

## Passos

### Passo 1: acumular a resposta em vez de emitir por nó

No gerador `event_stream` de `app.py`, remova a emissão dos frames `token` de dentro do laço `async for` sobre `astream`.
Em vez disso, guarde a resposta acumulada.

O estado acumulado já existe no gerador (a variável `accumulated`, usada em outros pontos do laço), então use-a como fonte da resposta final.

Mantenha inalterados dentro do laço: o frame `tool` do roteador (`app.py:257-259`) e o tratamento de `handoff`.
Esses são eventos de progresso legítimos e não são a resposta ao usuário.

**Verificar**: `grep -n "type': 'token'" services/agent_api/interface/app.py` → as ocorrências restantes estão **fora** do laço `async for`.

### Passo 2: emitir a resposta final uma única vez, após o grafo terminar

Depois que o `async for` completar, pegue a resposta final do estado acumulado e emita os frames `token` a partir dela — pode manter o fatiamento de 10 caracteres, que produz o efeito de máquina de escrever no front-end.

Em seguida emita o frame `done`, como já acontece hoje.

O caminho de fallback existente em `app.py:294` (quando nenhuma resposta foi produzida) deve continuar funcionando: se a resposta final for vazia, emita o texto de fallback.

**Verificar**: `pytest tests/e2e -v` → executa; a conversa continua produzindo frames `token`.

### Passo 3: escrever o teste de regressão que prova o bloqueio

Em `tests/e2e/test_chat_flow.py`, adicione um teste que:

1. Força o dublê de LLM (`tests/support/mock_llm.py`) a devolver uma resposta que viola o guardrail de saída.
   Consulte `services/agent_api/infrastructure/guardrails.py` para descobrir o que é detectado hoje — na prática, um CPF diferente do CPF do cliente da sessão.
2. Faz a requisição a `/chat` e concatena o conteúdo de todos os frames `token`.
3. Afirma que o texto violador **não** aparece na saída, e que o texto de bloqueio aparece.

Essa asserção deve **falhar** no código anterior ao passo 1 e passar depois.
Se ela passar antes da correção, sua reprodução está errada: refaça antes de continuar.

**Verificar**: `pytest tests/e2e -v -k guardrail` → passa. E, com `git stash` da correção, o mesmo teste falha.

### Passo 4: verificar o caso da resposta dupla na fraude

O caminho `risk_specialist → escalation` define `response` duas vezes.
Com a correção do passo 2, apenas a resposta final do estado acumulado é emitida.

Decida e documente qual deve prevalecer:

- Se a intenção é o cliente ver a análise **e** a nota de escalação, o nó `escalation` deve **compor** o texto (anexar à resposta existente do estado), não sobrescrevê-lo.
- Se a intenção é só a nota de escalação, o comportamento atual do estado acumulado já basta.

Escolha uma, implemente, e escreva um comentário de uma linha no nó explicando a decisão.

**Verificar**: `pytest tests/ -v -m "not requires_db"` → executa; adicione um teste que exercita o fluxo de `fraud_dispute` e afirma que existe exatamente um bloco de resposta coerente.

## Plano de teste

- **Novo teste de regressão** em `tests/e2e/test_chat_flow.py`: resposta violadora nunca alcança o cliente. Este é o teste que dá nome ao plano.
- **Novo teste** para o fluxo de `fraud_dispute`, afirmando o formato de resposta única decidido no passo 4.
- Use `tests/e2e/test_chat_flow.py` como padrão estrutural — o mesmo estilo de fixture `e2e_client`.
- Verificação: `pytest tests/ -v -m "not requires_db"` → passa, incluindo os dois testes novos.

## Critérios de pronto

- [ ] `pytest tests/ -m "not requires_db"` sai com código 0
- [ ] Existe teste que falha sem a correção e passa com ela (comprove no relatório final com a saída dos dois casos)
- [ ] Nenhum frame `token` é emitido de dentro do laço `async for` (`grep -n` comprovando)
- [ ] `ruff check .` sai com código 0
- [ ] Nenhum arquivo fora do escopo modificado (`git status`)
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- O trecho de `app.py:261-266` não corresponder ao citado em "Estado atual".
- O teste de regressão do passo 3 passar **antes** da correção — sua reprodução não reproduz o bug.
- A correção exigir mudar `guardrails.py` para funcionar.
- Você descobrir que existe streaming real de token em algum caminho (ou seja, que `stream=True` foi introduzido desde a escrita deste plano). Nesse caso, a estratégia de bufferizar precisa ser reavaliada por quem tomou aquela decisão.

## Notas de manutenção

- **Se um dia o streaming real for implementado**, este é o ponto de tensão: guardrail pós-resposta e streaming token a token são incompatíveis por natureza. As opções são bufferizar (perdendo o streaming), validar em janelas com política de retratação, ou aceitar o risco explicitamente. A decisão precisa ser registrada, não improvisada.
- Um revisor deve confirmar que nenhum caminho de erro voltou a emitir resposta parcial, e que o frame `done` continua sendo emitido em todos os caminhos, inclusive no `except`.
- O front-end Streamlit não precisa de mudança, mas vale verificar visualmente que o efeito de digitação continua funcionando.
