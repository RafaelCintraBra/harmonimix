# ✔️ Verificação: o produto foi construído conforme a especificação?

> A verificação compara cada artefato com o anterior (requisito → modelo → código → teste) por meio de revisões,
> inspeções e rastreabilidade. Ela olha **o caminho**. A validação, que olha **o destino** (se o usuário consegue fazer o que
> precisa), está em [VALIDACAO-COM-USUARIOS.md](VALIDACAO-COM-USUARIOS.md).

## 1. Revisão dos requisitos

Cada requisito de [02-requisitos.md](../situacao-1-planejamento/02-requisitos.md) foi revisado com as características
pedidas no material da disciplina:

| Característica | Pergunta de revisão | Resultado |
|----------------|---------------------|-----------|
| Descreve a necessidade real | O requisito resolve uma dor da persona (seção 1.6 do escopo)? | ✅ Todos os RF ligados a um caso de uso |
| Um só significado | Duas pessoas implementariam do mesmo jeito? | ✅ Após as revisões R01/R02 (Situação 1), "transição boa" e "sugestão" ganharam regra objetiva (RN08, RN11) |
| Modificável | Mudar o requisito afeta poucos lugares? | ✅ Limites centralizados em constantes (`TOLERANCIA_BPM`, `LIMITE_SUGESTOES`, `BPM_MIN/MAX`) |
| Atributos documentados | Tem prioridade, tipo e forma de verificação? | ✅ MoSCoW nos RF; "como verificar" nos RNF |
| Rastreável a código e teste | Dá para achar onde está implementado e testado? | ✅ Matriz da seção 3 |

## 2. Inspeção de código (checklist)

Inspeção feita no código da Situação 2 antes do teste com usuários.

| # | Item inspecionado | Resultado | Onde |
|---|-------------------|:---------:|------|
| 1 | Separação **MVC**: controllers não contêm regras de negócio; models não renderizam HTML | ✅ | `app/controllers/` chama `app/services/` |
| 2 | Regras de negócio isoladas e testáveis sem banco | ✅ | `app/services/harmonia.py` é "puro" |
| 3 | Toda entrada do usuário é validada no servidor (não só no navegador) | ✅ | `app/services/validacao.py` |
| 4 | Restrições também no banco (defesa em profundidade) | ✅ | `CheckConstraint`/`UniqueConstraint` nos models = script da Situação 1 |
| 5 | Senhas com hash; nunca registradas em log | ✅ | `Usuario.definir_senha` (Werkzeug) |
| 6 | Toda rota que acessa dados filtra pelo usuário logado | ✅ | funções `_*_do_usuario()` → 404 |
| 7 | Formulários com token CSRF; consultas parametrizadas (ORM) | ✅ | `csrf()` em todos os `<form method=post>` |
| 8 | Saída escapada (Jinja autoescape) e escape no JavaScript (`esc()`) | ✅ | Corrigido em D05 |
| 9 | Erros inesperados não mostram detalhes técnicos | ✅ | `_registrar_erros` em `app/__init__.py` |
| 10 | Mensagens dizem o que houve **e** como resolver | ✅ | Catálogo MSG01–MSG17 |
| 11 | Sem números "mágicos" espalhados | ✅ | Constantes nomeadas |
| 12 | Código e nomes em português, consistentes com o dicionário de dados | ✅ | Models = tabelas/colunas do dicionário |
| 13 | Nenhuma biblioteca externa carregada da internet no front-end | ✅ | SVG próprio (revisão R13) |

## 3. Matriz de rastreabilidade completa

| Requisito | Caso de uso | Implementação | Teste automatizado | Teste de sistema | Situação |
|-----------|:-----------:|---------------|--------------------|:----------------:|:--------:|
| RF01 Criar conta | UC01 | `controllers/auth.py::cadastro` | `test_auth.py::test_cadastro_*` | CTS-01 | ✅ |
| RF02 Login/logout | UC02 | `controllers/auth.py::login/logout` | `test_auth.py::test_login_*` | CTS-01 | ✅ |
| RF03 CRUD de faixas | UC03 | `controllers/faixas.py` | `test_faixas.py` | CTS-02, CTS-09 | ✅ |
| RF04 Busca e filtros | UC04 | `controllers/faixas.py::listar` | `test_listar_filtrar_e_ordenar` | CTS-03 | ✅ |
| RF05 CRUD de eventos | UC05 | `controllers/eventos.py` | `test_eventos_ajuda.py` | CTS-05 | ✅ |
| RF06 CRUD de setlists | UC06 | `controllers/setlists.py` | `test_setlists.py::test_criar_*`, `test_editar_*`, `test_excluir_*` | CTS-05 | ✅ |
| RF07 Adicionar faixa | UC07 | `services/setlist_service.py::adicionar_faixa` | `test_adicionar_faixas_e_ver_analise` | CTS-06 | ✅ |
| RF08 Remover/reordenar | UC08 | `setlist_service.py::remover_item/mover_item` | `test_remover_*`, `test_mover_*` | CTS-07 | ✅ |
| RF09 Sugestões | UC09 | `services/harmonia.py::sugerir_proximas` | `test_sugestoes_*` | CTS-06 | ✅ |
| RF10 Classificar transições | UC10 | `harmonia.py::classificar_transicao` | `test_transicao_*` | CTS-06, CTS-07 | ✅ |
| RF11 Pontuação harmônica | UC10 | `harmonia.py::analisar_setlist` | `test_analise_*` | CTS-06 | ✅ |
| RF12 Curva de energia | UC11 | `harmonia.py::curva_energia` + `static/js/app.js` | `test_curva_de_energia` | CTS-08 | ✅ |
| RF13 Duração e quantidade | UC11 | `harmonia.py::analisar_setlist` | `test_analise_*` | CTS-06 | ✅ |
| RF14 Ajuda Camelot | — | `controllers/ajuda.py` + `app.js` | `test_ajuda_camelot` | CTS-12 | ✅ |
| RF15 Painel | — | `controllers/painel.py` | `test_painel_*` | CTS-01 | ✅ |
| RF16 Importar CSV *(Could)* | UC12 | `services/csv_service.py::importar_faixas` | `test_importar_*` (incl. Rekordbox) | CTS-04 | ✅ |
| RF17 Exportar *(Could)* | UC13 | `csv_service.py::exportar_setlist` | `test_exportar_csv` | CTS-11 | ✅ |
| RN01 E-mail/senha | UC01 | `validacao.py::validar_usuario` | `test_senha_forte`, `test_cadastro_*` | CTS-01 | ✅ |
| RN02 BPM 60–200 | UC03 | `validacao.py` + `ck_faixa_bpm` | `test_validar_faixa_erros`, `test_banco_rejeita_*` | CTS-02 | ✅ |
| RN03 Tom Camelot | UC03 | `harmonia.py::tom_valido/normalizar_tom` | `test_tom_valido_*`, `test_normalizar_tom` | CTS-02 | ✅ |
| RN04 Energia/duração | UC03 | `validacao.py` + CHECKs | `test_validar_faixa_erros` | CTS-02 | ✅ |
| RN05 Faixa duplicada | UC03 | `faixas.py::_salvar` + UNIQUE | `test_faixa_duplicada_rn05` | — | ✅ |
| RN06 Compatibilidade de tom | UC10 | `harmonia.py::tipo_compatibilidade` | `test_tipo_compatibilidade` (11 casos) | CTS-06, CTS-12 | ✅ |
| RN07 BPM ±6% | UC10 | `harmonia.py::bpm_compativel` | `test_bpm_compativel_limite_de_6_por_cento` | CTS-07 | ✅ |
| RN08 Suave/Atenção/Arriscada | UC10 | `harmonia.py::Transicao` | `test_transicao_*` | CTS-06, CTS-07, CTS-11 | ✅ |
| RN09 Pontuação | UC10 | `harmonia.py::analisar_setlist` | `test_analise_*` | CTS-06 | ✅ |
| RN10 Sem repetição no set | UC07 | `setlist_service.py` + UNIQUE | `test_faixa_repetida_no_setlist_rn10` | — | ✅ |
| RN11 Regras da sugestão | UC09 | `harmonia.py::sugerir_proximas` | `test_sugestoes_filtram_e_ordenam` | CTS-06 | ✅ |
| RN12 Faixa em uso | UC03 | `faixas.py::excluir` + FK RESTRICT | `test_excluir_faixa_em_setlist_*`, `test_banco_impede_*` | CTS-10 | ✅ |
| RN13 Cascata do setlist | UC06 | `Setlist.itens` + FK CASCADE | `test_excluir_setlist_mantem_faixas_rn13` | — | ✅ |
| RN14 Excluir evento | UC05 | `eventos.py::excluir` + SET NULL | `test_excluir_evento_desvincula_*` | — | ✅ |
| RN15 Evento do mesmo usuário | UC06 | `setlists.py::_validar_vinculo_evento` | `test_nao_vincula_evento_de_outro_usuario_rn15` | — | ✅ |
| RNF01 Hash de senha | — | `models/usuario.py` | `test_senha_guardada_como_hash` | — | ✅ |
| RNF02 Isolamento | — | `_*_do_usuario()` | `test_usuario_nao_acessa_dados_de_outro` | CTS-14 | ✅ |
| RNF03 CSRF/SQLi/XSS | — | Flask-WTF, ORM, autoescape, `esc()` | `test_csrf_*`, `test_busca_com_aspas_*`, `test_textos_*_xss` | CTS-15 | ✅ |
| RNF04 Mensagens claras | — | Catálogo MSG01–MSG17 | vários (textos conferidos) | CTS-02 | ✅ + aceitação |
| RNF05 Responsivo (360 px) | — | `style.css` (media query) | — | CTS-13 | ✅ após D06/D07 |
| RNF06 Acessibilidade | — | rótulos, `aria-*`, ícone + texto | — | CTS-16 | ✅ |
| RNF07 Desempenho (≤ 1 s) | — | índices + consultas simples | — | ver seção 4 | ✅ |
| RNF08 MVC | — | estrutura de pastas | inspeção (seção 2) | — | ✅ |
| RNF09 Cobertura ≥ 80% | — | — | pytest-cov: **99%** | — | ✅ |
| RNF10 Banco configurável | — | `DATABASE_URL` / `TEST_DATABASE_URL` | suíte em SQLite **e** MariaDB | — | ✅ |
| RNF11 Erros amigáveis | — | `app/__init__.py::_registrar_erros` | `test_pagina_404_*`, `test_pagina_500_*` | CTS-14 | ✅ |

**Cobertura da matriz:** 17/17 RF, 15/15 RN e 11/11 RNF têm implementação identificada e pelo menos uma forma de
verificação.

## 4. Verificação de desempenho (RNF07)

Medição com uma biblioteca de **2.000 faixas** e um setlist de 30 faixas (SQLite, cliente de teste do Flask, mediana de
7 requisições), feita pelo script [`testes-sistema/medir_desempenho.py`](testes-sistema/medir_desempenho.py):

| Operação | Mediana | Pior caso | Meta |
|----------|:-------:|:---------:|:----:|
| Listar biblioteca (página 1) | 3,8 ms | 4,2 ms | ≤ 1.000 ms ✅ |
| Filtrar biblioteca (BPM 120–128 + busca) | 4,4 ms | 4,5 ms | ≤ 1.000 ms ✅ |
| Abrir o editor (análise + sugestões entre 1.970 candidatas) | 23,2 ms | 55,9 ms | ≤ 1.000 ms ✅ |
| Painel | 5,4 ms | 7,3 ms | ≤ 1.000 ms ✅ |

Saída completa em [`evidencias/desempenho.txt`](evidencias/desempenho.txt). Os tempos medem só o servidor; num servidor
publicado na internet soma-se o tempo de rede.
