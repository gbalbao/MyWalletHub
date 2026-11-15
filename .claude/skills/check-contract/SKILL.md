---
name: check-contract
description: Aciona o integration-reviewer para validar se Consolidator, Visualizer e ADC estão coerentes com a spec e com contracts/. Use depois que os subagentes concluírem.
---
1. Identifique a spec em questão (argumento ou a mais recente em `specs/`).
2. Delegue ao subagente `integration-reviewer`, informando o caminho da spec.
3. Apresente as divergências ao usuário por gravidade. Para cada quebra, indique qual subagente deve corrigir e pergunte se deve delegar.
