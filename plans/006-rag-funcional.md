# Plano 006: Fazer o RAG funcionar, e provar que funciona

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- shared/infrastructure/chroma_client.py services/ingestion_worker/`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: LOW — a funcionalidade está morta hoje; não há comportamento a preservar
- **Depende de**: `plans/004-falhas-visiveis.md`
- **Categoria**: bug
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

O RAG é metade do que o projeto anuncia, e está morto por **três causas independentes**, nenhuma das quais gera erro visível.
Toda pergunta do intent `faq` é respondida sem nenhum contexto recuperado, enquanto o prompt do especialista afirma que existe contexto abaixo — ou seja, o sistema alucina por construção nesse caminho.

As três causas, todas verificadas no código:

1. O espaço de embeddings da ingestão não coincide com o da consulta.
2. Nada enfileira trabalho de ingestão, então o índice está vazio de qualquer forma.
3. Os scripts de arranque não instalam as bibliotecas necessárias, então o código nem chega a tentar.

## Estado atual

### Causa 1 — incompatibilidade de dimensão

`services/ingestion_worker/application/etl_pipeline.py:43` grava com um modelo de 1024 dimensões:

```python
        _model = SentenceTransformer("BAAI/bge-m3")
```

e passa esses vetores explicitamente no upsert (`etl_pipeline.py:182-187`).

`shared/infrastructure/chroma_client.py:26-31` cria a coleção **sem** função de embedding:

```python
def get_or_create_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=KB_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
```

e consulta com `query_texts=` (`chroma_client.py:42`), o que faz o Chroma embutir a pergunta com sua função padrão, de 384 dimensões.
384 contra 1024 — a consulta não pode funcionar.
A exceção resultante cai no `except Exception: return []` de `chroma_client.py:44-45`.

### Causa 2 — nenhum produtor de trabalho de ingestão

`run_ingestion()` (`etl_pipeline.py:195`) só é alcançável por `process_ingestion_job` (`services/ingestion_worker/interface/worker.py:26-31`), que só dispara ao receber um trabalho na lista Redis `neobank:queue`.

Busca por `neobank:queue` em todo o repositório retorna **apenas duas linhas, ambas dentro do próprio worker**: `worker.py:75` que consome e `worker.py:101` que reenfileira em caso de retentativa.
Nenhum código publica trabalho.
`run_ingestion` também não tem bloco `if __name__ == "__main__"` nem entry point declarado.

Consequência: `collection.count()` é zero, e `chroma_client.py:40` retorna cedo com lista vazia antes mesmo de chegar na causa 1.

### Causa 3 — bibliotecas ausentes no caminho recomendado

`chroma_client.py:5-9` e `etl_pipeline.py:15-25` têm `try/except ImportError` com flags `CHROMA_AVAILABLE` e `ST_AVAILABLE`.
Os três scripts de arranque (`start.py`, `start.sh`, `start.bat`) instalam uma lista de pacotes escrita à mão que **omite `chromadb` e `sentence-transformers`**.
Quem segue o caminho "one-click start" do README obtém um sistema onde o RAG é fisicamente impossível, e falha em silêncio.

A causa 3 é corrigida no plano de scripts de arranque; **aqui você só precisa garantir que ela não te confunda durante os testes**. Instale com `pip install -e ".[dev]"`.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Subir Chroma | `docker compose up -d chroma` | container saudável |
| Testes offline | `pytest tests/ -v -m "not requires_db"` | passa |
| Lint / tipos | `ruff check .` e `mypy shared/ services/` | exit 0 |

## Escopo

**Em escopo**:

- `shared/infrastructure/chroma_client.py`
- `services/ingestion_worker/application/etl_pipeline.py`
- `services/ingestion_worker/interface/worker.py` — apenas para adicionar produtor ou entry point
- `pyproject.toml` — apenas para declarar entry point de console, se essa for a escolha
- `README.md` — a seção de setup, documentando como popular a base
- Testes novos

**Fora de escopo**:

- Trocar o modelo de embedding por outro. `sentence-transformers` arrasta torch e o stack CUDA para dentro das imagens, e há argumento real para usar uma alternativa mais leve — mas isso é decisão de arquitetura com plano próprio. Aqui, faça os dois lados **concordarem**, seja qual for o modelo.
- Métricas de qualidade de recuperação além do teste do passo 5.
- O caminho assíncrono do worker. Se você escolher entry point de linha de comando, o worker continua sem produtor — registre isso, não conserte aqui.

## Fluxo git

- Branch: `advisor/006-rag-funcional`
- Conventional Commits em inglês. Exemplo: `fix(kb): align query and ingestion embedding spaces`

## Passos

### Passo 1: centralizar a função de embedding

Crie uma única função em `shared/infrastructure/` que devolva a função de embedding a ser usada pelos **dois** lados — ingestão e consulta.

Ela precisa ser importável tanto pelo worker quanto pela API, e deve deixar explícito qual modelo usa.

**Verificar**: `grep -rn "BAAI/bge-m3" services/ shared/` → o nome do modelo aparece em **um** lugar só.

### Passo 2: registrar a função de embedding na coleção

Em `chroma_client.py`, passe a função de embedding em `get_or_create_collection`.
Alternativamente, calcule o vetor da pergunta com o mesmo modelo e chame `collection.query(query_embeddings=...)` em vez de `query_texts=`.

Escolha uma das duas abordagens e use-a de forma consistente.
Documente a escolha em um comentário de uma linha.

**Atenção**: uma coleção já existente com a dimensão antiga precisa ser recriada. Como nada popula o índice hoje, não há dado a perder — mas registre isso no relatório final para quem tiver um volume antigo.

**Verificar**: com Chroma no ar e o índice populado pelo passo 3, uma consulta retorna documentos em vez de lista vazia.

### Passo 3: criar um caminho executável de ingestão

Adicione um ponto de entrada de linha de comando que rode a ingestão diretamente, sem depender da fila:

- ou um bloco `if __name__ == "__main__":` em `etl_pipeline.py`, invocável por `python -m services.ingestion_worker.application.etl_pipeline`
- ou um `[project.scripts]` no `pyproject.toml`

Ele deve aceitar o diretório de dados como argumento, com valor padrão apontando para `data/kb/`, e imprimir quantos pedaços foram indexados.

**Verificar**: rodar o comando com o Chroma no ar imprime uma contagem maior que zero, e uma segunda execução é idempotente (o código já usa `upsert`).

### Passo 4: remover o silenciador de erro

Se o plano 004 já substituiu o `except Exception: return []` de `chroma_client.py:44-45` por log e métrica, apenas confirme.
Se não, faça agora: falha de consulta precisa ser distinguível de "nada encontrado".

Este é o passo que impede o RAG de morrer de novo em silêncio no futuro.

**Verificar**: `grep -n "except Exception" shared/infrastructure/chroma_client.py` → não há mais `except` que devolva lista vazia sem registrar nada.

### Passo 5: provar a recuperação com um teste

Escreva um teste que:

1. Indexe um documento conhecido e curto.
2. Consulte com uma pergunta cujo texto **não** seja idêntico ao documento, mas semanticamente próxima.
3. Afirme que o documento conhecido está entre os retornados.

Esse teste precisa exigir Chroma real: marque-o `requires_db` ou crie um marcador análogo, e documente como rodá-lo.
Um teste de recuperação contra um dublê não prova nada sobre compatibilidade de dimensão, que é justamente o defeito em questão.

**Verificar**: o teste falha com o código anterior ao passo 2 e passa depois.

### Passo 6: documentar como popular a base

No `README.md`, na sequência de setup, adicione o comando de ingestão **antes** do passo que manda abrir a interface.

Hoje o README não menciona ingestão em nenhuma linha, o que significa que ninguém que siga a documentação jamais terá uma base de conhecimento populada.

**Verificar**: `grep -in "ingest" README.md` → retorna resultado.

## Plano de teste

- Teste de recuperação do passo 5, exigindo Chroma real. É o teste que dá nome ao plano.
- Teste unitário: a função de embedding centralizada devolve vetores da dimensão esperada.
- Teste unitário: falha de consulta ao Chroma é distinguível de resultado vazio (pode já existir, vindo do plano 004).
- Padrão estrutural: `tests/integration/test_mock_api.py` para os que exigem serviço, `tests/unit/test_tools.py` para os unitários.

## Critérios de pronto

- [ ] `grep -rn "BAAI/bge-m3" services/ shared/` retorna exatamente uma ocorrência
- [ ] `grep -n "query_texts" shared/infrastructure/chroma_client.py` — ou não retorna nada, ou a coleção tem função de embedding registrada
- [ ] Existe comando documentado que popula a base e imprime a contagem
- [ ] O teste de recuperação passa com Chroma no ar, e falhava antes da correção (comprove no relatório final)
- [ ] `grep -in "ingest" README.md` retorna resultado
- [ ] `ruff check .` e `mypy shared/ services/` saem com código 0
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- Os trechos de "Estado atual" não corresponderem ao código vivo.
- O Chroma não subir localmente e você não conseguir executar o teste do passo 5. Sem esse teste, o plano **não pode ser dado como pronto** — a correção é justamente sobre compatibilidade em tempo de execução, que teste offline não verifica.
- A versão do cliente `chromadb` for incompatível com a imagem do servidor no `docker-compose.yml`. Existe divergência conhecida entre as duas: se ela impedir o trabalho, reporte em vez de atualizar versões por conta própria.
- Registrar a função de embedding exigir baixar um modelo de vários gigabytes num ambiente sem espaço ou sem rede.

## Notas de manutenção

- **A regra que este plano institui**: quem indexa e quem consulta usam a mesma função de embedding, vinda do mesmo lugar. Qualquer mudança de modelo exige reindexação completa, e a dimensão precisa bater — o Chroma não avisa de forma amigável.
- Um revisor deve confirmar que não sobrou nenhum `except` engolindo erro de consulta, e que o nome do modelo não voltou a ser duplicado.
- Deliberadamente adiado: o peso de `sentence-transformers` (que traz torch e o stack CUDA para as duas imagens Docker, incluindo a que nunca usa), e o fato de o worker de ingestão continuar sem produtor no caminho assíncrono.
