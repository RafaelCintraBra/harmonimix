-- =====================================================================
--  HarmoniMix: Consultas de exemplo (validação do modelo)
--  Executar depois de 01_schema_mysql.sql e 02_dados_iniciais.sql
-- =====================================================================
USE harmonimix;

-- 1) Resumo dos setlists (usa a visão vw_setlist_resumo)
SELECT * FROM vw_setlist_resumo;

-- 2) Setlist em ordem, com tom, BPM e nome musical
SELECT  i.posicao, f.titulo, f.artista, f.cod_tom, t.nome_musical, f.bpm, f.energia
FROM    item_setlist i
JOIN    faixa f       ON f.id_faixa = i.id_faixa
JOIN    tom_camelot t ON t.codigo   = f.cod_tom
WHERE   i.id_setlist = 1
ORDER BY i.posicao;

-- 3) Transições do setlist: tom compatível? variação de BPM?
--    (a mesma regra RN06/RN07 será implementada em Python no HarmoniaService)
SELECT  a.posicao                         AS de_pos,
        fa.titulo                         AS de_faixa,
        fa.cod_tom                        AS de_tom,
        fb.titulo                         AS para_faixa,
        fb.cod_tom                        AS para_tom,
        ROUND(ABS(fb.bpm - fa.bpm) / fa.bpm * 100, 2) AS variacao_bpm_pct,
        CASE
            WHEN ta.codigo = tb.codigo THEN 'mesmo tom'
            WHEN ta.modo = tb.modo AND (ABS(ta.numero - tb.numero) = 1
                                        OR ABS(ta.numero - tb.numero) = 11) THEN 'vizinho'
            WHEN ta.numero = tb.numero THEN 'relativo'
            ELSE 'incompatível'
        END AS compat_tom
FROM    item_setlist a
JOIN    item_setlist b  ON b.id_setlist = a.id_setlist AND b.posicao = a.posicao + 1
JOIN    faixa fa        ON fa.id_faixa = a.id_faixa
JOIN    faixa fb        ON fb.id_faixa = b.id_faixa
JOIN    tom_camelot ta  ON ta.codigo = fa.cod_tom
JOIN    tom_camelot tb  ON tb.codigo = fb.cod_tom
WHERE   a.id_setlist = 2
ORDER BY a.posicao;

-- 4) Sugestões para depois de 'Maré Alta' (9A, 120 BPM), a última faixa do setlist 2,
--    considerando apenas faixas que ainda não estão no setlist 2
SELECT  f.titulo, f.cod_tom, f.bpm,
        ROUND(ABS(f.bpm - ref.bpm) / ref.bpm * 100, 2) AS variacao_bpm_pct
FROM    faixa f
JOIN    tom_camelot t   ON t.codigo = f.cod_tom
JOIN    (SELECT fx.id_faixa, fx.id_usuario, fx.bpm, tc.numero, tc.modo, tc.codigo
         FROM faixa fx JOIN tom_camelot tc ON tc.codigo = fx.cod_tom
         WHERE fx.titulo = 'Maré Alta') ref ON ref.id_usuario = f.id_usuario
WHERE   f.id_faixa <> ref.id_faixa
  AND   f.id_faixa NOT IN (SELECT id_faixa FROM item_setlist WHERE id_setlist = 2)
  AND   (t.codigo = ref.codigo
         OR (t.modo = ref.modo AND ABS(t.numero - ref.numero) IN (1, 11))
         OR (t.numero = ref.numero))
  AND   ABS(f.bpm - ref.bpm) / ref.bpm * 100 <= 6
ORDER BY variacao_bpm_pct;

-- 5) Em quais setlists uma faixa está (usado para bloquear a exclusão, RN12)
SELECT s.nome
FROM   item_setlist i JOIN setlist s ON s.id_setlist = i.id_setlist
WHERE  i.id_faixa = (SELECT id_faixa FROM faixa WHERE titulo = 'Maré Alta');

-- =====================================================================
--  Testes de restrições: cada comando abaixo DEVE FALHAR.
--  Descomente um por vez para verificar.
-- =====================================================================
-- RN02: BPM fora do intervalo
-- INSERT INTO faixa (id_usuario, titulo, artista, bpm, cod_tom, energia, duracao_seg)
-- VALUES (1, 'Teste', 'X', 250, '8A', 5, 300);

-- RN03: tom inexistente (FK para tom_camelot)
-- INSERT INTO faixa (id_usuario, titulo, artista, bpm, cod_tom, energia, duracao_seg)
-- VALUES (1, 'Teste', 'X', 120, '13C', 5, 300);

-- RN05: faixa duplicada (mesmo título + artista para o mesmo usuário)
-- INSERT INTO faixa (id_usuario, titulo, artista, bpm, cod_tom, energia, duracao_seg)
-- VALUES (1, 'Aurora Boreal', 'Lumen Drift', 118, '8A', 5, 300);

-- RN10: mesma faixa duas vezes no setlist
-- INSERT INTO item_setlist (id_setlist, posicao, id_faixa) VALUES (1, 99, 1);

-- RN12: excluir faixa que está em um setlist
-- DELETE FROM faixa WHERE titulo = 'Maré Alta';
