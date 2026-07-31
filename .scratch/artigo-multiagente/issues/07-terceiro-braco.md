# 07 — O experimento tem um terceiro braço?

Type: grilling
Status: open
Blocked by: 03

## Question

O experimento roda dois arms (multi-agente vs agente único) ou três?

Origem: `research/03-storm-controversia.md`, ponto cego da literatura.

O rótulo "multi-agente" mistura três variáveis que ninguém separa:

1. compute extra (mais chamadas ao modelo);
2. escopo reduzido de ferramentas por chamada (cada especialista vê só as suas);
3. isolamento de contexto (cada especialista tem seu próprio histórico).

O terceiro braço proposto isola a variável 2: **agente único, contexto completo, mas conjunto de ferramentas e política filtrados pelo intent detectado.**

Por que interessa: se esse braço empatar com o multi-agente, o ganho vinha do escopo de ferramenta, não da arquitetura de agentes.
Esse é um resultado original, barato e defensável em escala de graduação — e ele responde diretamente à evidência de que modelos menores degradam quando muitas ferramentas competem no mesmo contexto.

## Decisões a fechar

1. Roda dois braços ou três?
2. Se três: o terceiro braço reusa o roteador existente para detectar intent, ou usa um classificador separado? Reusar o roteador do arm A o torna dependente do arm A — decidir se isso é aceitável e como é reportado.
3. Se três: cabe em 5-7 páginas com três colunas de tabela e a discussão correspondente? Se não couber, o terceiro braço vira trabalho futuro declarado.
4. Custo de implementação do terceiro braço, medido depois que o ticket 03 mapear o harness.

## Dependência descoberta depois

Este ticket pressupõe que o braço A decide ferramenta via LLM.
Descobriu-se que ele não decide — usa um dicionário fixo `INTENT_TOOLS`.
Resolver junto com [O braço multi-agente precisa usar tool calling do LLM?](09-o-que-esta-sendo-comparado.md); a contagem de braços depende daquela decisão.

## Trade-off

Contra: mais implementação, mais execuções, mais espaço no artigo — e o artigo tem 5 a 7 páginas.
A favor: sem ele o artigo compara duas arquiteturas; com ele o artigo explica **por que** uma ganha. É a diferença entre relato e contribuição.

## Answer

<!-- preencher na resolução -->
