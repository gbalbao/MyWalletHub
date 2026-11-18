---
name: weekly-post
description: Gera o rascunho do post semanal de LinkedIn sobre o progresso do MyWallet, a partir do diário, dos cards fechados e do git. Rode uma vez por semana.
---
1. Leia `docs/story/estilo.md` (voz e regras) e `docs/story/origem.md` (história e tom). Se `estilo.md` ainda não estiver preenchido, avise o usuário e use um tom simples e direto.
2. Reúna o material dos últimos 7 dias:
   - entradas de `docs/journal/` com data na semana e `Vale post: sim`;
   - cards concluídos no ClickUp (se o conector estiver ativo; `clickup_filter_tasks`);
   - `git log --since="7 days ago" --date=short --pretty="%ad %s"` em ../consolidator, ../visualizer e ../adc, só para confirmar e complementar.
3. Escolha UM tema principal para o post. Se a semana não tiver nada que valha post, use uma ideia de `docs/story/posts/estoque.md` (e marque-a como usada) ou diga ao usuário que a semana foi fraca.
4. Escreva o rascunho em português, no estilo do usuário, seguindo o fio: por que fiz isso (problema) → o que ganhamos (benefício) → o que o app faz agora. Gancho forte na primeira linha, parágrafos curtos, no máximo uma chamada para conversa no final. Sem listas de tecnologias para impressionar.
5. Regras de credibilidade e segurança:
   - só afirme o que é verdade e foi entregue; nunca invente métricas;
   - nada de tokens, segredos, detalhes de segurança, dados reais de carteira ou de terceiros;
   - o app é ferramenta de organização e análise, nunca recomendação de investimento; evite promessas de retorno.
6. Salve em `docs/story/posts/AAAA-MM-DD-semana.md` com: o rascunho, 2 variações de gancho, sugestão de imagem ou print, e as fontes usadas (entradas do diário, cards).
7. Mostre o rascunho ao usuário. Nunca publique nada.
