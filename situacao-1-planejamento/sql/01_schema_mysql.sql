-- =====================================================================
--  HarmoniMix: Projeto Físico do Banco de Dados
--  SGBD: MySQL 8.0+ (compatível com MariaDB 10.5+)
--  Charset: utf8mb4 (suporta acentos e emojis)
--  Versão do modelo: 2.0
-- =====================================================================

DROP DATABASE IF EXISTS harmonimix;
CREATE DATABASE harmonimix
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE harmonimix;

-- ---------------------------------------------------------------------
-- Tabela: usuario
-- DJ que utiliza o sistema. Dono de faixas, eventos e setlists.
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id_usuario      INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    nome            VARCHAR(100)    NOT NULL,
    nome_artistico  VARCHAR(60)     NULL,
    email           VARCHAR(120)    NOT NULL,
    senha_hash      VARCHAR(255)    NOT NULL,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_usuario        PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuario_email  UNIQUE (email),
    CONSTRAINT ck_usuario_nome   CHECK (CHAR_LENGTH(TRIM(nome)) >= 2),
    CONSTRAINT ck_usuario_email  CHECK (email LIKE '_%@_%._%')
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela: tom_camelot
-- Tabela de domínio com as 24 tonalidades da Roda de Camelot.
-- ---------------------------------------------------------------------
CREATE TABLE tom_camelot (
    codigo          VARCHAR(3)      NOT NULL,   -- '1A' .. '12B'
    numero          TINYINT         NOT NULL,   -- 1 .. 12 (SIGNED: permite subtração entre tons)
    modo            CHAR(1)         NOT NULL,   -- 'A' = menor, 'B' = maior
    nome_musical    VARCHAR(30)     NOT NULL,   -- ex.: 'Lá menor (Am)'
    CONSTRAINT pk_tom_camelot         PRIMARY KEY (codigo),
    CONSTRAINT uq_tom_numero_modo     UNIQUE (numero, modo),
    CONSTRAINT ck_tom_numero          CHECK (numero BETWEEN 1 AND 12),
    CONSTRAINT ck_tom_modo            CHECK (modo IN ('A', 'B'))
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela: genero
-- Tabela de domínio com os gêneros musicais.
-- ---------------------------------------------------------------------
CREATE TABLE genero (
    id_genero       SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome            VARCHAR(50)     NOT NULL,
    CONSTRAINT pk_genero       PRIMARY KEY (id_genero),
    CONSTRAINT uq_genero_nome  UNIQUE (nome)
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela: faixa
-- Música da biblioteca de um DJ.
-- ---------------------------------------------------------------------
CREATE TABLE faixa (
    id_faixa        INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_usuario      INT UNSIGNED    NOT NULL,
    cod_tom         VARCHAR(3)      NOT NULL,
    id_genero       SMALLINT UNSIGNED NULL,
    titulo          VARCHAR(150)    NOT NULL,
    artista         VARCHAR(120)    NOT NULL,
    bpm             DECIMAL(5,2)    NOT NULL,
    energia         TINYINT UNSIGNED NOT NULL DEFAULT 5,
    duracao_seg     SMALLINT UNSIGNED NOT NULL,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_faixa             PRIMARY KEY (id_faixa),
    CONSTRAINT fk_faixa_usuario     FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_faixa_tom         FOREIGN KEY (cod_tom)
        REFERENCES tom_camelot (codigo) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_faixa_genero      FOREIGN KEY (id_genero)
        REFERENCES genero (id_genero) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT uq_faixa_usuario_titulo_artista UNIQUE (id_usuario, titulo, artista),  -- RN05
    CONSTRAINT ck_faixa_bpm         CHECK (bpm BETWEEN 60 AND 200),                   -- RN02
    CONSTRAINT ck_faixa_energia     CHECK (energia BETWEEN 1 AND 10),                 -- RN04
    CONSTRAINT ck_faixa_duracao     CHECK (duracao_seg BETWEEN 30 AND 1800)           -- RN04
) ENGINE = InnoDB;

CREATE INDEX ix_faixa_usuario_bpm ON faixa (id_usuario, bpm);      -- filtros e sugestões
CREATE INDEX ix_faixa_usuario_tom ON faixa (id_usuario, cod_tom);  -- sugestões por tom

-- ---------------------------------------------------------------------
-- Tabela: evento
-- Apresentação/ocasião para a qual um ou mais setlists são preparados.
-- ---------------------------------------------------------------------
CREATE TABLE evento (
    id_evento       INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_usuario      INT UNSIGNED    NOT NULL,
    nome            VARCHAR(120)    NOT NULL,
    data_evento     DATE            NOT NULL,
    local           VARCHAR(120)    NULL,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_evento          PRIMARY KEY (id_evento),
    CONSTRAINT fk_evento_usuario  FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE INDEX ix_evento_usuario_data ON evento (id_usuario, data_evento);

-- ---------------------------------------------------------------------
-- Tabela: setlist
-- Sequência planejada de faixas.
-- ---------------------------------------------------------------------
CREATE TABLE setlist (
    id_setlist      INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    id_usuario      INT UNSIGNED    NOT NULL,
    id_evento       INT UNSIGNED    NULL,
    nome            VARCHAR(100)    NOT NULL,
    descricao       VARCHAR(500)    NULL,
    criado_em       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                    ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT pk_setlist          PRIMARY KEY (id_setlist),
    CONSTRAINT fk_setlist_usuario  FOREIGN KEY (id_usuario)
        REFERENCES usuario (id_usuario) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_setlist_evento   FOREIGN KEY (id_evento)
        REFERENCES evento (id_evento) ON DELETE SET NULL ON UPDATE CASCADE      -- RN14
) ENGINE = InnoDB;

-- ---------------------------------------------------------------------
-- Tabela: item_setlist
-- Entidade associativa Setlist N:N Faixa, com a posição da faixa no set.
-- ---------------------------------------------------------------------
CREATE TABLE item_setlist (
    id_setlist      INT UNSIGNED    NOT NULL,
    posicao         SMALLINT UNSIGNED NOT NULL,
    id_faixa        INT UNSIGNED    NOT NULL,
    CONSTRAINT pk_item_setlist        PRIMARY KEY (id_setlist, posicao),
    CONSTRAINT uq_item_setlist_faixa  UNIQUE (id_setlist, id_faixa),                -- RN10
    CONSTRAINT fk_item_setlist        FOREIGN KEY (id_setlist)
        REFERENCES setlist (id_setlist) ON DELETE CASCADE ON UPDATE CASCADE,       -- RN13
    CONSTRAINT fk_item_faixa          FOREIGN KEY (id_faixa)
        REFERENCES faixa (id_faixa) ON DELETE RESTRICT ON UPDATE CASCADE,          -- RN12
    CONSTRAINT ck_item_posicao        CHECK (posicao >= 1)
) ENGINE = InnoDB;

CREATE INDEX ix_item_faixa ON item_setlist (id_faixa);

-- ---------------------------------------------------------------------
-- Visão: vw_setlist_resumo
-- Totais por setlist (nº de faixas, duração, BPM médio).
-- ---------------------------------------------------------------------
CREATE VIEW vw_setlist_resumo AS
SELECT  s.id_setlist,
        s.id_usuario,
        s.nome                         AS setlist,
        e.nome                         AS evento,
        COUNT(i.id_faixa)              AS qtd_faixas,
        COALESCE(SUM(f.duracao_seg),0) AS duracao_total_seg,
        ROUND(AVG(f.bpm), 1)           AS bpm_medio
FROM        setlist s
LEFT JOIN   evento e        ON e.id_evento  = s.id_evento
LEFT JOIN   item_setlist i  ON i.id_setlist = s.id_setlist
LEFT JOIN   faixa f         ON f.id_faixa   = i.id_faixa
GROUP BY    s.id_setlist, s.id_usuario, s.nome, e.nome;
