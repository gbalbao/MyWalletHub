---
name: new-spec
description: Cria uma nova especificação de feature em specs/ a partir da discussão atual, usando o modelo padrão. Use quando o escopo de uma feature foi acordado.
---
1. Descubra o próximo número livre em `specs/` (NNN com 3 dígitos).
2. Copie `specs/_template.md` para `specs/NNN-nome-curto.md` e preencha todas as seções com o que foi decidido na conversa. Não invente: o que estiver em aberto vai em "Riscos e dúvidas".
3. Em "Mudanças de contrato", leia o código atual do Consolidator para descrever campos reais. Se houver mudança de API, proponha o ajuste em `contracts/`.
4. Critérios de aceite devem ser verificáveis. Tarefas por serviço devem ser pequenas o bastante para um card cada.
5. Mostre um resumo curto ao usuário e peça confirmação antes de criar cards.
