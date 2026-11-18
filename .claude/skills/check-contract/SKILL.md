---
name: check-contract
description: Aciona o integration-reviewer para validar se Consolidator, Visualizer e ADC estão coerentes com a spec e com contracts/. Use depois que os subagentes concluírem.
---
1. Identifique a spec em questão (argumento ou a mais recente em `specs/`).
2. Rode `python scripts/check_openapi.py` no hub. Ele sobe o Consolidator em dev, se ele não estiver na 8080, e compara o `/v3/api-docs.yaml` com `contracts/openapi.yaml`.
   - Saída 0: o código bate com o contrato.
   - Saída 1: divergência. Conta como **quebra**; mostre o diff.
   - Saída 2: falha de infraestrutura. Relate e siga para o passo 3 sem esse resultado.
   - Se a spec mudou a API de propósito, o contrato é atualizado primeiro (`--update` só depois de revisar o diff com o usuário).
3. Delegue ao subagente `integration-reviewer`, informando o caminho da spec e o resultado do passo 2.
4. Apresente as divergências ao usuário por gravidade. Para cada quebra, indique qual subagente deve corrigir e pergunte se deve delegar.
