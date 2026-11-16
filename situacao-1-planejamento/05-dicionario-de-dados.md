# 5. Dicionário de Dados: HarmoniMix

> SGBD: **MySQL 8** · Banco: `harmonimix` · Charset: `utf8mb4_unicode_ci` · Versão do modelo: 2.0
>
> **Legenda:** PK = chave primária · FK = chave estrangeira · UK = único · NN = obrigatório (NOT NULL) · AI = auto incremento

---

## Tabela `usuario`
**Descrição:** DJ cadastrado no sistema. É o "dono" de faixas, eventos e setlists.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_usuario | INT UNSIGNED | PK | ✔ | AI | ≥ 1 | Identificador do usuário |
| nome | VARCHAR(100) | | ✔ | | mín. 2 caracteres | Nome completo |
| nome_artistico | VARCHAR(60) | | | NULL | | Nome usado nas apresentações (ex.: "DJ Lumi") |
| email | VARCHAR(120) | UK | ✔ | | formato `x@y.z`, único (RN01) | Login do usuário |
| senha_hash | VARCHAR(255) | | ✔ | | hash PBKDF2-SHA256 (RNF01) | Senha criptografada, nunca a senha em texto |
| criado_em | DATETIME | | ✔ | CURRENT_TIMESTAMP | | Data/hora do cadastro |

---

## Tabela `tom_camelot`
**Descrição:** tabela de domínio com as **24 tonalidades** da Roda de Camelot. Carga fixa (não é editada pelo usuário).

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| codigo | VARCHAR(3) | PK | ✔ | | {1A … 12B} | Código Camelot |
| numero | TINYINT | UK¹ | ✔ | | 1 a 12 | Posição na roda (1–12) |
| modo | CHAR(1) | UK¹ | ✔ | | {A, B} | A = menor · B = maior |
| nome_musical | VARCHAR(30) | | ✔ | | | Nome tradicional (ex.: "Lá menor (Am)") |

¹ `UNIQUE (numero, modo)`: cada combinação existe uma única vez.

---

## Tabela `genero`
**Descrição:** tabela de domínio com os gêneros musicais.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_genero | SMALLINT UNSIGNED | PK | ✔ | AI | ≥ 1 | Identificador do gênero |
| nome | VARCHAR(50) | UK | ✔ | | único | Nome do gênero (ex.: "Tech House") |

---

## Tabela `faixa`
**Descrição:** música da biblioteca de um DJ, com os metadados usados na mixagem harmônica.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_faixa | INT UNSIGNED | PK | ✔ | AI | ≥ 1 | Identificador da faixa |
| id_usuario | INT UNSIGNED | FK, UK² | ✔ | | → usuario (CASCADE) | Dono da faixa |
| cod_tom | VARCHAR(3) | FK | ✔ | | → tom_camelot (RESTRICT) · RN03 | Tom da faixa na Roda de Camelot |
| id_genero | SMALLINT UNSIGNED | FK | | NULL | → genero (SET NULL) | Gênero musical |
| titulo | VARCHAR(150) | UK² | ✔ | | 1–150 caracteres | Título da música |
| artista | VARCHAR(120) | UK² | ✔ | | 1–120 caracteres | Artista/produtor |
| bpm | DECIMAL(5,2) | | ✔ | | 60,00 a 200,00 (RN02) | Batidas por minuto |
| energia | TINYINT UNSIGNED | | ✔ | 5 | 1 a 10 (RN04) | Nível de energia percebido (1 = calma, 10 = pico) |
| duracao_seg | SMALLINT UNSIGNED | | ✔ | | 30 a 1800 (RN04) | Duração em segundos (exibida como mm:ss) |
| criado_em | DATETIME | | ✔ | CURRENT_TIMESTAMP | | Data/hora do cadastro |

² `UNIQUE (id_usuario, titulo, artista)`: o mesmo DJ não pode cadastrar a mesma música duas vezes (RN05).
**Índices:** `ix_faixa_usuario_bpm (id_usuario, bpm)` e `ix_faixa_usuario_tom (id_usuario, cod_tom)`.

---

## Tabela `evento`
**Descrição:** apresentação (festa, casamento, formatura…) para a qual o DJ prepara setlists.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_evento | INT UNSIGNED | PK | ✔ | AI | ≥ 1 | Identificador do evento |
| id_usuario | INT UNSIGNED | FK | ✔ | | → usuario (CASCADE) | DJ responsável |
| nome | VARCHAR(120) | | ✔ | | 1–120 caracteres | Nome do evento |
| data_evento | DATE | | ✔ | | data válida | Data da apresentação |
| local | VARCHAR(120) | | | NULL | | Local do evento |
| criado_em | DATETIME | | ✔ | CURRENT_TIMESTAMP | | Data/hora do cadastro |

**Índice:** `ix_evento_usuario_data (id_usuario, data_evento)`, usado para listar os próximos eventos.

---

## Tabela `setlist`
**Descrição:** sequência planejada de faixas, opcionalmente vinculada a um evento.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_setlist | INT UNSIGNED | PK | ✔ | AI | ≥ 1 | Identificador do setlist |
| id_usuario | INT UNSIGNED | FK | ✔ | | → usuario (CASCADE) | DJ que criou o setlist |
| id_evento | INT UNSIGNED | FK | | NULL | → evento (SET NULL) · RN14, RN15 | Evento vinculado (opcional) |
| nome | VARCHAR(100) | | ✔ | | 1–100 caracteres | Nome do setlist |
| descricao | VARCHAR(500) | | | NULL | | Observações do DJ |
| criado_em | DATETIME | | ✔ | CURRENT_TIMESTAMP | | Data/hora de criação |
| atualizado_em | DATETIME | | ✔ | CURRENT_TIMESTAMP | atualiza automaticamente | Data/hora da última alteração |

---

## Tabela `item_setlist`
**Descrição:** entidade associativa que resolve o N:N entre **setlist** e **faixa** e guarda a **ordem** das faixas.

| Coluna | Tipo | Chave | NN | Padrão | Domínio / Regra | Descrição |
|--------|------|:-----:|:--:|--------|-----------------|-----------|
| id_setlist | INT UNSIGNED | PK, FK, UK³ | ✔ | | → setlist (CASCADE) · RN13 | Setlist ao qual o item pertence |
| posicao | SMALLINT UNSIGNED | PK | ✔ | | ≥ 1 | Ordem da faixa no set (1 = primeira) |
| id_faixa | INT UNSIGNED | FK, UK³ | ✔ | | → faixa (RESTRICT) · RN12 | Faixa tocada nesta posição |

³ `UNIQUE (id_setlist, id_faixa)`: uma faixa não se repete no mesmo setlist (RN10).
**Índice:** `ix_item_faixa (id_faixa)`, usado para descobrir em quais setlists uma faixa está.

---

## Visão `vw_setlist_resumo`
**Descrição:** totais por setlist, usados no painel e na listagem de setlists.

| Coluna | Origem | Descrição |
|--------|--------|-----------|
| id_setlist | setlist.id_setlist | Identificador |
| id_usuario | setlist.id_usuario | Dono (para filtrar por usuário) |
| setlist | setlist.nome | Nome do setlist |
| evento | evento.nome | Nome do evento (ou NULL) |
| qtd_faixas | COUNT(item_setlist) | Número de faixas |
| duracao_total_seg | SUM(faixa.duracao_seg) | Duração total em segundos |
| bpm_medio | AVG(faixa.bpm) | BPM médio do set |

---

## Resumo do modelo

| Tabela | Tipo | Registros iniciais | Cresce com o uso? |
|--------|------|:------------------:|:-----------------:|
| usuario | Cadastro | 1 (demo) | ✔ |
| tom_camelot | Domínio | 24 | ✘ |
| genero | Domínio | 9 | raramente |
| faixa | Cadastro | 18 (demo) | ✔ |
| evento | Cadastro | 1 (demo) | ✔ |
| setlist | Cadastro | 2 (demo) | ✔ |
| item_setlist | Associativa | 14 (demo) | ✔ |
