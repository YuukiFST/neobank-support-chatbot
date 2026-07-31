# 04 — O que conta como sucesso de tarefa, e quem julga

Type: grilling
Status: open
Blocked by: 03

## Question

Qual a definição operacional de "sucesso da tarefa" — o desfecho primário do artigo — e qual mecanismo a aplica?

Decisões a fechar:

1. Sucesso é binário por conversa, ou composto por componentes (rota correta, tool correta com argumentos corretos, resposta factualmente correta, ausência de vazamento de dado de outro cliente)?
2. Quem julga: verificação determinística contra o gabarito do JSONL, o LLM-as-judge de `prompts/judge.md`, anotação manual do autor, ou combinação?
3. Se houver LLM-as-judge: qual modelo julga, e como a validade dele é defendida na banca. O padrão aceito é medir concordância com anotação humana numa amostra — quantos casos, qual limiar de concordância aceitável.
4. O juiz pode ser o mesmo modelo que gera as respostas? Risco de viés de auto-avaliação — decidir e justificar.
5. Como um caso que escala para humano é pontuado: sucesso, falha, ou categoria própria?
6. Além do desfecho primário, registrar métricas decompostas de tool calling: `valid_json@1`, `correct_function@1`, `correct_args@1`. Motivo em `research/01-modelo-local.md`: o placar de sucesso é cego — há medição de dois modelos com placar idêntico no τ²-bench em que um alucina nome de ferramenta 2,5× mais que o outro, porque o orçamento de retry absorve o erro antes de ele aparecer no resultado final. Sem decompor, o artigo relata um empate que não existe.

Um LLM-as-judge que julga a própria saída, sem validação humana nenhuma, é o ponto mais atacável do artigo em banca.
Este ticket existe para blindar isso.

## Precedente levantado pela literatura (ver `research/02-literatura.md`)

O τ-bench (Yao et al., ICLR 2025) define sucesso como produto de duas verificações: a ação executada está correta **e** a saída contém a informação exigida, com a parte de ação avaliada por **comparação do estado final do banco de dados** contra um estado esperado, não por julgamento de texto.
Esse critério é determinístico, defensável em banca e já casa com a arquitetura deste repo, que tem PostgreSQL e tools que escrevem nele.

Alerta correspondente: o `eval/runner.py` atual julga por correspondência de substring isolada, e um preprint levantado mede esse critério com concordância próxima do acaso (kappa 0,049).
Substring sozinho não sustenta o desfecho primário do artigo.
A decisão deste ticket deve escolher entre adotar o critério do τ-bench, reter o LLM-as-judge com validação humana declarada, ou combinar os dois.

## Answer

<!-- preencher na resolução -->
