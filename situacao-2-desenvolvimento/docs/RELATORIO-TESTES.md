# 🧪 Relatório de Testes: Situação 2

> Testes automatizados com **pytest** que cobrem o back-end e as telas (front-end renderizado).
> A validação com usuários reais (5 colegas) e os testes de sistema ficam na Situação 3.

## 1. Resumo

| Indicador | Resultado |
|-----------|-----------|
| Testes automatizados | **173** |
| Aprovados | **173 (100%)** |
| Cobertura de código (`app/`) | **99%** (1.036 instruções, 13 não executadas) · meta do RNF09: ≥ 80% ✅ |
| Bancos de dados testados | **SQLite** (memória) e **MariaDB 10.11** (compatível com MySQL 8) |
| Tempo de execução | ≈ 11 s (SQLite) · ≈ 15 s (MariaDB) |

## 2. Níveis de teste (Modelo V)

| Nível do Modelo V | O que verifica | Arquivos | Qtd. |
|-------------------|----------------|----------|:----:|
| **Teste unitário** | Regras de negócio isoladas, sem banco nem servidor: Roda de Camelot, BPM, classificação, sugestões, validações | `test_harmonia.py`, `test_validacao.py` | 110 |
| **Teste de integração** | Rota → Controller → Service → Model → banco → HTML: telas, formulários, mensagens, CSV | `test_auth.py`, `test_faixas.py`, `test_setlists.py`, `test_eventos_ajuda.py` | 49 |
| **Segurança e banco** | Isolamento entre usuários, CSRF, XSS, SQL Injection, páginas de erro, restrições do banco | `test_seguranca_e_banco.py` | 14 |
| Teste de sistema / aceitação | Uso real no navegador por colegas | *Situação 3* | — |

## 3. Testes por requisito (rastreabilidade)

| Requisito / Regra | O que foi testado | Exemplos de testes |
|-------------------|-------------------|--------------------|
| RF01, RN01 | Cadastro, e-mail único, senha forte, dados mantidos após erro | `test_cadastro_*`, `test_senha_forte` |
| RF02, RNF01 | Login/logout, senha em hash, rotas protegidas, redirecionamento seguro | `test_login_*`, `test_senha_guardada_como_hash` |
| RF03, RN02–RN05 | Cadastrar, editar, excluir, duplicidade, limites de BPM/energia/duração | `test_cadastrar_faixa*`, `test_validar_faixa_erros` (14 casos) |
| RF04 | Busca, filtros por gênero/tom/BPM, ordenação, paginação | `test_listar_filtrar_e_ordenar`, `test_paginacao` |
| RF05, RN14 | CRUD de eventos; excluir evento desvincula setlists | `test_crud_evento`, `test_excluir_evento_desvincula_setlists_rn14` |
| RF06, RN13, RN15 | Criar/editar/excluir setlist; itens em cascata; evento de outro usuário | `test_criar_setlist_*`, `test_excluir_setlist_mantem_faixas_rn13` |
| RF07, RF08, RN10 | Adicionar, faixa repetida, remover (reorganiza posições), subir/descer | `test_adicionar_*`, `test_remover_*`, `test_mover_*` |
| RF09, RN11 | Sugestões: filtro por tom e BPM, ordem, limite de 10 | `test_sugestoes_*` |
| RF10, RF11, RN06–RN09 | Compatibilidade de tom (incl. 12↔1), BPM com limite exato de 6%, Suave/Atenção/Arriscada, pontuação | `test_tipo_compatibilidade` (11 casos), `test_bpm_compativel_*`, `test_transicao_*` |
| RF12, RF13 | Curva de energia, duração total, BPM médio | `test_curva_de_energia`, `test_analise_*` |
| RF15 | Painel com totais e estado vazio | `test_painel_*` |
| RF16, RF17 | Importar CSV (`;` ou `,`, UTF-8 ou Latin-1, cabeçalho em inglês, erros por linha); exportar CSV | `test_importar_csv*`, `test_exportar_csv` |
| RN12 | Faixa em uso não pode ser excluída (na aplicação **e** no banco) | `test_excluir_faixa_em_setlist_e_bloqueado_rn12`, `test_banco_impede_excluir_faixa_em_uso` |
| RNF02 | Usuário não vê nem altera dados de outro (9 rotas → 404) | `test_usuario_nao_acessa_dados_de_outro` |
| RNF03 | CSRF, XSS, SQL Injection | `test_csrf_*`, `test_textos_do_usuario_sao_escapados_xss`, `test_busca_com_aspas_*` |
| RNF11 | 404/500 amigáveis, sem detalhes técnicos; upload grande demais | `test_pagina_404_*`, `test_pagina_500_*`, `test_upload_grande_demais` |

## 4. Exemplo de caso de teste documentado

| Campo | Conteúdo |
|-------|----------|
| **ID** | CT-HARM-07 (`test_analise_do_setlist_rascunho_de_demonstracao`) |
| **Requisito** | RN08, RN09, RF13 |
| **Entrada** | Setlist: 7A/121 → 8A/118 → 5A/130 → 6A/140 → 9A/120 (durações 330, 372, 180, 410, 345 s) |
| **Resultado esperado** | Transições: Suave, Arriscada, Atenção, Arriscada · pontuação 25% · duração 1637 s (27:17) · BPM médio 125,8 |
| **Resultado obtido** | Igual ao esperado ✅ |
| **Observação** | É o mesmo setlist do protótipo da Situação 1, o que mostra que a implementação segue o que foi especificado |

## 5. Defeitos encontrados pelos testes e corrigidos

Os testes encontraram **defeitos reais** durante o desenvolvimento, que foram corrigidos antes da entrega:

| # | Defeito | Como foi encontrado | Correção |
|---|---------|--------------------|----------|
| D01 | Na importação de CSV, o número da linha com erro ficava errado quando o arquivo tinha linhas em branco | `test_importar_csv` esperava "Linha 6" e recebeu "Linha 5" | Usar `leitor.line_num` (linha real do arquivo) |
| D02 | Excluir um usuário com setlists falhava: o ORM tentava apagar as faixas antes dos itens que as referenciam (RN12) | `test_seed_demo` (recriar a demonstração) | Apagar os setlists antes do usuário |
| D03 | Trocar a ordem de faixas falhava **só no MySQL**: a posição temporária 65000 estoura o `SMALLINT` (máx. 32767); o SQLite não verifica esse limite | Rodar a suíte contra o MariaDB (`test_mover_subir_e_descer`) | Usar "maior posição + 1" como posição temporária |
| D04 | O SQLite não fazia autoincremento na tabela `genero` (`SMALLINT` não é `INTEGER PRIMARY KEY`) | Primeira execução da aplicação | Tipo `SMALLINT` no MySQL e `INTEGER` no SQLite (`with_variant`) |
| D05 | Títulos de músicas eram inseridos no gráfico via `innerHTML` sem escape (risco de XSS) | Revisão de código (alerta de segurança) | Função `esc()` no `app.js` + teste de XSS |

> **Lição aprendida (D03):** testar só em SQLite não basta; os testes precisam rodar também no SGBD de produção.

## 6. Verificação contra o banco da Situação 1

A aplicação foi executada sobre o banco criado pelo script `situacao-1-planejamento/sql/01_schema_mysql.sql`
(e não pelas tabelas geradas pelo ORM). Login com o usuário de demonstração, editor, sugestões, adicionar, reordenar,
remover, bloqueio da RN12 e exportação funcionaram, o que confirma que o código e o projeto físico estão coerentes.

## 7. Como reproduzir

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Saída obtida:

```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/controllers/auth.py              63      0   100%
app/controllers/faixas.py           104      0   100%
app/controllers/setlists.py         129      0   100%
app/services/harmonia.py            132      0   100%
app/services/validacao.py           129      0   100%
app/services/csv_service.py          76      3    96%
...
TOTAL                              1036     13    99%
173 passed
```
