"""Testes UNITÁRIOS do HarmoniaService (RN06 a RN11): não usam banco nem Flask."""
import pytest

from app.services import harmonia as h
from tests.conftest import faixa_fake as F


# ---------------------------------------------------------------- RN03: tom válido
@pytest.mark.parametrize("codigo", ["1A", "1B", "8A", "9B", "10A", "12B", " 8a "])
def test_tom_valido_aceita_codigos_da_roda(codigo):
    assert h.tom_valido(codigo)


@pytest.mark.parametrize("codigo", ["", None, "0A", "13A", "8C", "A8", "8", "8AB", "-1A", "08A"])
def test_tom_valido_rejeita_codigos_invalidos(codigo):
    assert not h.tom_valido(codigo)


# ---------------------------------------------------------------- conversão de formatos de tom
@pytest.mark.parametrize("texto,camelot", [
    ("8A", "8A"), (" 12b ", "12B"),
    # notação musical (Rekordbox "Classic", Serato, iTunes)
    ("Am", "8A"), ("C", "8B"), ("F#m", "11A"), ("Gbm", "11A"), ("Dbm", "12A"), ("C#m", "12A"),
    ("Abm", "1A"), ("G#m", "1A"), ("B", "1B"), ("Bm", "10A"), ("Bbm", "3A"), ("Bb", "6B"),
    ("Eb", "5B"), ("Ebm", "2A"), ("E", "12B"), ("Db", "3B"), ("F", "7B"), ("Fm", "4A"),
    ("A♭m", "1A"), ("F♯", "2B"), ("A minor", "8A"), ("Amin", "8A"), ("C major", "8B"), ("Cmaj", "8B"),
    # Open Key (Traktor)
    ("1d", "8B"), ("1m", "8A"), ("6d", "1B"), ("12m", "7A"), ("5M", "12A"),
])
def test_normalizar_tom(texto, camelot):
    assert h.normalizar_tom(texto) == camelot


@pytest.mark.parametrize("texto", [None, "", "H", "13A", "X#m", "Am7", "tom"])
def test_normalizar_tom_invalido(texto):
    assert h.normalizar_tom(texto) is None


def test_todas_as_24_tonalidades_musicais_cobrem_a_roda():
    notas = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    convertidos = {h.normalizar_tom(n) for n in notas} | {h.normalizar_tom(n + "m") for n in notas}
    assert convertidos == {f"{n}{m}" for n in range(1, 13) for m in "AB"}


def test_decompor_tom():
    assert h.decompor_tom("12b") == (12, "B")
    with pytest.raises(ValueError):
        h.decompor_tom("13A")


@pytest.mark.parametrize("a,b,esperado", [(1, 12, 1), (12, 1, 1), (3, 9, 6), (5, 5, 0), (2, 11, 3)])
def test_distancia_circular(a, b, esperado):
    assert h.distancia_circular(a, b) == esperado


# ---------------------------------------------------------------- RN06: compatibilidade de tom
@pytest.mark.parametrize("t1,t2,tipo", [
    ("8A", "8A", h.MESMO_TOM),
    ("8A", "9A", h.VIZINHO),
    ("8A", "7A", h.VIZINHO),
    ("12B", "1B", h.VIZINHO),      # a roda é circular
    ("1A", "12A", h.VIZINHO),
    ("8A", "8B", h.RELATIVO),
    ("8B", "8A", h.RELATIVO),
    ("8A", "9B", None),            # diagonal não é compatível
    ("8A", "10A", None),           # dois degraus
    ("8A", "2A", None),
    ("6A", "9A", None),
])
def test_tipo_compatibilidade(t1, t2, tipo):
    assert h.tipo_compatibilidade(t1, t2) == tipo
    assert h.tons_compativeis(t1, t2) is (tipo is not None)


def test_tons_compativeis_com_inclui_vizinhos_circulares():
    assert h.tons_compativeis_com("8A") == ["8A", "7A", "9A", "8B"]
    assert h.tons_compativeis_com("1B") == ["1B", "12B", "2B", "1A"]
    assert h.tons_compativeis_com("12A") == ["12A", "11A", "1A", "12B"]


# ---------------------------------------------------------------- RN07: BPM
def test_variacao_bpm_com_sinal():
    assert h.variacao_bpm(100, 106) == pytest.approx(6.0)
    assert h.variacao_bpm(120, 118) == pytest.approx(-1.6667, abs=1e-3)


def test_variacao_bpm_origem_invalida():
    with pytest.raises(ValueError):
        h.variacao_bpm(0, 120)


@pytest.mark.parametrize("b1,b2,ok", [
    (100, 106, True),      # exatamente 6%: limite incluído
    (100, 94, True),
    (100, 106.01, False),  # logo acima do limite
    (120, 128, False),     # 6,67%
    (128, 128, True),
])
def test_bpm_compativel_limite_de_6_por_cento(b1, b2, ok):
    assert h.bpm_compativel(b1, b2) is ok


# ---------------------------------------------------------------- RN08: classificação
def test_transicao_suave():
    t = h.classificar_transicao(F("7A", 121), F("8A", 118))
    assert t.nivel == h.SUAVE and t.tom_ok and t.bpm_ok
    assert t.rotulo == "🟢 Suave"
    assert t.motivo == "7A → 8A vizinho · BPM −2,5%"


def test_transicao_atencao_por_bpm():
    t = h.classificar_transicao(F("5A", 130), F("6A", 140))
    assert t.nivel == h.ATENCAO and t.tom_ok and not t.bpm_ok
    assert "acima de 6%" in t.motivo


def test_transicao_atencao_por_tom():
    t = h.classificar_transicao(F("7A", 121), F("3B", 124))
    assert t.nivel == h.ATENCAO and not t.tom_ok and t.bpm_ok
    assert t.motivo.startswith("Tom incompatível (7A → 3B)")


def test_transicao_arriscada():
    t = h.classificar_transicao(F("8A", 118), F("5A", 130))
    assert t.nivel == h.ARRISCADA
    assert t.rotulo == "🔴 Arriscada"


# ---------------------------------------------------------------- RN09: análise do setlist
def test_analise_do_setlist_rascunho_de_demonstracao():
    """Mesmo setlist do protótipo da Situação 1: 1 de 4 transições suaves = 25%."""
    faixas = [F("7A", 121, 5, 330), F("8A", 118, 4, 372), F("5A", 130, 9, 180),
              F("6A", 140, 8, 410), F("9A", 120, 5, 345)]
    a = h.analisar_setlist(faixas)
    assert [t.nivel for t in a.transicoes] == [h.SUAVE, h.ARRISCADA, h.ATENCAO, h.ARRISCADA]
    assert a.pontuacao == 25
    assert a.qtd_suaves == 1
    assert a.duracao_total == 1637          # 27:17
    assert a.bpm_medio == pytest.approx(125.8)
    assert a.nivel_geral == h.ARRISCADA


def test_analise_setlist_perfeito():
    faixas = [F("8A", 118), F("9A", 120), F("9B", 122), F("10B", 122)]
    a = h.analisar_setlist(faixas)
    assert a.pontuacao == 100 and a.nivel_geral == h.SUAVE


@pytest.mark.parametrize("pontos,nivel", [(80, h.SUAVE), (50, h.ATENCAO), (49.9, h.ARRISCADA)])
def test_nivel_geral_por_faixa_de_pontuacao(pontos, nivel):
    a = h.Analise(transicoes=[], pontuacao=pontos, duracao_total=0, bpm_medio=None, qtd_faixas=0)
    assert a.nivel_geral == nivel


@pytest.mark.parametrize("faixas", [[], [F()]])
def test_analise_sem_transicoes_nao_tem_pontuacao(faixas):
    a = h.analisar_setlist(faixas)
    assert a.pontuacao is None and a.nivel_geral is None and a.transicoes == []


def test_curva_de_energia():
    c = h.curva_energia([F("8A", 118, 4, 300, titulo="A"), F("9A", 120.5, 7, 240, titulo="B"),
                         F("3B", 140, 9, 200, titulo="C")])
    assert c == {"rotulos": ["1", "2", "3"], "titulos": ["A", "B", "C"], "bpm": [118.0, 120.5, 140.0],
                 "energia": [4, 7, 9], "tons": ["8A", "9A", "3B"], "duracoes": [300, 240, 200],
                 "niveis": [h.SUAVE, h.ARRISCADA]}


# ---------------------------------------------------------------- RN11: sugestões
def test_sugestoes_filtram_e_ordenam():
    ultima = F("9A", 120, id=1, titulo="Maré Alta")
    candidatas = [
        F("10A", 124, id=2, titulo="Batida Urbana"),      # vizinho, +3,3%
        F("9B", 122, id=3, titulo="Neon Copacabana"),     # relativo, +1,7%
        F("9A", 126, id=4, titulo="Mesmo tom"),           # mesmo tom, +5%
        F("8A", 113.5, id=5, titulo="Vizinho perto"),     # vizinho, −5,4%
        F("3B", 120, id=6, titulo="Tom ruim"),            # incompatível
        F("9A", 140, id=7, titulo="BPM ruim"),            # BPM fora
        ultima,                                            # a própria faixa
    ]
    sug = h.sugerir_proximas(ultima, candidatas)
    assert [s.faixa.titulo for s in sug] == ["Mesmo tom", "Batida Urbana", "Vizinho perto", "Neon Copacabana"]
    assert [s.tipo_tom for s in sug] == [h.MESMO_TOM, h.VIZINHO, h.VIZINHO, h.RELATIVO]


def test_sugestoes_respeitam_limite():
    candidatas = [F("8A", 120, id=i, titulo=f"F{i:02d}") for i in range(2, 30)]
    assert len(h.sugerir_proximas(F("8A", 120, id=1), candidatas)) == h.LIMITE_SUGESTOES
    assert len(h.sugerir_proximas(F("8A", 120, id=1), candidatas, limite=3)) == 3


def test_sugestoes_sem_ultima_faixa():
    assert h.sugerir_proximas(None, [F()]) == []


# ---------------------------------------------------------------- formatação
@pytest.mark.parametrize("valor,texto", [(3.333, "+3,3%"), (-2.48, "−2,5%"), (0.01, "0,0%"), (10.17, "+10,2%")])
def test_formatar_pct(valor, texto):
    assert h.formatar_pct(valor) == texto
