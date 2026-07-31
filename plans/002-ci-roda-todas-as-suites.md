# Plano 002: Fazer o CI executar todas as suítes e endurecer as asserções frágeis

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- .github/workflows/ci.yml tests/ pyproject.toml`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: S
- **Risco**: LOW para adicionar as suítes; espere vermelho imediato, que é o objetivo
- **Depende de**: `plans/001-build-system-e-ci-verde.md`
- **Categoria**: tests
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

O CI roda `pytest tests/unit/` e mais nada.
Quatro suítes existem e nunca são executadas em lugar nenhum: `tests/integration/`, `tests/e2e/`, `tests/smoke/` e `tests/dogfood/`, somando 348 linhas.
São justamente as que exercitam o fluxo real — endpoint `/chat`, framing SSE, roteamento do grafo, escalação, guardrails dentro do grafo.

Pior: quando essas suítes rodam, elas passam com o sistema totalmente quebrado, porque as asserções verificam a forma do evento e não o conteúdo.
Uma suíte que passa com tudo quebrado é pior que suíte nenhuma, porque produz confiança falsa.

Este plano faz o CI executar o que já foi escrito e endurece as asserções que não provam nada.

## Estado atual

`.github/workflows/ci.yml`, job `test`:

```yaml
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v --tb=short
```

`pyproject.toml:62-69`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "e2e: end-to-end tests",
]
```

Os markers estão declarados e **nenhum teste os usa** — `tests/e2e/test_chat_flow.py` só usa `@pytest.mark.asyncio`.
Como `testpaths = ["tests"]`, rodar `pytest` local executa tudo, enquanto o CI executa um quarto: local e CI divergem por construção.

`tests/conftest.py:119-138` define a fixture `e2e_client`, que substitui Postgres por `FakeSessionMaker` e o LLM por `mock_llm_completion`.
Ou seja: e2e, dogfood e smoke **não precisam de serviço externo** e podem rodar no runner do GitHub como estão.
Só `tests/integration/` toca infraestrutura de verdade.

Asserções frágeis identificadas, com o motivo de cada uma ser inútil:

- `tests/e2e/test_chat_flow.py:63` — `assert "done" in resp.text`.
  O handler de exceção em `services/agent_api/interface/app.py:313-316` emite um frame `error` **e** um frame `done`. Logo essa asserção passa mesmo se o grafo inteiro lançar exceção.
- `tests/e2e/test_chat_flow.py:85` — `assert "cannot" in content or "sorry" in content` para o teste de injection.
  O fallback genérico em `app.py:294` ("I'm sorry, I couldn't process your request") satisfaz a asserção. O teste passa quando o guardrail não fez nada e o grafo simplesmente não produziu saída.
- `tests/e2e/test_chat_flow.py:25` — `assert "token" in content` verifica o tipo do frame SSE, não o conteúdo.

Problema no dublê de LLM, `tests/support/mock_llm.py`:

- Linha 50 checa `"tool results" in system_msg` **antes** da linha 73 checar `"risk specialist"`.
  Como `INTENT_TOOLS["fraud_dispute"]` (`services/agent_api/application/tools.py:163`) sempre produz resultados de ferramenta, o cabeçalho `[Tool results …]` é sempre injetado, e o ramo do especialista de risco em `mock_llm.py:73-79` é **inalcançável**.
- Linhas 12-13 mapeiam "cartão"/"card" para o intent `card_invoice`, então `card_pay`, `limit_increase` e `block_card` **nunca são gerados** pelo dublê.
  Esses são exatamente os três intents quebrados no produto — o dublê foi construído em volta do bug.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Testes offline | `pytest tests/unit tests/smoke tests/dogfood tests/e2e -v` | executa até o fim |
| Só e2e | `pytest tests/e2e -v` | executa |
| Lint | `ruff check .` | exit 0 |

## Escopo

**Em escopo**:

- `.github/workflows/ci.yml`
- `pyproject.toml` (apenas a seção `[tool.pytest.ini_options]`)
- `tests/e2e/test_chat_flow.py`
- `tests/support/mock_llm.py`

**Fora de escopo**:

- Qualquer arquivo em `services/` ou `shared/`. Se um teste endurecido falhar por bug do produto, **esse é o resultado desejado**: registre a falha e deixe o bug para os planos 003 a 007.
- `tests/integration/` — precisa de Postgres real; fica atrás de marcador, não é corrigido aqui.
- `tests/support/fake_db.py` — o fake retorna sucesso para SQL não reconhecido, o que é débito real, mas endurecer isso derruba muita coisa de uma vez. Fica para depois.

## Fluxo git

- Branch: `advisor/002-ci-todas-as-suites`
- Conventional Commits em inglês, como o histórico. Exemplo: `test: run all offline suites in CI`
- Um commit por passo.

## Passos

### Passo 1: aplicar os markers declarados

Adicione `@pytest.mark.unit`, `@pytest.mark.integration` ou `@pytest.mark.e2e` às classes ou funções de teste conforme o diretório em que vivem.
Em `tests/integration/`, adicione também um marcador novo `requires_db` — declare-o em `pyproject.toml`:

```toml
markers = [
    "unit: unit tests",
    "integration: integration tests",
    "e2e: end-to-end tests",
    "requires_db: needs a live PostgreSQL",
]
```

**Verificar**: `pytest --collect-only -m requires_db -q` → coleta apenas testes de `tests/integration/`.

### Passo 2: fazer o CI rodar as suítes offline

Em `.github/workflows/ci.yml`, no job `test`, troque a linha de execução por:

```yaml
      - run: pytest tests/ -v --tb=short -m "not requires_db"
```

**Verificar** localmente: `pytest tests/ -v --tb=short -m "not requires_db"` → executa unit, smoke, dogfood e e2e; não coleta integration.
Espere falhas. Registre cada uma com nome e motivo.

### Passo 3: endurecer as asserções de e2e

Em `tests/e2e/test_chat_flow.py`:

1. Escreva uma função auxiliar no próprio arquivo que faça o parse do corpo SSE em uma lista de eventos `(tipo, dados)`, decodificando o JSON de cada linha `data: `.
2. Substitua `assert "done" in resp.text` (linha 63) por duas asserções: **nenhum** evento de tipo `error` está presente, e existe ao menos um evento `token` com conteúdo não vazio.
3. No teste de injection (linha 85), afirme sobre o comportamento correto e não sobre a substring da desculpa: o texto do usuário injetado **não** deve aparecer ecoado na resposta, e a conversa deve terminar sem evento `error`.
   Se você não conseguir distinguir bloqueio de falha genérica pelos eventos, essa é uma limitação real do produto: registre no relatório final e deixe o teste marcado com `pytest.mark.xfail(reason=...)` explicando, em vez de escrever asserção fraca.
4. Na linha 25, além de conferir que existe frame `token`, afirme sobre o conteúdo concatenado dos tokens.

**Verificar**: `pytest tests/e2e -v` → executa. As falhas que aparecerem agora são reais e devem ser registradas, não mascaradas.

### Passo 4: consertar a ordem de decisão do dublê de LLM

Em `tests/support/mock_llm.py`:

1. Mova a checagem de `"risk specialist"` (linha 73) para **antes** da checagem de `"tool results"` (linha 50), de forma que o ramo do especialista de risco seja alcançável.
2. Amplie o mapeamento de intent das linhas 12-13 para conseguir produzir `card_pay`, `limit_increase` e `block_card`, e não só `card_invoice`.
   Use expressões distintas para cada um — por exemplo "pagar fatura" para `card_pay`, "aumentar limite" para `limit_increase`, "bloquear cartão" para `block_card`.
3. Adicione um comentário curto no topo do arquivo dizendo que a ordem das checagens é significativa e por quê.

**Verificar**: `pytest tests/ -v -m "not requires_db"` → executa; o ramo de risco agora é exercitado.
Se o passo 4 fizer testes que antes passavam começarem a falhar, isso é esperado: eles passavam por acidente.

### Passo 5: manter a suíte de integração executável sob demanda

Não a coloque no CI ainda.
Adicione ao `README.md`, na seção de testes, uma linha documentando como rodá-la: `pytest tests/ -m requires_db`, com a nota de que exige Postgres em execução.

**Verificar**: `grep -n "requires_db" README.md` → retorna resultado.

## Plano de teste

- Não há teste novo de produto neste plano: o produto do plano são os próprios testes.
- Use `tests/unit/test_tools.py` como padrão estrutural para qualquer helper novo que você escrever.
- Ao terminar, o relatório final deve conter a lista completa de testes que falham, com uma linha por falha indicando se ela é bug de produto (deixar para outro plano) ou fragilidade de teste (corrigir aqui).

## Critérios de pronto

- [ ] `pytest tests/ -m "not requires_db"` executa unit, smoke, dogfood e e2e
- [ ] `pytest --collect-only -m requires_db -q` coleta apenas `tests/integration/`
- [ ] `.github/workflows/ci.yml` não contém mais a string `tests/unit/`
- [ ] `grep -n "risk specialist" tests/support/mock_llm.py` mostra a checagem antes da de `tool results`
- [ ] Nenhum arquivo em `services/` ou `shared/` foi modificado (`git status`)
- [ ] Relatório final lista cada teste que falha e classifica a causa
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- O plano 001 não foi concluído: sem ele `pip install -e ".[dev]"` falha e nada aqui roda.
- Alguma suíte que você esperava ser offline exigir Postgres ou Ollama de verdade. Nesse caso, reporte qual e por quê, em vez de adicionar serviço ao CI por conta própria.
- Endurecer uma asserção exigir mudar código de produto para passar.
- Mais de dez testes falharem depois do passo 4 — o volume indica que a suíte foi escrita contra um comportamento diferente do atual, e a decisão de o que é verdade é do dono do projeto.

## Notas de manutenção

- Quando os planos 003 a 007 corrigirem os bugs, vários testes marcados aqui devem passar a verde. Um `xfail` que começar a passar vira `XPASS` e deve ser promovido a teste normal.
- Um revisor deve conferir se alguma asserção nova é tautológica — o vício que este plano existe para eliminar.
- Deliberadamente adiado: fazer `tests/support/fake_db.py` levantar erro em SQL não reconhecido. É a próxima fragilidade da pilha e merece plano próprio.
