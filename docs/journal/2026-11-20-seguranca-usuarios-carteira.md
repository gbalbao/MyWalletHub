# Excluir uma carteira sem susto

- **Spec:** `specs/002-seguranca-usuarios-carteira.md`
- **Serviços:** Consolidator, Visualizer, hub
- **Data:** 2026-11-20 (feature concluída em 2026-11-19)

## Problema
Uma carteira com ações cadastradas não podia ser apagada: o app recusava e mostrava um erro genérico. A tela de login também atrapalhava. Uma senha digitada errado aparecia como "sessão expirada", e um e-mail que já tinha cadastro mostrava uma mensagem técnica incompreensível.

## Solução
- Ao apagar uma carteira com ativos, o app avisa quantos ativos ela tem e pergunta se é para seguir. Se a pessoa clicar em "Deletar mesmo assim", a carteira some com todo o histórico de uma vez. Se clicar em "Cancelar", nada muda.
- Login errado mostra "E-mail ou senha inválidos".
- Cadastro repetido mostra "E-mail já cadastrado".
- As regras de acesso às contas foram revisadas.

## Benefício
- A pessoa decide o que acontece com a carteira, com o aviso na frente, e não fica com dados pela metade: ou tudo é apagado, ou nada.
- Os erros dizem o que aconteceu, em português, e o app só pede login de novo quando é mesmo necessário.

## Aprendizado
- **O teste precisa ser parecido com a realidade.** Os testes automatizados mostravam a resposta certa, mas o servidor de verdade respondia outra coisa. Os testes novos sobem o servidor completo, e a diferença passou a aparecer.
- **Ações irreversíveis pedem duas etapas.** Recusar por padrão e só apagar com uma confirmação explícita é mais seguro do que apagar direto, e mais útil do que só recusar.

## Vale post
Sim. O popup "Deletar mesmo assim" é um exemplo concreto e fácil de mostrar de como desenhar uma ação destrutiva. O aprendizado sobre testes rende uma história curta.

## Material
- Print do popup de aviso com os botões "Cancelar" e "Deletar mesmo assim", numa carteira de exemplo.
- Print da tela de login com "E-mail ou senha inválidos".
- Diagrama simples do fluxo: excluir → aviso → confirmar ou cancelar.

## Pendências
- A tela ainda mostra alguns avisos em inglês. Eles entram na spec 009.
- Sugestões de revisão que não foram aplicadas e podem virar cards avulsos:
  - um helper único para o popup, que hoje está repetido na lista e no detalhe;
  - um teste de ponta a ponta do erro de login;
  - um teste de troca para um e-mail que já existe.
- No Visualizer, alguns testes falham por tempo esgotado na máquina local. Eles já falhavam antes desta spec.
