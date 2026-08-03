# 15 — Desenho das condições de escopo de ferramenta

Type: grilling
Status: open
Blocked by: 09, 14

## Question

Quais condições experimentais o artigo roda, e o que exatamente muda entre elas?

Este é o ticket central do desenho depois do reenquadramento de 2026-08-03: o eixo primário é **escopo de ferramentas por chamada**, e as duas âncoras (Less is more, DATE 2025; BiasBusters, ICLR 2026) preveem que reduzir o conjunto exposto melhora a seleção.

## Condições candidatas

Nome provisório, a fixar na resolução:

| Condição | O que o modelo vê por chamada | Papel |
|---|---|---|
| **C1 — plana cheia** | todas as ferramentas do registro de uma vez | linha de base "sem mitigação" |
| **C2 — plana filtrada** | só as ferramentas do intent detectado (2-4) | mitigação **sem** mudar arquitetura |
| **C3 — multi-agente** | partição por especialista (o supervisor atual) | mitigação **com** arquitetura |

O contraste que sustenta a contribuição é **C2 contra C3**: se empatarem, o ganho vinha do escopo de ferramenta, não da arquitetura de agentes. C1 estabelece que existe um efeito a explicar.

## Decisões a fechar

1. Roda as três condições, ou só duas? Se três, cabem em 5-7 páginas com tabela e discussão?
2. Quantas ferramentas em C1? O registro tem 10 (`tools.py:142-153`). Isso está longe do limiar de 30-50 que a Anthropic cita (§3.1) e abaixo do < 20 da OpenAI (§3.4). Decidir se o conjunto é inflado com distratores para produzir efeito mensurável.
3. Se inflar: **de onde vêm os distratores?** Duas fontes já existem no repo — `lookup_cep` e `get_currency_quote` são reais, implementadas e inalcançáveis por qualquer intent hoje (`tools.py:113-137`, ausentes de `INTENT_TOOLS`). Distrator sintético inventado é mais atacável em banca que ferramenta real órfã.
4. **Paridade de nomes e descrições entre condições.** Ameaça direta à validade interna, apontada por BiasBusters (§3.5) e reforçada pela Anthropic (§3.9): se os especialistas de C3 receberem descrições melhores que as ferramentas de C1, a redação vira confundidora e o artigo mede prosa, não arquitetura. Decidir o protocolo que garante texto idêntico.
5. Em C2, **quem detecta o intent**? Reusar o roteador de C3 torna C2 dependente de C3 — decidir se é aceitável e como é reportado. Alternativa: classificador separado, que introduz sua própria taxa de erro.
6. O erro do roteador é contado contra a condição, ou os casos mal roteados são excluídos? Decidir antes de rodar, nunca depois de ver o placar.
7. Quais métricas decompostas por condição: `valid_json@1`, `correct_function@1`, `correct_args@1` (ver ticket 04, decisão 6), além de latência e tokens.

## Dependências

- **09** precisa fechar antes: sem tool calling real do LLM, nenhuma condição mede seleção. As três correções técnicas listadas lá (`ollama_chat/` em vez de `ollama/`, `tool_calls` descartado em `llm_completion()`, ausência de instrumentação de latência) são pré-requisito de execução.
- **14** precisa fechar antes: `card_pay`, `limit_increase` e `block_card` não executam a ferramenta que prometem, o que afeta 4 dos 15 casos e contamina qualquer contagem de acurácia.

## Answer

<!-- preencher na resolução -->
