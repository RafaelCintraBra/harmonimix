# 2. Especificação de Requisitos: HarmoniMix

> Documento de Planejamento: versão 2.0. Prioridades no método **MoSCoW**:
> **M** = *Must* (obrigatório) · **S** = *Should* (importante) · **C** = *Could* (desejável).

---

## 2.1 Requisitos Funcionais (RF)

| ID | Requisito | Prioridade | Caso de uso |
|----|-----------|:----------:|:-----------:|
| RF01 | O sistema deve permitir que um visitante **crie uma conta** informando nome, nome artístico (opcional), e-mail e senha. | M | UC01 |
| RF02 | O sistema deve permitir que o usuário **faça login e logout**. | M | UC02 |
| RF03 | O sistema deve permitir **cadastrar, listar, editar e excluir faixas** (título, artista, BPM, tom Camelot, gênero, energia e duração). | M | UC03 |
| RF04 | O sistema deve permitir **buscar faixas** por título/artista e **filtrar** por gênero, tom e faixa de BPM. | M | UC04 |
| RF05 | O sistema deve permitir **cadastrar, listar, editar e excluir eventos** (nome, data e local). | S | UC05 |
| RF06 | O sistema deve permitir **criar, listar, renomear e excluir setlists**, com vínculo opcional a um evento. | M | UC06 |
| RF07 | O sistema deve permitir **adicionar uma faixa ao final** de um setlist. | M | UC07 |
| RF08 | O sistema deve permitir **remover** uma faixa e **reordenar** (subir/descer) as faixas do setlist. | M | UC08 |
| RF09 | O sistema deve **sugerir as próximas faixas compatíveis** com a última faixa do setlist, ordenadas por grau de compatibilidade. | M | UC09 |
| RF10 | O sistema deve **classificar cada transição** do setlist como *Suave*, *Atenção* ou *Arriscada* e explicar o motivo. | M | UC10 |
| RF11 | O sistema deve calcular a **pontuação harmônica** do setlist (percentual de transições suaves). | S | UC10 |
| RF12 | O sistema deve exibir a **curva de energia** do setlist (gráfico de BPM e energia por posição). | M | UC11 |
| RF13 | O sistema deve exibir a **duração total** e a **quantidade de faixas** do setlist. | M | UC11 |
| RF14 | O sistema deve exibir uma **página de ajuda** com a Roda de Camelot e as regras de compatibilidade. | S | — |
| RF15 | O sistema deve exibir um **painel inicial** com totais (faixas, setlists, próximos eventos). | S | — |
| RF16 | O sistema deve permitir **importar faixas** de um arquivo CSV. | C | UC12 |
| RF17 | O sistema deve permitir **exportar** um setlist em CSV. | C | UC13 |

## 2.2 Requisitos Não Funcionais (RNF)

| ID | Categoria | Requisito | Como verificar |
|----|-----------|-----------|----------------|
| RNF01 | **Segurança** | Senhas armazenadas apenas como *hash* (PBKDF2/scrypt via Werkzeug), nunca em texto puro. | Inspeção do banco + teste unitário |
| RNF02 | **Segurança** | Cada usuário só pode ver e alterar **os próprios dados** (faixas, eventos, setlists). | Teste de integração (acesso a ID de outro usuário → 404) |
| RNF03 | **Segurança** | Formulários protegidos contra CSRF e consultas protegidas contra SQL Injection (ORM com parâmetros). | Teste de integração |
| RNF04 | **Usabilidade** | Interface em português, com mensagens de erro claras que indiquem **o que** está errado e **como** corrigir. | Teste com usuários (Situação 3) |
| RNF05 | **Usabilidade** | Interface **responsiva**, utilizável em telas a partir de 360 px de largura. | Teste manual em celular/DevTools |
| RNF06 | **Acessibilidade** | Cores de status sempre acompanhadas de **ícone e texto** (não depender só da cor); contraste mínimo WCAG AA. | Inspeção |
| RNF07 | **Desempenho** | Listagens e sugestões respondem em **até 1 s** para bibliotecas de até 2.000 faixas. | Teste de carga simples |
| RNF08 | **Manutenibilidade** | Código organizado em **MVC** (models, views/templates, controllers) + camada de serviços para regras de negócio. | Revisão de código |
| RNF09 | **Testabilidade** | Regras de negócio com **cobertura de testes ≥ 80%** (pytest-cov). | Relatório de cobertura |
| RNF10 | **Portabilidade** | Banco configurável por variável de ambiente (MySQL em produção, SQLite em testes). | Execução dos testes |
| RNF11 | **Confiabilidade** | Erros inesperados exibem página amigável (404/500), sem expor detalhes técnicos. | Teste de integração |

## 2.3 Regras de Negócio (RN)

| ID | Regra |
|----|-------|
| RN01 | O **e-mail** é único no sistema e deve ter formato válido. A **senha** deve ter no mínimo 8 caracteres, com pelo menos uma letra e um número. |
| RN02 | O **BPM** de uma faixa deve estar entre **60 e 200** (até duas casas decimais). |
| RN03 | O **tom** deve ser um código válido da Roda de Camelot: número de **1 a 12** + letra **A** (menor) ou **B** (maior). |
| RN04 | A **energia** da faixa é um inteiro de **1 a 10**. A **duração** deve estar entre **30 segundos e 30 minutos**. |
| RN05 | Um mesmo usuário não pode cadastrar duas faixas com o mesmo **título + artista**. |
| RN06 | **Compatibilidade de tom.** Duas faixas são harmonicamente compatíveis quando: (a) têm o **mesmo código** (ex.: 8A → 8A); (b) têm a **mesma letra e números vizinhos** na roda, considerando que 12 é vizinho de 1 (ex.: 8A → 7A ou 9A; 12B → 1B); ou (c) têm o **mesmo número e letras diferentes**, ou seja, a tonalidade relativa (ex.: 8A ↔ 8B). |
| RN07 | **Compatibilidade de BPM.** A variação de BPM entre faixas consecutivas é aceitável quando for de **no máximo 6%**, calculada como `|BPM₂ − BPM₁| ÷ BPM₁ × 100`. |
| RN08 | **Classificação da transição:** 🟢 **Suave** = tom compatível **e** BPM ≤ 6% · 🟡 **Atenção** = apenas um dos critérios atendido · 🔴 **Arriscada** = nenhum critério atendido. |
| RN09 | **Pontuação harmônica** do setlist = (nº de transições suaves ÷ nº total de transições) × 100. Setlists com menos de 2 faixas não têm pontuação. |
| RN10 | Uma faixa **não pode se repetir** no mesmo setlist. |
| RN11 | A **sugestão** considera apenas faixas do próprio usuário que ainda não estão no setlist e que tenham tom compatível **e** BPM ≤ 6%. A ordem é: mesmo tom → vizinho → relativo; depois, menor diferença de BPM. São exibidas no máximo **10** sugestões. |
| RN12 | Uma faixa que está em algum setlist **não pode ser excluída**; o sistema informa em quais setlists ela está. |
| RN13 | Ao excluir um **setlist**, os seus itens são excluídos junto; as faixas continuam na biblioteca. |
| RN14 | Ao excluir um **evento**, os setlists vinculados a ele **não são excluídos**, apenas desvinculados. |
| RN15 | Um setlist só pode ser vinculado a um evento **do mesmo usuário**. |

## 2.4 Matriz de rastreabilidade (Requisito → Caso de uso → Teste)

Esta matriz liga cada requisito ao caso de uso e ao teste automatizado que vai verificá-lo na Situação 2/3.

| Requisito / Regra | Caso de uso | Teste previsto (pytest) |
|-------------------|-------------|-------------------------|
| RF01, RN01 | UC01 | `test_auth.py::test_cadastro_*` |
| RF02, RNF01 | UC02 | `test_auth.py::test_login_*`, `test_senha_hash` |
| RF03, RN02–RN05 | UC03 | `test_faixas.py`, `test_validacao.py` |
| RF04 | UC04 | `test_faixas.py::test_filtro_*` |
| RF05, RN14 | UC05 | `test_eventos.py` |
| RF06, RN13, RN15 | UC06 | `test_setlists.py` |
| RF07, RF08, RN10 | UC07, UC08 | `test_setlists.py::test_adicionar_*`, `test_reordenar_*` |
| RF09, RN11 | UC09 | `test_harmonia.py::test_sugestao_*` |
| RF10, RF11, RN06–RN09 | UC10 | `test_harmonia.py::test_tom_*`, `test_bpm_*`, `test_classificacao_*` |
| RF12, RF13 | UC11 | `test_setlists.py::test_curva_energia` |
| RN12 | UC03 | `test_faixas.py::test_excluir_faixa_em_setlist` |
| RNF02 | Todos | `test_seguranca.py::test_isolamento_usuarios` |
