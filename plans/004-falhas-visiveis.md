# Plano 004: Parar de disfarçar falha de infraestrutura como resposta válida

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- shared/infrastructure/llm.py shared/infrastructure/chroma_client.py services/agent_api/application/tools.py services/agent_api/application/agent.py`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: LOW — no pior caso um erro honesto substitui uma resposta falsa
- **Depende de**: `plans/002-ci-roda-todas-as-suites.md`
- **Categoria**: bug
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

Três camadas do sistema transformam falha de infraestrutura em resposta aparentemente normal, com HTTP 200 e sem nenhum sinal em log ou métrica.

Num contexto bancário, isso significa afirmar fatos financeiros falsos a um cliente por causa de um backend fora do ar.
O caso mais grave: quando o provedor de LLM cai, **toda** conversa é classificada como `human` e escalada, gravando escalações falsas na tabela `handoffs`, indistinguíveis das reais — a fila do atendente humano enche de lixo e ninguém percebe.

Este plano não adiciona resiliência (retry, backoff, circuit breaker). Ele apenas torna a falha **visível e distinguível** do sucesso.

## Estado atual

### Falha 1 — LLM

`shared/infrastructure/llm.py:58-65`:

```python
    except Exception as exc:
        return {
            "content": "I'm sorry, I'm having trouble connecting to the AI service. Please try again shortly.",
            "tokens_in": 0,
            "tokens_out": 0,
            "model": model,
            "error": str(exc),
        }
```

A chave `error` é escrita e **nenhum chamador a lê** em todo o repositório.
O roteador (`services/agent_api/application/agent.py:105-118`) recebe essa desculpa, não encontra o JSON esperado, e cai no padrão `intent = "human"`.
O especialista (`agent.py:153-161`) devolve a desculpa como resposta normal.

Risco adicional: a mensagem de exceção do LiteLLM costuma conter o `api_base` e o nome do modelo, e está sentada numa estrutura que viaja junto com o conteúdo da resposta.

### Falha 2 — ferramentas

`services/agent_api/application/tools.py:173-176` converte qualquer exceção em `f"Tool {name} failed: {exc}"` e anexa aos resultados.
Esses resultados são injetados em `agent.py:140-145` sob o cabeçalho `[Tool results — use ONLY this data]`, acima de um prompt que instrui o modelo a **nunca** fabricar dado financeiro e a usar apenas o que as ferramentas retornaram.

Pior caso concreto: `tools.py:58-65` captura `HTTPException` de forma ampla, então o 500 ou 504 injetado por `mock_banking_api.py:88-89` é reportado ao cliente como o fato de negócio **"No open invoice found for this card."**

### Falha 3 — base de conhecimento

`shared/infrastructure/chroma_client.py:44-45`:

```python
    except Exception:
        return []
```

Chroma fora do ar, coleção vazia, partição de rede e "nada relevante encontrado" produzem exatamente o mesmo resultado.
O especialista de FAQ então responde sem nenhuma recuperação, enquanto o prompt afirma que há contexto recuperado abaixo.

### Métricas já declaradas e nunca usadas

`shared/infrastructure/observability.py:35-36` define `KB_RETRIEVALS` e `KB_CACHE_HITS`, ambos nunca incrementados.
O padrão de logging do projeto é `structlog` com chaves nomeadas — veja `agent.py:207` (`log.info("guardrail_out", passed=..., reason=...)`) e siga esse estilo.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Testes offline | `pytest tests/ -v -m "not requires_db"` | passa ao final |
| Lint | `ruff check .` | exit 0 |
| Tipos | `mypy shared/ services/` | exit 0 |

## Escopo

**Em escopo**:

- `shared/infrastructure/llm.py`
- `shared/infrastructure/chroma_client.py`
- `services/agent_api/application/tools.py`
- `services/agent_api/application/agent.py` — apenas o tratamento do estado de erro
- `shared/infrastructure/observability.py` — apenas para adicionar contadores de erro
- Testes novos em `tests/unit/`

**Fora de escopo**:

- Retry, backoff, circuit breaker, timeout configurável. O projeto não declarou precisar dessas categorias; adicioná-las por conta própria é escopo inventado.
- Corrigir a incompatibilidade de embedding do Chroma. É o plano 006. Aqui só se torna o erro **visível**; lá ele é **corrigido**.
- `services/agent_api/interface/app.py`, exceto se o passo 4 exigir — e nesse caso, apenas o mínimo.

## Fluxo git

- Branch: `advisor/004-falhas-visiveis`
- Conventional Commits em inglês. Exemplo: `fix(llm): surface provider failures instead of returning an apology`

## Passos

### Passo 1: tornar a falha de LLM distinguível

Em `shared/infrastructure/llm.py`, no bloco `except`:

1. Logue o erro com `log.error("llm_call_failed", provider=..., model=model, error=str(exc))`, seguindo o estilo de logging já usado no projeto.
2. Substitua a chave `error` com o texto cru da exceção por um código opaco (por exemplo `"error": "llm_unavailable"`), para que a mensagem do provedor não viaje junto com a resposta.
3. Mantenha a estrutura de retorno com as mesmas chaves, para não quebrar chamadores — mas marque claramente o resultado como falho.

Adicione um contador em `shared/infrastructure/observability.py`, seguindo o padrão dos existentes:

```python
LLM_ERRORS = Counter("neobank_llm_errors_total", "Total LLM call failures", ["provider"])
```

**Verificar**: `pytest tests/unit -v -k llm` → passa, incluindo o teste novo do passo 5.

### Passo 2: fazer o roteador distinguir falha de intent legítimo

Em `agent.py`, no nó do roteador: quando o retorno de `llm_completion` indicar falha, **não** classifique como `intent = "human"`.
Defina o campo `error` do `AgentState` (ele já existe — veja o estado inicial montado em `services/agent_api/interface/app.py:232-247`, que inclui `"error": None`).

O objetivo é que escalação genuína e falha de provedor sejam separáveis nos dados.
Registre no relatório final como o grafo passou a se comportar nesse caso.

**Verificar**: `pytest tests/ -v -m "not requires_db"` → executa; um teste novo cobre esse caminho.

### Passo 3: parar de mascarar 500 como 404 nas ferramentas

Em `services/agent_api/application/tools.py`, na função `get_invoice` (por volta da linha 58): capture `HTTPException` **apenas** quando `status_code == 404`.
Qualquer outro status deve propagar ou ser tratado como falha explícita.

No tratador genérico de `execute_tools_for_intent` (por volta da linha 173): em vez de anexar `f"Tool {name} failed: {exc}"` aos resultados que vão para o prompt, logue o erro, incremente um contador de falha de ferramenta, e marque o estado como degradado.

O texto que chega ao modelo deve dizer que um sistema está indisponível — nunca um fato de negócio inventado.

**Verificar**: `pytest tests/unit -v -k tool` → passa, incluindo os testes novos.

### Passo 4: separar "Chroma falhou" de "nada encontrado"

Em `shared/infrastructure/chroma_client.py`, no `except Exception` de `query_kb`:

1. Logue com `log.error("kb_query_failed", error=str(exc))`.
2. Incremente um contador de erro de KB.
3. Sinalize a falha de forma que o chamador consiga distinguir de lista vazia legítima — por exemplo, propagando a exceção, ou retornando um resultado que carregue esse estado.

Incremente `KB_RETRIEVALS` no caminho de sucesso — ele já existe e nunca foi usado.

Em `agent.py`, ao redor da linha 136, faça o especialista de FAQ saber que a recuperação falhou, para que possa dizer que não consegue consultar agora em vez de responder de memória.

**Verificar**: `pytest tests/unit -v -k kb` → passa.

### Passo 5: escrever os testes que provam cada falha

Ver "Plano de teste". Cada um deve falhar sem a correção correspondente.

**Verificar**: `pytest tests/ -v -m "not requires_db"` → passa, com os testes novos.

## Plano de teste

Novos testes, em `tests/unit/`, seguindo o padrão estrutural de `tests/unit/test_tools.py`:

1. `llm_completion` com o provedor lançando exceção: o retorno é marcado como falho e o contador de erro incrementa.
2. Roteador recebendo um retorno de LLM falho: o estado sai com `error` definido, e **não** com `intent == "human"`.
3. `get_invoice` diante de um 500: não retorna a string "No open invoice found"; sinaliza falha.
4. `get_invoice` diante de um 404 genuíno: continua retornando o caso de "nenhuma fatura aberta", porque esse é o comportamento correto.
5. `query_kb` com o cliente Chroma lançando exceção: falha é distinguível de lista vazia.

O item 4 é essencial: ele impede que a correção do item 3 vá longe demais.

Verificação: `pytest tests/ -v -m "not requires_db"` → todos passam, incluindo os 5 novos.

## Critérios de pronto

- [ ] `pytest tests/ -m "not requires_db"` sai com código 0, com pelo menos 5 testes novos
- [ ] `grep -rn "Tool {name} failed" services/` não retorna nada, ou retorna apenas dentro de um caminho de log
- [ ] `grep -n "except Exception:" shared/infrastructure/chroma_client.py` não retorna mais um `except` que só devolve lista vazia sem logar
- [ ] `mypy shared/ services/` sai com código 0
- [ ] `ruff check .` sai com código 0
- [ ] Nenhum arquivo fora do escopo modificado (`git status`)
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- Os trechos de "Estado atual" não corresponderem ao código vivo.
- Tornar a falha visível exigir mudança no contrato HTTP do endpoint `/chat` (por exemplo, passar a responder 503). Essa é decisão de produto: reporte a necessidade em vez de decidir sozinho.
- Um teste novo passar antes da correção correspondente.
- A correção do passo 3 fizer o caso legítimo de "nenhuma fatura aberta" parar de funcionar. Nesse caso, você foi longe demais: o teste 4 do plano de teste existe exatamente para pegar isso.

## Notas de manutenção

- Este plano estabelece a fronteira entre "erro" e "resposta". Qualquer `except` novo no projeto deve seguir a mesma regra: falha de infraestrutura nunca vira texto para o modelo nem para o cliente.
- Um revisor deve procurar por `except Exception` remanescentes que devolvam valor de sucesso — esse é o padrão que este plano combate, e ele aparece em mais lugares que os quatro citados.
- Deliberadamente adiado: o `except Exception` único e amplo em `app.py:313-316`, que cobre o grafo inteiro, a escrita do handoff e a das métricas, tornando indistinguível uma falha de INSERT de uma falha do LLM. Merece plano próprio junto com a decomposição de `app.py`.
