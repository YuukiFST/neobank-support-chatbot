# Plano 008: Alinhar a documentação ao que o código realmente faz

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- README.md docs/`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: S
- **Risco**: LOW — não toca código de produção
- **Depende de**: idealmente executar por último, depois de 003 a 007, para descrever o estado final
- **Categoria**: docs
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

Este é um projeto de portfólio: o produto dele é a credibilidade técnica de quem o escreveu.
O `README.md` contém pelo menos onze afirmações verificavelmente falsas, e a seção cujo título declara honestidade sobre limitações é justamente a que contém a alegação mais forte e não sustentada.

O custo é assimétrico. Um avaliador que confira duas afirmações e ache duas falsas passa a descontar o resto — inclusive tudo que é verdadeiro e bem feito, que não é pouco.
Corrigir texto é o item mais barato da lista inteira e o de maior retorno para o objetivo declarado do projeto.

## Estado atual

Afirmações do `README.md` confrontadas com o código:

| Linha | Afirma | Realidade verificada |
|---|---|---|
| 39 | Postgres guarda o checkpointer do LangGraph | `agent.py:289` compila sem checkpointer; a tabela `checkpoints` de `ops/init.sql:107-114` nunca é escrita |
| 174-179 | Intents 4, 5 e 6 acionam a API de cartões | `tools.py:160-162` executa só `get_cards`; nenhuma ação ocorre |
| 176 | Aumento de limite escala acima do teto | `agent.py:229` roteia para o especialista de cartão; nunca escala |
| 184 | Autorização por cliente em toda ferramenta | verdadeiro em `tools.py`, falso nas rotas `/mock`, e a sessão é fabricável pelo chamador |
| 185 | Guardrail detecta injeção e vazamento de PII | são 8 expressões regulares, todas em inglês, num produto cujo idioma padrão é português |
| 191 | Langfuse faz tracing de LLM | nenhuma linha do repositório importa `langfuse` |
| 194 | FinOps com custo por sessão | as colunas de token e custo ficam permanentemente em zero |
| 89 | `pip install -e ".[dev]"` | falha; o pacote não é instalável |
| 95 | `psql -f ops/init.sql` é "rodar migrações" | é `CREATE TABLE IF NOT EXISTS`, não migração; e falha no meta-comando `\i` |
| 63-70 | Os três scripts de arranque fazem as mesmas sete coisas | `start.bat` faz três; `start.py` faz seis |
| 215 | `prompts/` contém prompts versionados do sistema | o diretório não é lido por nenhum código; os prompts reais estão embutidos em `agent.py:45-79` |
| 216 | `docs/` contém arquitetura e ADRs | `docs/` tem um arquivo; não há ADR nenhum |
| 225 | Kubernetes validado em `kind`, com evidência em `docs/` | não existe evidência alguma em `docs/` |

Em `docs/ai-assisted-development.md`:

- Linha 18 afirma avaliação com LLM-as-judge. `eval/runner.py:47-54` faz comparação de string; `prompts/judge.md` não é carregado por nada; `eval/runner.py:13` importa `llm_completion` e nunca usa.
- Linha 27 afirma que o CI tem um passo opcional de revisão de código por IA. O `ci.yml` tem quatro jobs, nenhum de revisão.
- Linha 28 cita o mapa wayfinder e o PRD como evidência. O `.gitignore:65-68` exclui `PRD.md`, `CONTEXT.md`, `jobs/` e `wayfinder/` do controle de versão — a evidência citada foi deliberadamente removida.

Um item precisa de verificação antes de decidir: `README.md:162` instrui `ollama pull qwen3.5:9b`, e o mesmo identificador aparece em `shared/infrastructure/config.py:10`.
A família de tags do Ollama historicamente usa `qwen2.5` e `qwen3`. **Confirme no registro do Ollama antes de alterar**, e não mude o valor por suposição.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Conferir afirmação | `grep -rn "<termo>" services/ shared/` | evidência ou ausência dela |
| Lint de docs | nenhum configurado | — |

## Escopo

**Em escopo**:

- `README.md`
- `docs/ai-assisted-development.md`
- Novos arquivos em `docs/` (por exemplo ADRs), se você optar por criá-los
- `CLAUDE.md` na raiz (criar) — ver passo 4

**Fora de escopo**:

- Implementar o que a documentação promete. A regra deste plano é **descrever o que existe**, nunca construir para justificar o texto.
- Código de produção, sob qualquer pretexto.
- Reescrever o README inteiro. Corrija o que é falso e reorganize o mínimo; um redesign completo dificulta a revisão e não é o objetivo.

## Fluxo git

- Branch: `advisor/008-documentacao-honesta`
- Conventional Commits em inglês. Exemplo: `docs: describe implemented behaviour and move claims to roadmap`

## Passos

### Passo 1: verificar cada afirmação antes de reescrevê-la

Para cada linha da tabela de "Estado atual", confirme você mesmo no código antes de alterar o texto.
Se algum dos planos 003 a 007 já tiver sido executado, a realidade pode ter mudado — e aí a afirmação do README pode ter virado verdade.

Produza uma lista de três colunas no relatório final: afirmação, estado verificado hoje, ação tomada.

**Verificar**: a lista existe e cobre as treze linhas da tabela mais os três itens de `docs/ai-assisted-development.md`.

### Passo 2: separar o que existe do que é intenção

Reescreva as afirmações falsas de forma que descrevam o comportamento real.
Mova o que é intenção para uma seção explícita chamada "Roadmap" ou "Não implementado", em vez de apagar — o plano do projeto tem valor, desde que não seja apresentado como estado atual.

Regra de redação: se você não conseguir apontar o `arquivo:linha` que sustenta uma frase, ela não fica na descrição do estado atual.

**Verificar**: `grep -in "langfuse" README.md` → ou a menção sumiu, ou está sob a seção de não implementado.

### Passo 3: corrigir o documento sobre uso de IA

Em `docs/ai-assisted-development.md`, mantenha apenas o que é verificável neste repositório.
Marque explicitamente o LLM-as-judge e a revisão de código no CI como **não implementados**.

Sobre a citação ao mapa e ao PRD: existe hoje, versionado, o diretório `.scratch/artigo-multiagente/`, com mapa, tickets e pesquisas.
Se a intenção for citar evidência de design assistido, cite o que está no repositório, e não arquivos excluídos pelo `.gitignore`.

**Verificar**: `grep -in "judge\|code-review" docs/ai-assisted-development.md` → as menções aparecem marcadas como não implementadas.

### Passo 4: escrever o arquivo de orientação para agentes

Não existe `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` nem ADR no projeto.
Um agente ou pessoa que entre neste repositório não tem como saber que `prompts/` é código morto, que o layer hexagonal não tem portas, ou quais bugs são estado conhecido em vez de regressão sua.

Crie um `CLAUDE.md` na raiz contendo, no mínimo:

- Os comandos que **de fato** funcionam para instalar, testar, lintar e rodar.
- O mapa das camadas, com a observação de que vários diretórios `domain/` estão vazios.
- A lista explícita do que é código morto: o diretório `prompts/`, as dependências declaradas e nunca importadas, as ferramentas registradas e inalcançáveis.
- Um ponteiro para `plans/README.md`, dizendo que os defeitos conhecidos estão planejados lá e não devem ser corrigidos ad hoc.

Isso é o que impede o próximo agente de "consertar" a coisa errada.

**Verificar**: o arquivo existe e cada comando citado nele foi executado com sucesso por você.

### Passo 5: registrar as decisões de arquitetura que ninguém escreveu

Crie de três a cinco ADRs curtos em `docs/adr/`, um por decisão, cada um com contexto, decisão e consequência.
Candidatos, todos com evidência no código:

- Domínio em Pydantic com persistência em SQL cru, sem mapeamento ORM.
- Ferramentas chamando o backend simulado em processo, e não por HTTP.
- Prompts embutidos no código, apesar da existência do diretório `prompts/`.
- Redis em vez de fila com broker completo, e LangGraph em vez de outras bibliotecas de agente — o `docs/ai-assisted-development.md:14` afirma que essa avaliação foi feita, e o resultado nunca foi registrado.

Se você não souber a motivação real de uma decisão, **escreva o ADR com a seção de contexto marcada como desconhecida** em vez de inventar uma justificativa. Um ADR com lacuna honesta vale mais que um com racional fabricado.

**Verificar**: `ls docs/adr/` → lista os arquivos criados.

## Plano de teste

Documentação não tem teste automatizado neste projeto. A verificação é procedimental:

- Todo comando citado no README ou no `CLAUDE.md` deve ter sido executado por você, com o resultado registrado no relatório final.
- Toda afirmação sobre comportamento deve ter `arquivo:linha` no seu relatório, mesmo que não apareça no texto final.

## Critérios de pronto

- [ ] As treze afirmações da tabela foram verificadas e tratadas, com a lista de três colunas no relatório final
- [ ] `grep -in "langfuse\|checkpointer\|FinOps" README.md` → toda ocorrência descreve o estado real ou está sob "não implementado"
- [ ] `docs/ai-assisted-development.md` não cita artefato ausente ou excluído do versionamento
- [ ] `CLAUDE.md` existe na raiz e cada comando nele foi executado com sucesso
- [ ] `ls docs/adr/` lista pelo menos três ADRs
- [ ] Nenhum arquivo de código de produção foi modificado (`git status`)
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- Você descobrir que uma afirmação do README é **verdadeira** e a tabela de "Estado atual" está errada. Reporte — significa que este plano foi escrito sobre premissa falsa, e o resto dele precisa ser reavaliado.
- Corrigir a documentação exigir mudar código para o texto ficar verdadeiro. A regra é o oposto: o texto se ajusta ao código.
- Não conseguir verificar a tag do Ollama do `README.md:162`. Deixe como está e registre a incerteza; alterar identificador de modelo por suposição quebra o setup de quem seguir a documentação.

## Notas de manutenção

- **A regra que este plano institui**: afirmação sobre comportamento no README precisa de `arquivo:linha` que a sustente. Se a evidência sumir num refactor, o texto vai junto.
- Um revisor deve conferir por amostragem: escolher três afirmações do README novo e verificar no código. Se uma falhar, o plano não foi cumprido.
- Este plano deve ser o **último** a ser executado entre os oito, porque descreve o estado final. Se rodar antes dos planos 003 a 007, ele precisará ser revisitado.
