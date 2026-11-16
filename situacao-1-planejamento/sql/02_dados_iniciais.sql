-- =====================================================================
--  HarmoniMix: Carga inicial de dados (domínios + dados de demonstração)
--  Executar depois de 01_schema_mysql.sql
--  As faixas de demonstração são FICTÍCIAS (títulos e artistas inventados).
-- =====================================================================
USE harmonimix;

-- ---------------------------------------------------------------------
-- Domínio: as 24 tonalidades da Roda de Camelot
-- A = modo menor · B = modo maior
-- ---------------------------------------------------------------------
INSERT INTO tom_camelot (codigo, numero, modo, nome_musical) VALUES
('1A',  1, 'A', 'Lá bemol menor (A♭m)'),
('1B',  1, 'B', 'Si maior (B)'),
('2A',  2, 'A', 'Mi bemol menor (E♭m)'),
('2B',  2, 'B', 'Fá sustenido maior (F♯)'),
('3A',  3, 'A', 'Si bemol menor (B♭m)'),
('3B',  3, 'B', 'Ré bemol maior (D♭)'),
('4A',  4, 'A', 'Fá menor (Fm)'),
('4B',  4, 'B', 'Lá bemol maior (A♭)'),
('5A',  5, 'A', 'Dó menor (Cm)'),
('5B',  5, 'B', 'Mi bemol maior (E♭)'),
('6A',  6, 'A', 'Sol menor (Gm)'),
('6B',  6, 'B', 'Si bemol maior (B♭)'),
('7A',  7, 'A', 'Ré menor (Dm)'),
('7B',  7, 'B', 'Fá maior (F)'),
('8A',  8, 'A', 'Lá menor (Am)'),
('8B',  8, 'B', 'Dó maior (C)'),
('9A',  9, 'A', 'Mi menor (Em)'),
('9B',  9, 'B', 'Sol maior (G)'),
('10A', 10, 'A', 'Si menor (Bm)'),
('10B', 10, 'B', 'Ré maior (D)'),
('11A', 11, 'A', 'Fá sustenido menor (F♯m)'),
('11B', 11, 'B', 'Lá maior (A)'),
('12A', 12, 'A', 'Ré bemol menor (D♭m)'),
('12B', 12, 'B', 'Mi maior (E)');

-- ---------------------------------------------------------------------
-- Domínio: gêneros musicais
-- ---------------------------------------------------------------------
INSERT INTO genero (nome) VALUES
('Afro House'), ('Deep House'), ('Downtempo'), ('Funk'), ('House'),
('Pop'), ('Tech House'), ('Techno'), ('Trance');

-- ---------------------------------------------------------------------
-- Usuário de demonstração
-- e-mail: demo@harmonimix.dev · senha: Demo1234  (hash PBKDF2-SHA256)
-- ---------------------------------------------------------------------
INSERT INTO usuario (nome, nome_artistico, email, senha_hash) VALUES
('Usuário Demonstração', 'DJ Demo', 'demo@harmonimix.dev',
 'pbkdf2:sha256:1000000$cmXRiSlriy72UFq8$83c89104b1fe0becacb4917b7aa383db3dddc975f77cbf3152b2b5206e2404a4');

SET @u := LAST_INSERT_ID();

-- ---------------------------------------------------------------------
-- Biblioteca de faixas (fictícias)
-- ---------------------------------------------------------------------
INSERT INTO faixa (id_usuario, titulo, artista, bpm, cod_tom, id_genero, energia, duracao_seg) VALUES
(@u, 'Aurora Boreal',          'Lumen Drift',  118.00, '8A',  (SELECT id_genero FROM genero WHERE nome='Deep House'), 4, 372),
(@u, 'Maré Alta',              'Coral Sound',  120.00, '9A',  (SELECT id_genero FROM genero WHERE nome='Deep House'), 5, 345),
(@u, 'Neon Copacabana',        'Rio Pulse',    122.00, '9B',  (SELECT id_genero FROM genero WHERE nome='House'),      6, 330),
(@u, 'Pôr do Sol em Ipanema',  'Lumen Drift',  122.00, '10B', (SELECT id_genero FROM genero WHERE nome='House'),      6, 360),
(@u, 'Batida Urbana',          'Kaleo Beats',  124.00, '10A', (SELECT id_genero FROM genero WHERE nome='Tech House'), 7, 318),
(@u, 'Concreto',               'Kaleo Beats',  125.00, '11A', (SELECT id_genero FROM genero WHERE nome='Tech House'), 7, 342),
(@u, 'Eletricidade',           'Volt Sisters', 126.00, '11B', (SELECT id_genero FROM genero WHERE nome='Techno'),     8, 390),
(@u, 'Horizonte Vertical',     'Volt Sisters', 128.00, '12B', (SELECT id_genero FROM genero WHERE nome='Techno'),     9, 405),
(@u, 'Ponto Final',            'Nébula 9',     128.00, '1B',  (SELECT id_genero FROM genero WHERE nome='Techno'),    10, 420),
(@u, 'Brisa',                  'Coral Sound',  100.00, '4A',  (SELECT id_genero FROM genero WHERE nome='Downtempo'),  3, 240),
(@u, 'Funk do Satélite',       'MC Órbita',    130.00, '5A',  (SELECT id_genero FROM genero WHERE nome='Funk'),       9, 180),
(@u, 'Samba Digital',          'Rio Pulse',    124.00, '3B',  (SELECT id_genero FROM genero WHERE nome='Afro House'), 7, 355),
(@u, 'Céu de Néon',            'Nébula 9',     140.00, '6A',  (SELECT id_genero FROM genero WHERE nome='Trance'),     8, 410),
(@u, 'Cidade Acesa',           'DJ Lumi',      123.00, '8B',  (SELECT id_genero FROM genero WHERE nome='House'),      6, 300),
(@u, 'Garoa Paulista',         'Coral Sound',  121.00, '7A',  (SELECT id_genero FROM genero WHERE nome='Deep House'), 5, 330),
(@u, 'Tambores da Serra',      'Rio Pulse',    120.00, '2A',  (SELECT id_genero FROM genero WHERE nome='Afro House'), 6, 365),
(@u, 'Segunda Chance',         'DJ Lumi',       95.00, '5B',  (SELECT id_genero FROM genero WHERE nome='Pop'),        5, 210),
(@u, 'Madrugada',              'Lumen Drift',  126.00, '12A', (SELECT id_genero FROM genero WHERE nome='Techno'),     8, 380);

-- ---------------------------------------------------------------------
-- Evento e setlists de demonstração
-- ---------------------------------------------------------------------
INSERT INTO evento (id_usuario, nome, data_evento, local) VALUES
(@u, 'Formatura Engenharia 2026', '2026-12-12', 'Espaço Villa Verde');
SET @ev := LAST_INSERT_ID();

-- Setlist 1: progressão harmônica perfeita (todas as transições suaves)
INSERT INTO setlist (id_usuario, id_evento, nome, descricao) VALUES
(@u, @ev, 'Warm-up até o pico', 'Começa no Deep House e sobe gradualmente até o Techno.');
SET @s1 := LAST_INSERT_ID();

INSERT INTO item_setlist (id_setlist, posicao, id_faixa)
SELECT @s1, ROW_NUMBER() OVER (ORDER BY FIELD(titulo,
        'Aurora Boreal','Maré Alta','Neon Copacabana','Pôr do Sol em Ipanema',
        'Batida Urbana','Concreto','Eletricidade','Horizonte Vertical','Ponto Final')),
       id_faixa
FROM   faixa
WHERE  id_usuario = @u
  AND  titulo IN ('Aurora Boreal','Maré Alta','Neon Copacabana','Pôr do Sol em Ipanema',
                  'Batida Urbana','Concreto','Eletricidade','Horizonte Vertical','Ponto Final');

-- Setlist 2: exemplo com transições problemáticas (para demonstrar os alertas)
INSERT INTO setlist (id_usuario, id_evento, nome, descricao) VALUES
(@u, NULL, 'Rascunho: precisa revisar', 'Exemplo com transições de Atenção e Arriscadas.');
SET @s2 := LAST_INSERT_ID();

INSERT INTO item_setlist (id_setlist, posicao, id_faixa)
SELECT @s2, ROW_NUMBER() OVER (ORDER BY FIELD(titulo,
        'Garoa Paulista','Aurora Boreal','Funk do Satélite','Céu de Néon','Maré Alta')),
       id_faixa
FROM   faixa
WHERE  id_usuario = @u
  AND  titulo IN ('Garoa Paulista','Aurora Boreal','Funk do Satélite','Céu de Néon','Maré Alta');
