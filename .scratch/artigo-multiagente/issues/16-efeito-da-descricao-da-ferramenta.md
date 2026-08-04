# 16 — O artigo replica o efeito de descrição do BiasBusters?

Type: grilling
Status: open
Blocked by: 15

## Question

O experimento inclui uma manipulação da **redação das descrições** das ferramentas, mantendo a função idêntica?

Origem: BiasBusters (Blankenstein et al., ICLR 2026, ficha em `research/02-literatura.md` §3.5). O paper afirma que a similaridade semântica entre a consulta e os metadados da ferramenta domina a seleção, e que pequenas edições de descrição deslocam significativamente a escolha.

Por que interessa aqui: das duas âncoras, esta é a que produz a demonstração mais barata e mais visual. Mesma tarefa, mesma ferramenta, mesmo modelo, só o texto da descrição muda — e a escolha muda junto. Cabe numa figura.

O domínio ajuda: o chatbot tem verbos que se sobrepõem entre especialistas (consultar saldo / consultar fatura / consultar limite), que é exatamente a condição de confusão que a Anthropic descreve em §3.9.

## Decisões a fechar

1. Entra no artigo como manipulação medida, ou fica como trabalho futuro declarado? Com 5-7 páginas, somar isto às três condições do ticket 15 pode estourar o espaço.
2. Se entra: quantas variantes de descrição por ferramenta, e quem as escreve. Escrever uma variante deliberadamente ruim e apresentá-la como neutra é manipulação — o critério de redação precisa ser declarado antes.
3. Quais pares de ferramentas são o alvo. Candidatos naturais no repo: `get_invoice` contra `get_cards` (ambos "consultar cartão"), `get_balance` contra `get_transactions` (ambos "consultar conta").
4. A métrica é a taxa de troca de escolha entre variantes, ou a acurácia contra o gabarito? São perguntas diferentes; BiasBusters mede viés, não acerto.
5. Relação com a decisão 4 do ticket 15: lá a paridade de descrições é **controlada** para não confundir; aqui ela é **manipulada** de propósito. Precisam ser experimentos separados e declarados como tal, senão um invalida o outro.

## Answer

<!-- preencher na resolução -->
