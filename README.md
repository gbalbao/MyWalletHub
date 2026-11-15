# MyWallet Hub

Repositório de coordenação do MyWallet. Não contém código de aplicação; guarda o que une os três serviços.

## Serviços (repositórios irmãos)
- `../consolidator`: backend Java + Spring (dono dos dados e da API)
- `../visualizer`: frontend Angular
- `../adc`: coletor de dados de ativos (Python)

## Estrutura
- `specs/`: uma especificação por feature (objetivo, critérios de aceite, mudanças de contrato, tarefas por serviço)
- `contracts/`: contratos entre serviços (OpenAPI e schemas), fonte de verdade da integração
