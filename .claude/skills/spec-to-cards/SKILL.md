---
name: spec-to-cards
description: Transforma uma spec de specs/ em cards no ClickUp, um por serviço, com critérios de aceite e link para a spec. Use após a spec ser aprovada.
---
Requer o conector ClickUp ativo (tools `clickup_*`).

1. Leia a spec indicada. Se não houver, use a mais recente de `specs/`.
2. Use `clickup_get_workspace_hierarchy` para achar a lista do MyWallet. Se houver dúvida, pergunte ao usuário e não crie nada antes.
3. Crie um card por serviço com tarefas na spec (`[Consolidator] título`, `[Visualizer] ...`, `[ADC] ...`) usando `clickup_create_task`. Descrição: contexto em 2 linhas, tarefas como checklist, critérios de aceite, mudanças de contrato relevantes e caminho da spec.
4. Indique dependências na descrição (ex.: Visualizer depende do endpoint do Consolidator).
5. Escreva os links dos cards na seção "ClickUp" da spec.
6. Responda com a lista de cards criados (título e link).
