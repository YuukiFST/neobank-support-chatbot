# 14 — Defeitos do braço A que contaminam o experimento

Type: grilling
Status: open
Blocked by: —

## Question

O braço A entra no experimento como está, com defeitos, ou é corrigido antes?

A pergunta não é técnica, é metodológica.
Se o braço A perde por defeito de implementação, o artigo mede a qualidade do código do autor, não a arquitetura multi-agente.
Se é corrigido, é preciso declarar que foi corrigido e o que mudou — caso contrário o experimento não é reprodutível a partir do repositório publicado.

## Defeitos levantados pelo ticket 03, verificados no código

1. **Três intents nunca executam a ferramenta correta.** `tools.py:156-164` mapeia `card_pay`, `limit_increase` e `block_card` todos para `["get_cards"]`. As ferramentas `pay_invoice`, `request_limit_increase` e `block_card` existem no registro e nunca são executadas. São 4 dos 15 casos do dataset afetados.
2. **`prompts/` é diretório morto.** Nenhum arquivo dele é carregado; os prompts reais estão embutidos em `agent.py:45-79`. Um leitor do artigo que for ao repositório procurar os prompts do experimento encontra arquivos que não têm efeito.
3. **Dois casos do dataset são mecanicamente impossíveis de passar** (`eval_009` e `eval_013`), e `eval_013` está rotulado como português mas escrito em inglês.
4. **`expected_tool` nunca é lido por código.** O campo existe no dataset e não é verificado por nada.
5. **O intent `pix_status` não tem nenhum caso de teste**, apesar de estar entre os nove.

## Decisões a fechar

1. Corrigir o defeito 1 antes do experimento? Ele é o único que altera resultado de forma direta e grande.
2. Corrigir os demais, ou declará-los como limitação?
3. Se corrigir: o artigo relata o estado corrigido e aponta o commit, ou relata os dois estados?
4. A correção precisa ser feita **antes** de qualquer execução medida — corrigir no meio contamina a série.

## Nota de honestidade

Estes defeitos foram encontrados enquanto se planejava o experimento, não durante ele.
Corrigi-los agora é legítimo e não é manipulação de resultado.
O que seria manipulação é corrigir só o braço que perdeu, depois de ver o placar.

## Answer

<!-- preencher na resolução -->
