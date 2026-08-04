# 14 — Defeitos do braço A que contaminam o experimento

Type: grilling
Status: resolved
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

**Corrigir os defeitos 1, 3 e 4 antes de qualquer execução medida. Declarar 2 e 5 como limitação.** Resolvido em 2026-08-03.

O reenquadramento de 2026-08-03 mudou o peso da pergunta. Quando o eixo era "multi-agente contra agente único", corrigir o braço A era questão de justiça entre braços. Agora o eixo é escopo de ferramenta, e o defeito 1 deixa de ser assimetria: ele impede a medição existir.

**Defeito 1 — obrigatório corrigir.** `card_pay`, `limit_increase` e `block_card` mapeiam para `["get_cards"]`, então `pay_invoice`, `request_limit_increase` e `block_card` nunca executam. O desfecho primário do artigo é acurácia de seleção de ferramenta. Um intent cuja ferramenta correta é inalcançável tem acurácia zero por construção, em todas as condições, e não discrimina entre elas. Não é um braço em desvantagem: é um caso que não mede nada. São 4 dos 15 casos, ou seja, 27% do dataset seria ruído.

Isso torna o defeito 1 pré-requisito do ticket [Desenho das condições de escopo de ferramenta](15-condicoes-de-escopo-de-ferramenta.md), não só do experimento. O plano `plans/007-intents-que-nao-executam.md` é onde a correção acontece.

**Defeito 3 — corrigir.** `eval_009` e `eval_013` são mecanicamente impossíveis de passar, e `eval_013` está rotulado como português e escrito em inglês. Caso impossível não é caso difícil: ele adiciona ruído sem poder discriminar. Com 15 casos e o poder estatístico já apertado (ticket 08), gastar dois deles em casos mortos é caro. O rótulo de idioma errado é pior ainda, porque idioma é variável de controle declarada.

**Defeito 4 — corrigir.** `expected_tool` existe no dataset e nenhum código o lê. O desfecho primário do artigo **é** comparar ferramenta escolhida contra ferramenta esperada. O campo deixa de ser débito e passa a ser o gabarito do oráculo. A implementação pertence ao ticket [O que conta como sucesso de tarefa, e quem julga](04-definicao-de-sucesso.md).

**Defeito 2 — limitação declarada, não correção.** `prompts/` é diretório morto e os prompts reais estão embutidos em `agent.py`. Um leitor que for ao repositório procurar os prompts do experimento encontra arquivos sem efeito, o que é problema de reprodutibilidade real. Mas resolver bem exige carregamento com falha alta se faltar arquivo — mudança de arquitetura de carregamento no meio do caminho, sem ganho para a medição. O artigo declara onde os prompts vivem e cita o commit. O plano `plans/008-documentacao-honesta.md` resolve depois das execuções.

**Defeito 5 — limitação declarada.** `pix_status` não tem caso de teste. Escrever casos novos agora significa escrever casos depois de conhecer os defeitos, o que é exatamente o viés que a nota de honestidade deste ticket adverte. Se casos forem adicionados, é decisão do ticket 08 junto com o tamanho de amostra, com critério de autoria declarado antes.

**Decisão 3 do ticket — como relatar.** O artigo relata **o estado corrigido**, cita o commit congelado, e traz uma subseção curta listando o que foi corrigido antes de medir e por quê. Relatar os dois estados dobraria as execuções sem responder à pergunta de pesquisa. O que sustenta a honestidade é a ordem: os defeitos foram achados durante o planejamento, corrigidos antes de qualquer execução, e nenhum resultado foi visto antes da correção.

**Decisão 4 — confirmada.** Toda correção acontece antes da primeira execução medida. Congelamento de commit ao fim, como `plans/README.md` já determina.

**Registro de processo:** este ticket é HITL por padrão do wayfinder e foi resolvido sem a conversa ao vivo, por delegação explícita do usuário em 2026-08-03 ("decida tudo que for necessário"). Qualquer item acima pode ser derrubado sem custo — nada foi executado ainda.
