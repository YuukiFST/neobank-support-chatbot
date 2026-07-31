# Plano 007: Fazer os intents de cartão executarem a ação que prometem

> **Instruções ao executor**: siga o plano passo a passo.
> Rode todo comando de verificação e confirme o resultado esperado antes de seguir.
> Se ocorrer qualquer condição da seção "STOP", pare e reporte — não improvise.
> Ao terminar, atualize a linha deste plano em `plans/README.md`.
>
> **Verificação de deriva (rode primeiro)**: `git diff --stat 34264cb..HEAD -- services/agent_api/application/tools.py services/agent_api/application/agent.py services/agent_api/infrastructure/mock_banking_api.py`
> Divergência entre o código vivo e os trechos de "Estado atual" é condição de STOP.

## Status

- **Prioridade**: P1
- **Esforço**: M
- **Risco**: MED — liga ações de escrita a intents classificados por um modelo de linguagem
- **Depende de**: `plans/004-falhas-visiveis.md`
- **Categoria**: bug
- **Planejado em**: commit `34264cb`, 2026-07-31

## Por que isso importa

Três dos nove intents do catálogo são operações vazias: pagar fatura, aumentar limite e bloquear cartão.
O agente responde ao cliente como se a ação tivesse acontecido, e nada aconteceu.
Num contexto financeiro, esse é o pior modo de falha possível — pior que erro, porque não deixa rastro nem para o cliente nem para o operador.

A regra de negócio de aumento de limite existe em **três versões divergentes**, e a única que descreve a política real nunca é executada.

Há um risco de direção oposta ao corrigir: passar a executar escrita a partir de intent classificado por modelo de linguagem sem confirmação explícita troca "nada acontece" por "acontece o que não devia". O plano trata isso no passo 4, e não é opcional.

## Estado atual

### O mapeamento que anula três intents

`services/agent_api/application/tools.py:156-164`:

```python
# Intent → tools to run before specialist LLM call
INTENT_TOOLS: dict[str, list[str]] = {
    "balance": ["get_balance"],
    "pix_status": ["get_transactions"],
    "card_invoice": ["get_cards"],
    "card_pay": ["get_cards"],
    "limit_increase": ["get_cards"],
    "block_card": ["get_cards"],
    "fraud_dispute": ["get_transactions", "get_cards"],
}
```

`card_pay`, `limit_increase` e `block_card` executam apenas `get_cards`.

O registro de ferramentas (`tools.py:142-153`) contém as funções que deveriam ser chamadas — `pay_invoice`, `request_limit_increase`, `block_card` —, todas com validação de propriedade implementada e correta, e **nenhuma delas é alcançável por intent nenhum**.

### A regra de negócio em três versões

1. **Prompt do especialista de risco** (`agent.py:74-78`): aprovar automaticamente até 1,5× o limite atual **se não houver transações marcadas como risco nos últimos 90 dias, senão escalar**. É a única sede da política.
2. **Backend** (`mock_banking_api.py:186-199`): aprova **sempre**, e fabrica a justificativa:

```python
            return LimitIncreaseResponse(
                card_id=card_id,
                approved=True,
                new_limit=max_auto,
                reason=f"Auto-approved: {current_limit:.2f} -> {max_auto:.2f} (within 1.5x ceiling, no risk flags)",
            )
```

Não lê `risk_flag`, não considera data, nunca escala. A frase "no risk flags" é literal na string, independentemente dos dados.

3. **Roteamento** (`agent.py:224-233`):

```python
def route_after_router(state: AgentState) -> str:
    intent = state.get("intent", "human")
    if intent in ("balance", "pix_status"):
        return "account_specialist"
    if intent in ("card_invoice", "card_pay", "limit_increase", "block_card"):
        return "card_specialist"
    if intent == "fraud_dispute":
        return "risk_specialist"
```

`limit_increase` vai para o especialista de cartão. O especialista de risco — dono da política — só é alcançável por `fraud_dispute`.

### Contexto do dado

O schema (`ops/init.sql`) define `transactions.risk_flag`, que é exatamente o campo que a política dos 90 dias exigiria e que o backend ignora.

## Comandos que você vai precisar

| Propósito | Comando | Esperado |
|---|---|---|
| Instalar | `pip install -e ".[dev]"` | exit 0 |
| Testes offline | `pytest tests/ -v -m "not requires_db"` | passa |
| Lint / tipos | `ruff check .` e `mypy shared/ services/` | exit 0 |

## Escopo

**Em escopo**:

- `services/agent_api/application/tools.py` — `INTENT_TOOLS` e o despachante
- `services/agent_api/application/agent.py` — `route_after_router` e os prompts afetados
- `services/agent_api/infrastructure/mock_banking_api.py` — a lógica de `request_limit_increase`
- Testes novos

**Fora de escopo**:

- As quatro ferramentas restantes sem intent (`lookup_cep`, `get_currency_quote`, `get_investments`, e o caso especial de `get_invoice`). São débito conhecido, tratado em outro plano.
- Autenticação e autorização na fronteira HTTP. As rotas `/mock` não checam propriedade, e isso é grave — mas é plano próprio, e este aqui não pode esperar por ele.
- Substituir o `INTENT_TOOLS` por tool calling do modelo. Essa mudança está sendo avaliada em paralelo, em um experimento sobre este repositório; **não a antecipe aqui**.

## Fluxo git

- Branch: `advisor/007-intents-de-cartao`
- Conventional Commits em inglês. Exemplo: `fix(agent): route limit increase through the risk specialist`

## Passos

### Passo 1: mover a política de aumento de limite para o código

Implemente em `mock_banking_api.py`, na função `request_limit_increase`, a regra que hoje só existe no texto do prompt:

- Aprovar até 1,5× o limite atual **apenas** se não houver transação com `risk_flag` marcada nos últimos 90 dias para aquele cliente.
- Caso contrário, retornar `approved=False` com um motivo verdadeiro, derivado dos dados.

A justificativa devolvida deve refletir o que foi de fato verificado. Nunca afirme "no risk flags" sem ter olhado.

Se os dados de semente não tiverem transação marcada como risco para nenhum cliente, adicione uma em `data/seeds/` para que o caminho negativo seja exercitável — e registre isso no relatório final.

**Verificar**: `pytest tests/unit -v -k limit` → passa, com um teste para cada ramo (aprovado e negado).

### Passo 2: rotear o aumento de limite para o especialista de risco

Em `route_after_router`, remova `limit_increase` do grupo do especialista de cartão e mande-o para `risk_specialist`.

Ajuste o prompt do especialista de risco se necessário para tratar os dois casos (disputa de fraude e pedido de limite) sem confundi-los.

**Verificar**: teste unitário direto sobre `route_after_router` — é função pura. Nove intents, nove asserções. Não existe nenhum teste de aresta do grafo hoje; este é o primeiro.

### Passo 3: ligar as ferramentas de escrita aos seus intents

Atualize `INTENT_TOOLS` para que `card_pay` execute `pay_invoice`, `limit_increase` execute `request_limit_increase` e `block_card` execute `block_card` — mantendo `get_cards` onde ele for necessário para resolver qual cartão.

**Não faça este passo antes do passo 4.** Ligar escrita sem confirmação é regressão de segurança, não correção.

**Verificar**: `pytest tests/ -v -m "not requires_db"` → passa.

### Passo 4: exigir confirmação antes de qualquer escrita

Esta é a parte que impede a correção de virar um problema pior.

Nenhuma operação de escrita — pagar fatura, bloquear cartão, aumentar limite — pode ser executada apenas porque o classificador de intent achou que o cliente queria.
Implemente uma etapa de confirmação explícita: o agente descreve a ação pretendida, e a execução só ocorre num turno seguinte, mediante confirmação do cliente.

**Restrição importante**: o sistema hoje **não tem memória entre turnos** — o estado é montado do zero a cada requisição, e o grafo é compilado sem checkpointer.
Isso significa que confirmação em dois turnos **não é implementável** sem a memória de conversa, que é outro plano.

Diante disso, escolha uma das duas saídas e registre a escolha:

- **Opção A (recomendada)**: implemente a confirmação e declare no `README.md` que os intents de escrita ficam desabilitados até a memória de conversa existir. O passo 3 então liga apenas o que é leitura, e as escritas permanecem fora do `INTENT_TOOLS` com um comentário explicando por quê.
- **Opção B**: implemente a confirmação dentro de um único turno, com o cliente repetindo a intenção de forma inequívoca no mesmo texto. Mais frágil, e você precisa documentar a fragilidade.

Se escolher a Opção A, o passo 3 fica parcialmente adiado — e isso é um resultado legítimo deste plano, não uma falha.

**Verificar**: existe teste afirmando que uma requisição de escrita sem confirmação **não** altera estado.

### Passo 5: alinhar a documentação ao comportamento

O `README.md` descreve o intent 5 como "Card API + risk rule / escalates yes, above ceiling", e os intents 4, 5 e 6 como acionando a API de cartões.
Ajuste o texto ao que passou a ser verdade depois dos passos anteriores — inclusive se a resposta for "desabilitado até haver memória de conversa".

**Verificar**: leitura manual; o relatório final deve citar as linhas alteradas.

## Plano de teste

Novos testes, com `tests/unit/test_tools.py` e `tests/unit/test_agent_graph.py` como padrão estrutural:

1. `route_after_router` para os nove intents — a primeira cobertura de roteamento do projeto.
2. `request_limit_increase` aprovando quando não há transação de risco em 90 dias.
3. `request_limit_increase` **negando** quando há — este é o teste que prova que a política saiu do prompt e entrou no código.
4. Requisição de escrita sem confirmação não altera estado (conforme a opção escolhida no passo 4).
5. Se o passo 3 ligar alguma ferramenta: teste de que ela é efetivamente executada para o intent correspondente.

Verificação: `pytest tests/ -v -m "not requires_db"` → passa, com pelo menos 4 testes novos.

## Critérios de pronto

- [ ] `pytest tests/ -m "not requires_db"` sai com código 0
- [ ] Existe teste unitário cobrindo os nove ramos de `route_after_router`
- [ ] `grep -n "no risk flags" services/agent_api/infrastructure/mock_banking_api.py` não retorna string fabricada — a justificativa é derivada dos dados
- [ ] `limit_increase` é roteado para `risk_specialist` (comprovado por teste)
- [ ] A decisão do passo 4 (opção A ou B) está registrada em comentário no código e no relatório final
- [ ] `README.md` descreve o comportamento real dos intents 4, 5 e 6
- [ ] `ruff check .` e `mypy shared/ services/` saem com código 0
- [ ] Linha deste plano atualizada em `plans/README.md`

## Condições de STOP

- Os trechos de "Estado atual" não corresponderem ao código vivo.
- Você concluir que a confirmação exige memória entre turnos e que a Opção A não é aceitável para o dono do projeto — nesse caso a decisão é dele, não sua.
- Ligar uma ferramenta de escrita quebrar mais de dois testes existentes: sinal de que o comportamento esperado pela suíte é diferente do que este plano assume.
- O dado de semente não permitir exercitar o ramo de negação e você não conseguir adicioná-lo sem alterar o schema.

## Notas de manutenção

- **A regra que este plano institui**: política de negócio vive no código, não no texto de um prompt. Prompt pode descrever a política ao usuário; não pode ser a única sede dela.
- Um revisor deve verificar com atenção o passo 4. É o ponto onde uma correção bem-intencionada pode introduzir execução indevida de operação financeira.
- Este plano interage diretamente com um experimento científico em curso sobre este repositório, que compara o roteamento determinístico atual contra tool calling do modelo. Mudar `INTENT_TOOLS` **altera o braço de controle desse experimento** — coordene antes de mesclar, e registre o commit exato no relatório final.
