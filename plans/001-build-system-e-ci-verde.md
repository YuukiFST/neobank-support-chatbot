# Plano 001: Tornar o pacote instalável e o CI verde

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- pyproject.toml .github/workflows/ci.yml`
> Se algum arquivo em escopo mudou desde a escrita deste plano, compare os trechos de "Estado atual" com o código vivo antes de prosseguir.
> Divergência é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: S
- **Risco**: MED (o `ruff format` produz diff grande; ver passo 4)
- **Depende de**: nenhum
- **Categoria**: dx
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

`pip install -e ".[dev]"` falha neste repositório, e sempre falhou.
Como consequência, os jobs `test` e `type-check` do CI morrem na instalação, e nenhum teste ou verificação de tipo jamais executou aqui.
As cinco execuções mais recentes do CI são todas FAIL.

Isso é a causa-raiz de quase todo o resto do débito do projeto: sem portão de verificação funcionando, 111 erros de lint e vários bugs graves entraram sem resistência.
Nenhum outro plano deste diretório pode ser verificado com confiança antes deste.

## Estado atual

Arquivos relevantes:

- `pyproject.toml` — 74 linhas, configura ruff, mypy, pytest e coverage. **Não tem tabela `[build-system]` e não tem `[tool.setuptools]`.**
- `.github/workflows/ci.yml` — 4 jobs: `lint`, `test`, `type-check`, `docker-build`.

O erro exato do CI (run 30637025619, job `type-check`):

```
error: Multiple top-level packages discovered in a flat-layout:
       ['ops', 'eval', 'data', 'shared', 'prompts', 'frontend', 'services'].
ERROR: Failed to build ... when getting requirements to build editable
```

Causa: sem `[build-system]` e sem declaração de pacotes, o setuptools tenta autodescobrir e encontra sete diretórios de topo, dos quais só `shared` e `services` são pacotes Python de verdade.
`eval`, `frontend`, `ops`, `data` e `prompts` são diretórios de dados e scripts.

O job `lint` reporta `Found 111 errors`, distribuídos assim: `E501`×49, `I001`×20, `F401`×19, `UP042`×9, `UP045`×7, `B904`×3, mais `UP036`, `SIM105`, `E402`, `B905`.

Configuração de lint em `pyproject.toml:50-55`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH"]
```

Configuração de mypy em `pyproject.toml:57-60`:

```toml
[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]
```

Os Dockerfiles não sofrem do problema porque usam `uv pip install --system .`, que tolera o layout — por isso só o job `docker-build` passa.

## Comandos que você vai precisar

| Propósito | Comando | Esperado no sucesso |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Lint | `ruff check .` | exit 0, `All checks passed!` |
| Formatação | `ruff format --check .` | exit 0 |
| Testes | `pytest tests/unit/ -v` | exit 0, todos passam |
| Tipos | `mypy shared/ services/` | ver passo 5 |

## Escopo

**Em escopo** (os únicos arquivos que você deve modificar):

- `pyproject.toml`
- Qualquer arquivo `.py` que o `ruff` apontar, **apenas** para correções de lint
- `.github/workflows/ci.yml` (somente se o passo 5 exigir)

**Fora de escopo** (não toque, mesmo parecendo relacionado):

- Qualquer mudança de comportamento. Este plano não corrige bug nenhum — só torna o projeto verificável.
  Se o lint apontar algo que parece um bug de verdade, **anote no relatório final e deixe o comportamento como está**.
- `.scratch/` — planejamento de um artigo acadêmico, não é código.
- `tests/` além de correções de lint. A mudança de quais suítes rodam é o plano 002.

## Fluxo git

- Branch: `advisor/001-build-system`
- Conventional Commits, em inglês, como o histórico existente. Exemplo real do repo: `chore: ignore local planning files from version control`
- Um commit por passo. **O passo 4 tem que ser um commit isolado**, porque produz um diff grande de formatação.
- Não faça push nem abra PR a menos que o operador peça.

## Passos

### Passo 1: declarar o sistema de build e os pacotes

Adicione ao topo do `pyproject.toml`, antes de `[project]`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

E adicione, após a tabela `[project.optional-dependencies]`:

```toml
[tool.setuptools]
packages = ["shared", "services"]
```

Note que `shared` e `services` têm subpacotes.
Se o `pip install` reclamar de subpacotes ausentes, troque por descoberta explícita:

```toml
[tool.setuptools.packages.find]
include = ["shared*", "services*"]
```

**Verificar**: `pip install -e ".[dev]"` → exit 0, termina com `Successfully installed`.

### Passo 2: confirmar que os testes finalmente rodam

Não corrija teste que falhe neste passo — só registre.

**Verificar**: `pytest tests/unit/ -v` → executa e reporta resultado.
Anote quantos passam e quantos falham no relatório final.
Se **todos** os testes unitários falharem por erro de importação, isso é condição de STOP.

### Passo 3: correções automáticas de lint

```
ruff check --fix .
```

Isso resolve `I001` (ordenação de import), `F401` (import não usado), `UP042`, `UP045`, `UP036` e `SIM105`.

Atenção ao `F401`: em `services/ingestion_worker/interface/worker.py:15` os nomes `engine` e `Base` são importados e não usados.
Confirme que remover não quebra um efeito colateral de importação antes de aceitar — se `engine` for importado só para inicializar a conexão, remover muda comportamento, e aí você deve adicionar `# noqa: F401` com um comentário explicando, em vez de apagar.

**Verificar**: `ruff check .` → o número de erros caiu; anote o que restou.

### Passo 4: correções manuais restantes, em commit isolado

O que sobra depois do `--fix`:

- **`E501`** (49 ocorrências, linha acima de 100 colunas). Rode `ruff format .` primeiro — ele resolve a maioria.
  As que sobrarem são strings longas, que o formatador não quebra. Quebre-as manualmente com concatenação implícita entre parênteses.
- **`B904`** (3 ocorrências): `raise` dentro de `except` sem `from`. Corrija para `raise X(...) from exc`, ou `from None` quando a causa original for deliberadamente omitida.
- **`E402`**: em `tests/conftest.py:26-30` há statements executáveis antes de um import de nível de módulo.
  Esse bloco também contém um caminho absoluto de máquina específica (um hash do `/nix/store`).
  **Não resolva movendo o import** — isso pode quebrar a configuração de ambiente que o bloco faz.
  Adicione `# noqa: E402` nos imports afetados e registre o caminho hardcoded no relatório final como débito conhecido.
- **`B905`**: `zip()` sem `strict=`. Adicione `strict=True` se os iteráveis devem ter o mesmo tamanho, `strict=False` se não.

Faça este passo em **um commit separado**, com mensagem `style: apply ruff formatting and fix lint violations`.

**Verificar**: `ruff check .` → `All checks passed!` e `ruff format --check .` → exit 0.

### Passo 5: decidir o que fazer com o mypy strict

Rode `mypy shared/ services/` pela primeira vez na história do projeto.

O `strict = true` está ligado e o código não é anotado o suficiente para passar.
Assinaturas sem anotação de retorno em caminhos centrais incluem:

- `shared/infrastructure/chroma_client.py:17` — `def _get_client():`
- `shared/infrastructure/chroma_client.py:26` — `def get_or_create_collection():`
- `services/agent_api/application/agent.py:121` — `def _make_specialist_node(specialist_name: str):`
- `services/agent_api/application/agent.py:254` — `def create_agent_graph():`
- `services/ingestion_worker/application/etl_pipeline.py:38` — `def _get_model():`

Regra de decisão, aplicada estritamente:

- **Se o mypy reportar 20 erros ou menos**: corrija adicionando as anotações faltantes. Não use `# type: ignore` para calar erro.
- **Se reportar mais de 20 erros**: NÃO tente corrigir tudo. Em vez disso, adicione ao `pyproject.toml` overrides por módulo para as bibliotecas sem stubs decentes:

```toml
[[tool.mypy.overrides]]
module = ["litellm.*", "langgraph.*", "chromadb.*", "sentence_transformers.*"]
ignore_missing_imports = true
```

Rode novamente. Se ainda passar de 20 erros depois disso, **pare e reporte o total e as cinco categorias mais frequentes** — a decisão entre baixar o rigor do mypy e anotar o código inteiro é do dono do projeto, não sua.

**Verificar**: `mypy shared/ services/` → exit 0, ou relatório de STOP com a contagem.

### Passo 6: garantir que o CI reflete o que passou localmente

Não mude o conjunto de suítes que roda — isso é o plano 002.
Apenas confirme que os quatro jobs de `.github/workflows/ci.yml` correspondem aos comandos que você acabou de rodar com sucesso.

Se o passo 5 terminou em STOP, o job `type-check` continuará vermelho.
Nesse caso, e **somente** nesse caso, registre no relatório final; não desabilite o job.

**Verificar**: `git diff .github/workflows/ci.yml` → vazio, ou com a única alteração que o passo 5 exigiu.

## Plano de teste

Este plano não adiciona teste novo — ele torna os testes existentes executáveis pela primeira vez.

- Registre no relatório final o resultado de `pytest tests/unit/ -v`: quantos passam, quantos falham, e o nome de cada falha.
- Teste que falhe por bug real do produto **não deve ser corrigido aqui**. Anote e deixe para os planos 003 a 007.
- Se um teste falhar por causa de uma correção sua de lint, isso é regressão sua e deve ser corrigida antes de terminar.

## Critérios de pronto

Todos devem valer:

- [ ] `pip install -e ".[dev]"` sai com código 0
- [ ] `ruff check .` sai com código 0
- [ ] `ruff format --check .` sai com código 0
- [ ] `pytest tests/unit/ -v` executa até o fim (não precisa passar tudo; precisa executar)
- [ ] `mypy shared/ services/` sai com código 0, ou existe relatório de STOP com contagem e categorias
- [ ] `grep -n "build-system" pyproject.toml` retorna resultado
- [ ] Nenhum arquivo fora do escopo foi modificado (`git status`)
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

Pare e reporte, sem improvisar, se:

- O `pyproject.toml` já contiver `[build-system]` quando você começar — o repositório derivou, e o resto do plano pode não se aplicar.
- `pip install -e ".[dev]"` continuar falhando depois do passo 1 com erro **diferente** do de descoberta de pacotes.
- Todos os testes unitários falharem por erro de importação após a instalação ter sucesso.
- O mypy reportar mais de 20 erros mesmo após os overrides do passo 5.
- Uma correção de lint exigir mudar comportamento para o lint passar. Nesse caso o lint está apontando um bug, e bug é escopo de outro plano.

## Notas de manutenção

- O `[tool.setuptools] packages` precisa ser revisado se um novo pacote Python de topo for criado. `eval/` e `frontend/` continuam propositalmente fora do pacote instalável — são scripts, não biblioteca.
- Um revisor deve olhar com atenção o commit de formatação do passo 4 separadamente dos demais: ele é grande por natureza e não deve conter nenhuma mudança semântica.
- Ficou deliberadamente de fora deste plano: o caminho absoluto do `/nix/store` em `tests/conftest.py:26-28`, que quebra após um `nix-collect-garbage`. Registrado como débito, tratado no plano de scripts de arranque.
