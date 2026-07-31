# 06 — Ferramenta de escrita ABNT e política anti-plágio

Type: grilling
Status: open
Blocked by: —

## Question

Como o artigo é fisicamente escrito, e qual o processo que garante originalidade?

Decisões a fechar:

1. ~~Ferramenta de escrita.~~ **Decidido em 2026-07-31: Google Docs.** Consequências a resolver junto com o item 2: o Docs não tem estilo ABNT nativo, então margens, fonte, entrelinhamento, recuo de citação longa e numeração de seção são configurados à mão a partir da seção 7 de `research/05-normas-abnt.md`. Exportar em PDF ao final.
2. Gerenciamento de referências: manual, ou Zotero com o plugin de Google Docs. Deve produzir citação e referência conforme NBR 10520:2023 e NBR 6023:2025 — atenção ao fato de que estilos ABNT distribuídos para gerenciadores costumam estar na versão antiga da norma, com citação em caixa-alta.
3. Política anti-plágio operacional, dado que o usuário tratou isso como restrição inegociável:
   - Nenhum trecho de fonte entra no texto sem aspas e citação direta com página.
   - Paráfrase é reescrita completa, não troca de sinônimos.
   - Texto rascunhado por LLM é reescrito na voz do autor antes de entrar no artigo — usar a skill `no-ai-slop`.
   - Qual verificador roda antes da entrega e em que momento.
4. ~~**Declaração de uso de IA.**~~ **Resolvido pelo ticket [13](13-declaracao-de-uso-de-ia.md):** subseção numerada ao fim do Método, com um dos três modelos de `research/06-declaracao-de-ia.md`. Resta ao autor escolher qual dos três modelos usar e preencher ferramenta, versão e período.

   Texto original do item, mantido como registro:
   **Declaração de uso de IA.** `research/04-marcadores-de-ia.md` levantou que a Portaria CNPq nº 2.664/2026 e a Deliberação Unicamp CONSU-A-005/2026 exigem declaração explícita de uso de ferramenta de IA em trabalho acadêmico. Decidir: qual a política da sua instituição, onde a declaração entra no artigo (nota de rodapé, seção de método, agradecimentos), e o que exatamente ela declara. Declarar o uso é proteção, não confissão — o risco está em omitir e ser questionado depois.
5. Idioma do artigo: português. Confirmar, e definir como termos técnicos em inglês são tratados (itálico, glossário, tradução).
5. Onde o PDF e os fontes vivem: neste repo, ou fora dele.

## Insumos

Duas pesquisas alimentam este ticket sem bloqueá-lo:

- [Normas ABNT aplicáveis a este artigo](11-normas-abnt.md) — o conteúdo normativo, em `research/05-normas-abnt.md`. A escolha de ferramenta do item 1 pode ser feita antes dela; a conferência final não.
- [Marcadores linguísticos de texto gerado por IA](10-marcadores-de-texto-de-ia.md) — em `research/04-marcadores-de-ia.md`. Vira o checklist de revisão do item 3, aplicado antes da entrega.

## Answer

<!-- preencher na resolução -->
