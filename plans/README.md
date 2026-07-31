# Planos de implementação

Gerados pela skill `improve` em 2026-07-31, contra o commit `34264cb`.
Execute na ordem abaixo, salvo indicação das dependências.
Cada executor: leia o plano inteiro antes de começar, respeite as condições de STOP, e atualize sua linha ao terminar.

## Como este projeto está dividido

Existem dois esforços concorrentes sobre este repositório, e eles competem por um motivo específico.

1. **Profissionalizar o projeto** — o que estes planos cobrem.
2. **Um experimento científico**, planejado em `.scratch/artigo-multiagente/`, que compara a arquitetura multi-agente atual contra um agente único com tool calling, medindo sucesso de tarefa, latência e tokens.

O conflito: **corrigir código no meio das execuções medidas invalida a série do experimento.**

A ordem adotada resolve isso em três fases:

- **Fase 0 — base comum** (planos 001 a 005). Conserta o que bloqueia os dois esforços: verificação funcionando, falhas visíveis, instrumentação de tokens e latência. O experimento precisa disso tanto quanto o projeto.
- **Congelamento.** Ao fim da fase 0, o commit é registrado e o experimento roda sobre ele. O artigo cita esse commit exato.
- **Fase 2 — profissionalização** (planos 006 a 008 e as fichas). Só depois das execuções medidas.

**Atenção especial ao plano 007**: ele altera `INTENT_TOOLS`, que é o braço de controle do experimento. Coordene antes de mesclar.

## Ordem de execução e status

| Plano | Título | Fase | Prioridade | Esforço | Depende de | Status |
|---|---|---|---|---|---|---|
| 001 | Tornar o pacote instalável e o CI verde | 0 | P1 | S | — | TODO |
| 002 | CI executa todas as suítes; asserções endurecidas | 0 | P1 | S | 001 | TODO |
| 003 | Guardrail de saída realmente bloqueia | 0 | P1 | M | 002 | TODO |
| 004 | Falhas de infraestrutura param de virar resposta válida | 0 | P1 | M | 002 | TODO |
| 005 | Instrumentação de tokens, latência e ferramentas | 0 | P1 | M | 004 | TODO |
| 006 | RAG funcional, com prova de recuperação | 2 | P1 | M | 004 | TODO |
| 007 | Intents de cartão executam a ação que prometem | 2 | P1 | M | 004 | TODO |
| 008 | Documentação alinhada ao código | 2 | P1 | S | executar por último | TODO |

Valores de status: TODO | EM ANDAMENTO | PRONTO | BLOQUEADO (com o motivo em uma linha) | REJEITADO (com a justificativa em uma linha).

## Notas de dependência

- **001 destrava tudo.** `pip install -e ".[dev]"` falha neste repositório e sempre falhou, então nenhum teste e nenhuma verificação de tipo jamais rodou aqui. Sem ele, nenhum outro plano pode ser verificado.
- **002 antes de 003 a 007.** Esses quatro planos exigem teste de regressão que prove a correção, e as suítes que exercitam o fluxo real não rodam em lugar nenhum hoje.
- **004 antes de 005 e 006.** Instrumentar e corrigir o RAG sobre uma base que engole exceção produz número que mente.
- **008 por último.** Ele descreve o estado final; rodar antes obriga a revisitar.

## Fichas — findings reais sem plano completo

Cada uma tem evidência verificada. Viram plano quando alguém decidir executá-las.

### F1 — Memória de conversa não existe

`services/agent_api/interface/app.py:234` monta o estado com uma única mensagem por requisição, e `agent.py:289` compila o grafo sem checkpointer.
O `for msg in state["messages"][-5:]` de `agent.py:149` sempre itera exatamente um elemento.
As tabelas `checkpoints` e `customer_facts` existem em `ops/init.sql` e nunca são escritas; o front-end guarda histórico e nunca o envia.
Consequência: o bot esquece a pergunta anterior a cada turno, e o resumo entregue ao atendente humano na escalação contém uma linha.
Esforço M, e é pré-requisito da confirmação em dois turnos exigida pelo plano 007.
Interage com o experimento: sem memória, só é possível medir tarefas de turno único.

### F2 — Identidade do cliente vem do corpo da requisição

`app.py:143` — `SessionRequest.customer_id` é escolhido por quem chama; a única validação é que o UUID existe.
Toda a autorização por cliente de `tools.py` está correta, mas defende a fronteira errada.
Somado a isso: `/mock/*` é montado no app público (`app.py:82`) com auth resolvida em tempo de importação (`mock_banking_api.py:20`), e as rotas de escrita mutam estado sabendo apenas o UUID do cartão.
Com banco fictício o dano hoje é zero. É bloqueante absoluto antes de qualquer dado real. Esforço L.

### F3 — Guardrails cobrem o idioma errado e têm padrões mortos

`guardrails.py:14-16` define `EMAIL_PATTERN`, `PHONE_PATTERN` e `ACCOUNT_MASK_PATTERN`, nenhum referenciado em lugar nenhum.
As 8 expressões de detecção de injeção são todas em inglês, num produto cujo idioma padrão é português.
A checagem de saída só bloqueia CPF diferente do cliente — que o modelo nem recebe no contexto.
Além disso, `agent.py:146` injeta `customer_id` no prompt e `tools.py:46` coloca UUID interno de cartão no texto que o modelo vê.
Esforço S para a paridade de idioma e para usar os padrões já definidos.

### F4 — Diretório `prompts/` é código morto que diverge do que roda

Sete arquivos, 235 linhas, não lidos por nenhum código; os prompts reais estão em `agent.py:45-79`.
Já há divergência mensurável: `prompts/router.md:24` manda extrair entidades, e nenhuma entidade é extraída.
O `docker-compose.yml:60` monta o diretório e o Dockerfile o copia para a imagem.
Decisão binária: carregar de verdade, com registro e falha alta se faltar arquivo, ou deletar junto com as referências no compose, no Dockerfile e no README. Esforço S.

### F5 — Dependências declaradas e nunca importadas

`celery`, `alembic`, `langfuse`, `sse-starlette`, `langchain-ollama` e `langchain-community`: zero importações.
`celery[redis]` arrasta kombu, billiard, vine e amqp para as duas imagens.
`sentence-transformers` traz torch e o stack CUDA para a imagem do `agent_api`, que nunca usa tensor — e, se o ETL for importado no processo errado, o modelo de embedding disputa VRAM com o modelo de linguagem local.
Tetos de major que merecem decisão consciente: `langgraph<1` e `langchain-core<1` estão acoplados; `chromadb<1` com imagem de servidor uma minor atrás; `langfuse` preso na v2 com SDK v4 lançado. Esforço S para remover, M para as migrações.

### F6 — Cinco fontes divergentes de dependências e três scripts de arranque

`start.py`, `start.sh` e `start.bat` repetem a mesma lista escrita à mão, que omite `chromadb` e `sentence-transformers`, e ignoram o `uv.lock` de 888 KB.
`shell.nix` e `flake.nix` divergem entre si.
Os três scripts fazem coisas diferentes — o `.bat` não inicializa banco nem sobe worker — enquanto o README descreve os três como equivalentes.
`start.py:68-79` verifica dependências no interpretador errado, então o ambiente virtual pode ficar vazio.
Há caminho absoluto de máquina específica em `start.sh:63` e em `tests/conftest.py:26-28`, e um nome de usuário fixo em `nixos-setup.nix:20`.
Esforço S para unificar em `uv sync`, M para consolidar os scripts.

### F7 — Schema sem migração, e hexagonal decorativo

`alembic` está declarado e não há uma única migração; `Base.metadata.create_all` (`app.py:52`) é operação nula porque nenhum modelo está mapeado.
O schema tem três fontes divergentes: `ops/init.sql`, os modelos Pydantic de `shared/domain/models.py` e as strings SQL espalhadas.
`ops/init.sql:127` usa o meta-comando `\i` do psql para carregar seeds, e o `docker-compose.yml:12` não monta o arquivo referenciado — o caminho falha.
Em paralelo: quatro diretórios de camada estão vazios, não há um único `Protocol` no repositório, e `application` importa infraestrutura concreta.
Os 176 linhas de modelo de domínio são importadas apenas por testes. Esforço M cada.

## Findings considerados e rejeitados

Registrados para que ninguém os re-audite.

- **Rate limiter em memória de processo** (`shared/infrastructure/rate_limit.py:8`): não escala horizontalmente e vaza memória, mas é consistente com o escopo single-node declarado, e o Redis já está disponível se um dia for preciso. Nota: a chave é o `session_id`, escolhido pelo cliente, então o limite é contornável — se for endereçado algum dia, é por essa razão, não pela arquitetura.
- **`Decimal` no domínio contra `float` nos DTOs do backend simulado**: risco real de precisão em valores monetários, mas o dado é sintético e não alimenta cálculo nenhum. Volta a importar se F7 for endereçado.
- **Varreduras lineares em `mock_banking_api.py`**: O(n) sobre dezenas de linhas de semente em memória. Indexar não muda nada mensurável neste tamanho.
- **Cliente HTTP recriado por chamada em `tools.py:118,132`**: seria finding de performance, mas `lookup_cep` e `get_currency_quote` não são alcançáveis por nenhum intent. A decisão real é ligá-las ou removê-las, não otimizá-las.
- **Sub-pins de patch das dependências**: o `uv.lock` está resolvido em versões recentes dentro das faixas. O problema é teto de major em quatro pacotes (ver F5), não higiene de minor.

## O que não foi auditado

- Execução real de qualquer teste, lint ou verificação de tipo: as dependências não estavam instaladas na máquina onde a auditoria rodou, e instalar não é permitido a esta skill. Todas as conclusões vêm de leitura de código, do `uv.lock` e dos logs do CI.
- Auditoria de CVE das dependências. Não há `pip-audit` nem Dependabot configurados no projeto, e nenhum audit foi executado. A postura de segurança das dependências está **não avaliada**, não "limpa".
- `frontend/app.py` além do que apareceu por acoplamento com a API.
- O conteúdo de `ops/grafana/` e `ops/prometheus/` além da constatação de que o dashboard provisionado tem `"panels": []`.
