# Situação 1: Planejamento (versão 2.0)

Atualização do plano de projeto do **HarmoniMix**, com escopo, modelagem, IHC e banco de dados.

## Entregas da Situação 1

| Entrega pedida | Documento |
|----------------|-----------|
| Verificar e adequar o escopo/ideia | [01-escopo.md](01-escopo.md) |
| Requisitos (base para modelagem e testes) | [02-requisitos.md](02-requisitos.md) |
| Modelagem UML: casos de uso, classes, sequência, atividades | [03-modelagem-uml.md](03-modelagem-uml.md) |
| Projetos de dados: conceitual, lógico normalizado e físico | [04-banco-de-dados.md](04-banco-de-dados.md) |
| Projeto físico (scripts MySQL) | [sql/](sql/) |
| Dicionário de dados | [05-dicionario-de-dados.md](05-dicionario-de-dados.md) |
| IHC: telas, mensagens de erro, mapas, protótipo | [06-ihc-prototipo.md](06-ihc-prototipo.md) · [prototipo/index.html](prototipo/index.html) |
| Melhoria contínua (Kaizen) e críticas dos colegas | [07-historico-revisoes.md](07-historico-revisoes.md) · [formulario-critica-colegas.md](formulario-critica-colegas.md) |

## Estrutura

```
situacao-1-planejamento/
├── 01-escopo.md
├── 02-requisitos.md
├── 03-modelagem-uml.md          ← diagramas Mermaid (o GitHub desenha automaticamente)
├── 04-banco-de-dados.md
├── 05-dicionario-de-dados.md
├── 06-ihc-prototipo.md
├── 07-historico-revisoes.md
├── formulario-critica-colegas.md
├── img/                         ← prints das telas do protótipo
│   └── diagramas/               ← todos os diagramas exportados em PNG
├── prototipo/index.html         ← protótipo navegável (abrir no navegador)
└── sql/
    ├── 01_schema_mysql.sql      ← criação do banco (DDL)
    ├── 02_dados_iniciais.sql    ← tons Camelot, gêneros e dados de demonstração
    └── 03_consultas_exemplo.sql ← consultas e testes de restrições
```
