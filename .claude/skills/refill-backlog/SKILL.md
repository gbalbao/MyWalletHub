---
name: refill-backlog
description: Mantém 3 specs prontas (spec escrita e cards no ClickUp em pendente), escrevendo as próximas da ordem do docs/backlog-proposto.md. Use após o /close-feature ou quando o usuário pedir para repor o backlog.
---
Argumento opcional: números de spec a preparar, em ordem (ex.: `005 006 008`). Sem argumento, siga a ordem de `docs/backlog-proposto.md` (ondas e ordem dentro da onda), pulando specs rejeitadas ou já escritas.

1. **Contagem.** Specs prontas são as de `specs/` cujos cards estão todos em `pendente` no ClickUp. Uma spec com algum card em `em progresso` não conta como pronta. Se já houver 3 ou mais prontas e o usuário não passou argumento, diga isso e pare.
2. **Uma spec por vez**, até chegar a 3 prontas:
   1. Leia a seção da spec em `docs/backlog-proposto.md`, os achados relacionados em `docs/estado-do-projeto.md` e os problemas conhecidos em `contracts/openapi.yaml`.
   2. Leia o código atual dos serviços afetados para levantar os fatos: campos reais, arquivos e linhas, consumidores. Use subagentes Explore só se a busca for ampla. O código manda: se o backlog divergir dele, siga o código e diga isso.
   3. Separe o que é fato do que é decisão. Leve as decisões caras de desfazer ao usuário numa única rodada de `AskUserQuestion`, com até 4 perguntas por spec e a opção recomendada primeiro. Não decida design sozinho. O que ficar em aberto vai em "Riscos e dúvidas".
   4. Com as respostas, siga `/new-spec`: arquivo `specs/NNN-nome.md` a partir do modelo, decisões datadas e mudanças de contrato com os campos reais. Na primeira linha depois do título, coloque `> Escrita em AAAA-MM-DD a partir dos commits <hash curto de cada repositório afetado>`. Esses hashes são a base que o `/start-spec` usa para a revalidação.
   5. Mostre um resumo curto e peça a aprovação da spec. Com a aprovação, siga `/spec-to-cards`: um card por serviço, cards do hub na lista Hub, status `pendente` e dependências no ClickUp, inclusive com os cards das specs anteriores que ainda não foram concluídas.
3. **Ordem e sobreposição.** Se duas specs prontas mexem nos mesmos arquivos ou DTOs, registre a dependência nos cards e nas duas specs, em "Riscos e dúvidas".
4. **Final.** Liste as specs prontas na ordem em que devem ser executadas, com os links dos cards, e diga qual é a próxima (`/start-spec NNN`).

Limites: não crie cards sem a spec aprovada, não comece a implementação e não faça commit.
