---
name: start-spec
description: Começa a implementação de uma spec pronta. Primeiro revalida a spec contra o que mudou no código e no contrato desde que foi escrita, atualiza spec e cards se preciso e só então delega aos subagentes. Use sempre que for iniciar uma spec.
---
Argumento: número da spec. Sem argumento, use a próxima spec pronta na ordem do backlog.

1. **Base.** Leia a spec. A linha `> Escrita em ... a partir dos commits ...`, ou a última `> Revisada em ...`, dá a data e os hashes de base. Se não houver essa linha, use a data da spec no `git log` do hub (`git log --diff-filter=A -- specs/NNN-*.md`).
2. **O que mudou desde a base**, em cada repositório (hub, `../consolidator`, `../visualizer/visualizer`, `../adc`):
   - Rode `git log --oneline <base>..HEAD`. Sem hash, use `--since=<data>`.
   - Rode `git diff --stat` no mesmo intervalo.
   - Confira as mudanças nos arquivos, DTOs, rotas e migrations que a spec cita, e em `contracts/openapi.yaml`.
   - Leia as linhas `Impacto da NNN` em "Riscos e dúvidas", que o `/close-feature` deixou.
3. **Revalidação.** Para cada critério de aceite, tarefa e linha da tabela de contrato, classifique em:
   - **Ainda vale:** nada a fazer.
   - **Mudou:** outro nome de campo, outro arquivo, outra linha, tarefa já feita por outra spec, ou um consumidor novo. Corrija o texto.
   - **Decisão afetada:** a premissa de uma decisão mudou. Pare e pergunte ao usuário com `AskUserQuestion` antes de seguir.
4. **Atualização.** Se algo mudou:
   - Edite a spec.
   - Acrescente `> Revisada em AAAA-MM-DD a partir dos commits <hashes>` abaixo da linha de base.
   - Atualize a descrição dos cards afetados no ClickUp.
   - Mostre ao usuário um resumo antes e depois e peça confirmação.
   - Se nada mudou, diga isso em uma linha, registre a linha `Revisada em` e siga sem pedir confirmação.
5. **Início.** Com a spec validada:
   - Mova para `em progresso` só os cards que serão delegados agora, os sem dependência pendente.
   - Delegue ao subagente de cada serviço, com o caminho da spec e os pontos revisados.
   - Siga o fluxo normal: `code-reviewer` até `APROVADO`, `/check-contract`, `/commit-message`, commit do usuário, cards em concluído e `/close-feature`.

Limites: não mude decisões já tomadas sem perguntar e não faça commit.
