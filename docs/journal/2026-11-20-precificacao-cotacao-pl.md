# Cotação de verdade e lucro sem prejuízo inventado

- **Spec:** `specs/004-precificacao-cotacao-pl.md`
- **Serviços:** Consolidator, Visualizer, hub
- **Data:** 2026-11-20

## Problema
- A tela de ativos mostrava como "cotação" o preço do dia em que o ativo foi cadastrado, e esse preço nunca mudava. O lucro e o potencial de valorização saíam errados.
- Quando a cotação de um ativo não chegava, o custo dele continuava sendo contado, e o painel mostrava um prejuízo que não existia.
- O "valor justo" era uma conta automática feita só no cadastro, sem relação com as análises que a pessoa faz depois.

## Solução
- Toda tela que mostra cotação usa o preço de mercado do momento. Sem cotação, aparece "sem cotação", nunca zero.
- O lucro de cada carteira e do total considera só os ativos que têm cotação. Um aviso lista os que ficaram de fora.
- O valor justo é a última análise que a pessoa calculou, com o método e a data, por exemplo "Graham, 12/11/2026". Sem análise, a tela oferece um atalho para calcular.

## Benefício
- Os números de lucro e de potencial refletem o mercado atual.
- Uma falha momentânea na cotação não aparece mais como perda.
- O valor justo mostra uma análise que a pessoa escolheu fazer.
- Os totais vêm de um lugar só, o servidor. A tela não refaz as contas, então o painel e a carteira mostram sempre os mesmos totais.

## Aprendizado
- **"Sem dado" não é zero.** Trocar um valor ausente por 0 parece inofensivo, mas vira prejuízo falso ou potencial falso. A regra foi aplicada ponta a ponta, e a revisão ainda achou um contador que mostrava 0 quando a busca falhava.
- **Uma fonte para cada número.** Enquanto a tela somava por conta própria, os totais divergiam do servidor. Calcular num lugar só eliminou a divergência.

## Vale post
Sim. "Por que o seu app mostra um prejuízo que não existe" é uma dor que qualquer investidor reconhece. O antes e depois é visual.

## Material
- Print do painel antes e depois com uma carteira de exemplo, mostrando o prejuízo falso que some.
- Print do aviso de ativos sem cotação, com tickers de exemplo.
- Print do valor justo com método e data, e do estado "sem valuation" com o atalho.

## Pendências
- A tela de ativos ficou mais lenta, porque busca a cotação de cada ativo a cada abertura. O cache entre leituras entra na spec 008.
- Na spec 008, porque o cadastro de um ativo consulta o preço duas vezes, e uma falha na segunda deixa o ativo sem cotação na resposta.
- A moeda e o horário da cotação ainda não aparecem na tela (spec 006).
- Alguns campos do front ainda não marcam corretamente quando podem vir vazios (spec 006).
