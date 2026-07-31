# Plano 005: Instrumentar tokens, latência e chamadas de ferramenta ponta a ponta

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- services/agent_api/application/agent.py services/agent_api/interface/app.py shared/infrastructure/observability.py shared/infrastructure/llm.py`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: LOW — adiciona observação, não muda comportamento
- **Depende de**: `plans/004-falhas-visiveis.md`
- **Categoria**: perf
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

O projeto já produz os números de token e os descarta.
Quatro métricas Prometheus e três colunas de banco existem para recebê-los e ficam permanentemente em zero.
O README promete rastreamento de custo por sessão, e o painel Grafana provisionado tem `"panels": []`.

Além do débito em si, este plano é **pré-requisito de um experimento científico** que o dono do projeto vai conduzir sobre este repositório, comparando arquitetura multi-agente contra agente único.
Os desfechos secundários desse experimento são latência p50 e p95, tokens de entrada e saída, e custo estimado.
Sem esta instrumentação, o experimento não tem o que medir.

Por isso este plano tem um requisito incomum: além das métricas agregadas, ele precisa produzir um **registro por execução**, com granularidade suficiente para análise posterior.

## Estado atual

Os tokens **já existem** no retorno do gateway de LLM — `shared/infrastructure/llm.py`, no caminho de sucesso:

```python
    return {
        "content": response.choices[0].message.content or "",
        "tokens_in": response.usage.prompt_tokens if response.usage else 0,
        "tokens_out": response.usage.completion_tokens if response.usage else 0,
```

E são logados em `services/agent_api/application/agent.py:117` e `:154-159` — depois disso, descartados.

Métricas declaradas em `shared/infrastructure/observability.py:29-36`:

```python
CHAT_REQUESTS = Counter("neobank_chat_requests_total", "Total chat requests", ["intent", "language"])
CHAT_TOKENS_IN = Counter("neobank_chat_tokens_in_total", "Total input tokens")
CHAT_TOKENS_OUT = Counter("neobank_chat_tokens_out_total", "Total output tokens")
CHAT_LATENCY = Histogram("neobank_chat_latency_seconds", "Chat request latency", buckets=[0.5, 1, 2, 5, 10, 30])
ACTIVE_SESSIONS = Gauge("neobank_active_sessions", "Active sessions")
ESCALATIONS = Counter("neobank_escalations_total", "Total escalations", ["intent"])
KB_RETRIEVALS = Counter("neobank_kb_retrievals_total", "KB retrieval calls")
KB_CACHE_HITS = Counter("neobank_kb_cache_hits_total", "KB cache hits")
```

Destas, `CHAT_TOKENS_IN`, `CHAT_TOKENS_OUT`, `KB_RETRIEVALS` e `KB_CACHE_HITS` nunca são incrementadas.

A persistência de métricas em `services/agent_api/interface/app.py:302-311` grava apenas duas colunas:

```python
                        "INSERT INTO session_metrics (session_id, turns, latency_p95_ms, updated_at) "
                        "VALUES (:session_id, 1, :latency, NOW()) "
                        "ON CONFLICT (session_id) DO UPDATE SET turns = session_metrics.turns + 1, latency_p95_ms = :latency, updated_at = NOW()"
```

A tabela `session_metrics` (`ops/init.sql:90-92`) tem `tokens_in`, `tokens_out` e `cost_brl_equiv`, sempre zeradas.

Dois defeitos adicionais de métrica, ambos em escopo:

- `app.py:195` chama `ACTIVE_SESSIONS.inc()` e **não existe `.dec()` em lugar nenhum** — o gauge só sobe.
- A coluna se chama `latency_p95_ms` mas recebe a latência **da última requisição**, não um percentil. O nome mente.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Testes offline | `pytest tests/ -v -m "not requires_db"` | passa |
| Lint | `ruff check .` | exit 0 |
| Tipos | `mypy shared/ services/` | exit 0 |

## Escopo

**Em escopo**:

- `shared/infrastructure/observability.py`
- `services/agent_api/application/agent.py` — acumulação no estado
- `services/agent_api/interface/app.py` — persistência e gauge
- `ops/init.sql` — apenas se o passo 5 exigir coluna nova
- `eval/runner.py` — para gravar o registro por execução
- Testes novos

**Fora de escopo**:

- Implementar streaming real para medir tempo até o primeiro token. É desejável para o experimento, mas depende de mudar o gateway de LLM e o contrato de streaming; tem plano próprio.
- Integrar Langfuse. A dependência está declarada e não é importada por nenhuma linha; a decisão entre adotar ou remover é do dono do projeto.
- Calcular custo real em moeda. Registre tokens; a conversão para custo é decisão de negócio e muda por provedor.

## Fluxo git

- Branch: `advisor/005-instrumentacao`
- Conventional Commits em inglês. Exemplo: `feat(observability): record token usage and per-run latency`

## Passos

### Passo 1: acumular tokens no estado do grafo

O `AgentState` precisa carregar os totais de token da execução.
Adicione os campos ao estado e faça cada chamada de LLM somar seus `tokens_in` e `tokens_out` ao acumulado — tanto a chamada do roteador quanto a do especialista.

Cuidado: o merge de estado do grafo (`agent.py`, função `merge_graph_state`) descarta valores `None`.
Garanta que a acumulação some, e não sobrescreva, quando dois nós reportarem tokens na mesma execução.

**Verificar**: `pytest tests/unit -v -k token` → passa, com um teste que executa o grafo com o dublê de LLM e afirma que o total acumulado é a soma das duas chamadas.

### Passo 2: incrementar as métricas Prometheus que já existem

Em `app.py`, ao final do fluxo de chat, incremente `CHAT_TOKENS_IN` e `CHAT_TOKENS_OUT` com os totais acumulados.
Incremente `KB_RETRIEVALS` no caminho de sucesso da recuperação — se o plano 004 já tiver feito isso, apenas confirme.

**Verificar**: após uma requisição de chat, `curl -s localhost:8000/metrics | grep neobank_chat_tokens` → mostra valor maior que zero.
Se você não puder subir o serviço, escreva um teste que chame o handler e leia o valor do contador diretamente do objeto Prometheus.

### Passo 3: corrigir o gauge de sessões ativas

`ACTIVE_SESSIONS` só incrementa.
Decida a semântica correta e implemente:

- Se "ativa" significa sessão criada e não encerrada, é preciso um ponto de decremento — e não existe endpoint de encerramento hoje. Nesse caso, ou se cria o conceito de expiração, ou a métrica deve ser um `Counter` de sessões criadas, não um `Gauge`.
- **Recomendação**: trocar por `Counter` chamado `neobank_sessions_created_total`, que é honesto e não exige inventar ciclo de vida.

Documente a escolha num comentário de uma linha.

**Verificar**: `grep -rn "ACTIVE_SESSIONS" services/ shared/` → o uso é coerente com a escolha; não sobra gauge que só sobe.

### Passo 4: corrigir o nome enganoso da coluna de latência

A coluna `latency_p95_ms` recebe a latência da última requisição.
Como renomear coluna exige migração e não há sistema de migração no projeto, faça o mínimo honesto:

- Grave a latência da requisição atual numa coluna com nome correto, e/ou
- Adicione um comentário no SQL do `INSERT` explicando que o valor é o da última requisição, não um percentil.

Se você optar por adicionar coluna nova a `ops/init.sql`, saiba que o arquivo só roda quando o volume do Postgres está vazio — registre isso no relatório final como limitação.

**Verificar**: `grep -n "latency" services/agent_api/interface/app.py` → o código não afirma percentil onde grava valor único.

### Passo 5: persistir tokens em `session_metrics`

Estenda o `INSERT ... ON CONFLICT` de `app.py:302-311` para gravar também `tokens_in` e `tokens_out`, **somando** no conflito, do mesmo jeito que `turns` já soma.

Deixe `cost_brl_equiv` de fora, ou grave zero com um comentário: a conversão de token para moeda depende do provedor e é decisão de negócio.

**Verificar**: teste de integração (marcado `requires_db`) que faz duas requisições na mesma sessão e afirma que `tokens_in` acumulou as duas.

### Passo 6: registro por execução para o experimento

Este passo existe para o experimento científico e é o mais importante do plano.

Em `eval/runner.py`, faça cada caso avaliado gravar uma linha estruturada num arquivo JSONL de saída, contendo no mínimo:

- identificador do caso
- carimbo de tempo do início e do fim
- latência total em milissegundos
- `tokens_in` e `tokens_out`
- intent roteado
- lista de ferramentas efetivamente executadas
- se houve escalação
- se houve erro, e qual código
- identificador do modelo e do provedor

Um objeto JSON por linha, um arquivo por execução do runner, com o nome carregando data e hora.
Não agregue nada neste arquivo: agregação é análise, e análise acontece depois.

**Verificar**: rodar o runner produz um arquivo JSONL cujo número de linhas é igual ao número de casos, e `python -c "import json,sys; [json.loads(l) for l in open(ARQUIVO)]"` roda sem erro.

## Plano de teste

Novos testes seguindo o padrão de `tests/unit/test_tools.py` e `tests/unit/test_agent_graph.py`:

1. Acumulação de tokens no estado com duas chamadas de LLM: o total é a soma.
2. Contadores Prometheus incrementam após um fluxo de chat completo.
3. O registro por execução do passo 6 contém todos os campos obrigatórios, para um caso de sucesso e para um caso com erro.
4. Teste marcado `requires_db`: duas requisições na mesma sessão acumulam tokens na tabela.

Verificação: `pytest tests/ -v -m "not requires_db"` → passa, com pelo menos 3 testes novos.

## Critérios de pronto

- [ ] `pytest tests/ -m "not requires_db"` sai com código 0
- [ ] `grep -rn "CHAT_TOKENS_IN" services/` mostra ao menos um ponto de incremento
- [ ] `grep -rn "KB_RETRIEVALS" services/ shared/` mostra ao menos um ponto de incremento
- [ ] Nenhuma métrica declarada em `observability.py` permanece sem uso — ou ela é incrementada, ou é removida com justificativa no relatório
- [ ] Rodar `eval/runner.py` produz JSONL válido com uma linha por caso
- [ ] `mypy shared/ services/` e `ruff check .` saem com código 0
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- Os trechos de "Estado atual" não corresponderem ao código vivo.
- O merge de estado do grafo perder os tokens acumulados e você não conseguir resolver sem mudar a semântica de `merge_graph_state` — essa função é usada em quatro lugares e mudá-la tem alcance maior que este plano.
- Persistir tokens exigir alteração de schema num banco já existente. Não há sistema de migração no projeto; reporte em vez de improvisar.
- Você concluir que precisa de streaming real para cumprir algum critério de pronto. Não precisa: tempo até o primeiro token está explicitamente fora de escopo.

## Notas de manutenção

- O arquivo JSONL do passo 6 é o insumo do experimento científico. Mudar seus campos depois que execuções medidas começarem **invalida a comparação** — congele o formato antes de medir e versione qualquer mudança.
- Um revisor deve conferir que nenhuma métrica nova ficou declarada e não usada, que é exatamente o vício que este plano corrige.
- Deliberadamente adiado: tempo até o primeiro token, que exige `stream=True` no gateway e interage com o guardrail de saída do plano 003. E a integração com Langfuse, que continua sendo dependência declarada e nunca importada.
