---
name: close-feature
description: Registra o encerramento de uma feature no diário (docs/journal) em linguagem leiga, alimentando os posts semanais. Use quando uma feature for concluída e revisada.
---
Argumento: número ou nome da spec. Sem argumento, use a mais recente em `specs/`.

1. Leia a spec e confirme com o usuário que os critérios de aceite foram atendidos. Se algo ficou de fora, registre como pendência.
2. Crie `docs/journal/AAAA-MM-DD-nome-curto.md` com:
   - `Spec`: caminho. `Serviços`: quais foram afetados. `Data`: de hoje.
   - `Problema`: o que incomodava, em 2–3 linhas, linguagem de pessoa investidora, sem jargão.
   - `Solução`: o que o app faz agora, em 2–3 linhas.
   - `Benefício`: ganho real para o usuário. Só afirme o que é verdadeiro; número só se medido.
   - `Aprendizado`: uma lição técnica ou de produto, se houver.
   - `Vale post`: sim ou não, com um motivo curto.
   - `Material`: sugestões de print ou gráfico que ilustrariam (sem dados pessoais).
3. Nunca inclua segredos, tokens, nomes de clientes, dados reais de carteira ou detalhes de segurança.
4. Se o conector ClickUp estiver ativo, ofereça mover os cards da spec para concluído e só faça se o usuário confirmar.
5. Checagem de impacto nas specs prontas. Specs prontas são as de `specs/` com todos os cards em `pendente`. Para cada uma:
   - Compare com o que a feature fechada mudou: contrato, DTOs, campos, rotas, migrations e arquivos citados nas tarefas.
   - Se houver impacto, acrescente em "Riscos e dúvidas" da spec afetada uma linha `- **Impacto da NNN (AAAA-MM-DD):** <o que mudou e o que a spec precisa considerar>.` Não reescreva o resto da spec; a revisão completa é do `/start-spec`.
   - Diga ao usuário quais specs foram afetadas e se isso sugere mudar a ordem do backlog. Sem impacto, diga isso em uma linha.
6. Conte as specs prontas. Se houver menos de 3, ofereça rodar `/refill-backlog` e só rode com a confirmação do usuário.
