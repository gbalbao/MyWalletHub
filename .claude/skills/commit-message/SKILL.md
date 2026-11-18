---
name: commit-message
description: Gera mensagens de commit em inglês (header até 50 caracteres e body explicativo), uma por repositório alterado. Só use após o code-reviewer dar VEREDITO - APROVADO.
---
Porta de entrada: confirme que a revisão mais recente do `code-reviewer` nesta conversa terminou em `VEREDITO: APROVADO` para os repositórios em questão. Se não houve revisão, ou o veredito foi `AJUSTES NECESSARIOS`, pare e diga isso. Não gere mensagem.

Para cada repositório com mudanças (../consolidator, ../visualizer, ../adc, e o hub se houver):
1. Leia `git diff --staged` (se vazio, `git diff`) para basear a mensagem no que realmente mudou.
2. Escreva em inglês:
   - Header: no máximo 50 caracteres, modo imperativo, sem ponto final, prefixo opcional (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`) contado nos 50. Confira a contagem.
   - Linha em branco.
   - Body, quebrado em ~72 colunas: o que mudou e por quê (não como). Pode usar bullets.
3. Entregue uma mensagem por repositório, em bloco de código, com o nome do repo acima.

Nunca execute `git commit`. Apenas sugira; o usuário comita.

Ao final, se a feature da spec estiver concluída, lembre o usuário de rodar `/close-feature`.
