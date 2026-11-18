---
name: build-timeline
description: Monta a linha do tempo do MyWallet (docs/story/timeline.md) e um estoque de ideias de posts a partir do histórico do git e da auditoria. Use no início e quando quiser atualizar os marcos.
---
Somente leitura nos repositórios.

1. Leia `docs/estado-do-projeto.md` (auditoria) e `docs/story/origem.md`.
2. Colete datas reais: `git log --reverse --date=short --pretty="%ad %s"` em ../consolidator, ../visualizer e ../adc (e no hub). Não rode auditoria nova do código: a auditoria existente dá o "o quê", o git dá o "quando". Se algo for ambíguo, marque `data aproximada`.
3. Agrupe em marcos (não em commits): um marco é algo que o usuário final percebe (login, consolidação da carteira, importador de planilha, coletor de fundamentos, gráficos etc.). Escreva `docs/story/timeline.md` em ordem cronológica com: data, marco, serviço(s), por que importou para o investidor.
4. Gere `docs/story/posts/estoque.md`: para cada marco, uma ideia de post com título provisório, ângulo (problema → benefício → o que o app faz), material sugerido e status `ideia`. Sugira também uma ordem de publicação começando pelo post de origem.
5. Mostre ao usuário o resumo dos marcos e peça ajustes. Não invente marcos que não estão no código ou no git.
