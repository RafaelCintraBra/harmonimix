"""Testes de INTEGRAÇÃO: setlists, editor e análise (UC06 a UC11, UC13, RN10, RN13, RN15)."""
from sqlalchemy import select

from app.extensions import db
from app.models import Faixa, ItemSetlist, Setlist


def _ordem(app, sid):
    with app.app_context():
        itens = db.session.scalars(select(ItemSetlist).where(ItemSetlist.id_setlist == sid)
                                   .order_by(ItemSetlist.posicao)).all()
        return [(i.posicao, i.faixa.titulo) for i in itens]


def test_criar_setlist_abre_editor(logado, app, usuario, criar_evento):
    eid = criar_evento(usuario)
    resp = logado.post("/setlists/novo", data={"nome": "Abertura", "id_evento": str(eid), "descricao": "x"})
    assert resp.status_code == 302 and "/setlists/" in resp.location
    html = logado.get(resp.location).get_data(as_text=True)
    assert "Abertura" in html and "O setlist está vazio" in html
    with app.app_context():
        assert db.session.scalar(select(Setlist)).id_evento == eid


def test_criar_setlist_sem_nome(logado):
    resp = logado.post("/setlists/novo", data={"nome": ""})
    assert resp.status_code == 400
    assert "Preencha o campo nome do setlist." in resp.get_data(as_text=True)


def test_nao_vincula_evento_de_outro_usuario_rn15(logado, criar_usuario, criar_evento):
    outro = criar_usuario(email="outro@x.com")
    eid = criar_evento(outro)
    resp = logado.post("/setlists/novo", data={"nome": "Set", "id_evento": str(eid)})
    assert resp.status_code == 400


def test_adicionar_faixas_e_ver_analise(logado, app, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario, titulo="Garoa", bpm=121, tom="7A", duracao=330)
    b = criar_faixa(usuario, titulo="Aurora", bpm=118, tom="8A", duracao=372)
    c = criar_faixa(usuario, titulo="Funk", bpm=130, tom="5A", duracao=180)
    sid = criar_setlist(usuario)

    r = logado.post(f"/setlists/{sid}/itens", data={"id_faixa": a}, follow_redirects=True)
    assert "“Garoa” adicionada na posição 1." in r.get_data(as_text=True)
    r = logado.post(f"/setlists/{sid}/itens", data={"id_faixa": b}, follow_redirects=True)
    assert "adicionada na posição 2." in r.get_data(as_text=True)
    r = logado.post(f"/setlists/{sid}/itens", data={"id_faixa": c}, follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Transição 🔴 Arriscada" in html            # avisa ao adicionar faixa incompatível (MSG15)

    assert _ordem(app, sid) == [(1, "Garoa"), (2, "Aurora"), (3, "Funk")]
    assert "7A → 8A vizinho · BPM −2,5%" in html
    assert "Tom incompatível (8A → 5A) · BPM +10,2% (acima de 6%)" in html
    assert "14:42" in html                              # 330 + 372 + 180 segundos
    assert "1 de 2 suaves" in html and "50%" in html
    assert 'id="visao-geral"' in html                   # visão geral do set (desenhada no navegador)


def test_faixa_repetida_no_setlist_rn10(logado, app, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario, titulo="Única")
    sid = criar_setlist(usuario, ids_faixas=[a])
    html = logado.post(f"/setlists/{sid}/itens", data={"id_faixa": a}, follow_redirects=True).get_data(as_text=True)
    assert "“Única” já está neste setlist (posição 1)." in html
    assert len(_ordem(app, sid)) == 1


def test_adicionar_faixa_inexistente_ou_de_outro_usuario(logado, criar_usuario, usuario, criar_faixa, criar_setlist):
    outro = criar_usuario(email="outro@x.com")
    alheia = criar_faixa(outro, titulo="Alheia")
    sid = criar_setlist(usuario)
    for dado in ({"id_faixa": alheia}, {"id_faixa": 9999}, {}):
        html = logado.post(f"/setlists/{sid}/itens", data=dado, follow_redirects=True).get_data(as_text=True)
        assert "Faixa não encontrada na sua biblioteca." in html


def test_remover_reorganiza_posicoes(logado, app, usuario, criar_faixa, criar_setlist):
    ids = [criar_faixa(usuario, titulo=t) for t in "ABCD"]
    sid = criar_setlist(usuario, ids_faixas=ids)
    html = logado.post(f"/setlists/{sid}/itens/2/remover", follow_redirects=True).get_data(as_text=True)
    assert "“B” removida do setlist." in html
    assert _ordem(app, sid) == [(1, "A"), (2, "C"), (3, "D")]
    html = logado.post(f"/setlists/{sid}/itens/9/remover", follow_redirects=True).get_data(as_text=True)
    assert "Item não encontrado" in html


def test_mover_subir_e_descer(logado, app, usuario, criar_faixa, criar_setlist):
    ids = [criar_faixa(usuario, titulo=t) for t in "ABC"]
    sid = criar_setlist(usuario, ids_faixas=ids)
    logado.post(f"/setlists/{sid}/itens/3/subir")
    assert _ordem(app, sid) == [(1, "A"), (2, "C"), (3, "B")]
    logado.post(f"/setlists/{sid}/itens/1/descer")
    assert _ordem(app, sid) == [(1, "C"), (2, "A"), (3, "B")]
    html = logado.post(f"/setlists/{sid}/itens/1/subir", follow_redirects=True).get_data(as_text=True)
    assert "já está no limite" in html
    html = logado.post(f"/setlists/{sid}/itens/1/lado", follow_redirects=True).get_data(as_text=True)
    assert "Direção inválida." in html
    assert _ordem(app, sid) == [(1, "C"), (2, "A"), (3, "B")]


def test_sugestoes_no_editor(logado, usuario, criar_faixa, criar_setlist):
    mare = criar_faixa(usuario, titulo="Maré Alta", bpm=120, tom="9A")
    criar_faixa(usuario, titulo="Batida Urbana", bpm=124, tom="10A")
    criar_faixa(usuario, titulo="Neon Copacabana", bpm=122, tom="9B")
    criar_faixa(usuario, titulo="Ponto Final", bpm=128, tom="1B")
    sid = criar_setlist(usuario, ids_faixas=[mare])
    html = logado.get(f"/setlists/{sid}").get_data(as_text=True)
    sug = html[html.index("Sugestões"):html.index("Adicionar faixa")]
    assert "Batida Urbana" in sug and "Neon Copacabana" in sug and "Ponto Final" not in sug
    assert sug.index("Batida Urbana") < sug.index("Neon Copacabana")     # vizinho antes de relativo

    busca = logado.get(f"/setlists/{sid}?busca=ponto").get_data(as_text=True)
    assert "Ponto Final" in busca and "incompatível" in busca


def test_editor_sem_sugestoes_compativeis(logado, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario, titulo="Sozinha", tom="1A", bpm=100)
    criar_faixa(usuario, titulo="Longe", tom="6B", bpm=170)
    sid = criar_setlist(usuario, ids_faixas=[a])
    html = logado.get(f"/setlists/{sid}").get_data(as_text=True)
    assert "Nenhuma faixa da sua biblioteca é compatível com “Sozinha”" in html
    assert "Nenhuma faixa fora do setlist corresponde" in logado.get(f"/setlists/{sid}?busca=zzz").get_data(as_text=True)


def test_editar_setlist(logado, app, usuario, criar_setlist, criar_evento):
    sid = criar_setlist(usuario, nome="Antigo")
    eid = criar_evento(usuario)
    html = logado.post(f"/setlists/{sid}/editar", data={"nome": "Novo nome", "id_evento": str(eid), "descricao": "d"},
                       follow_redirects=True).get_data(as_text=True)
    assert "Setlist atualizado." in html and "Novo nome" in html
    html = logado.post(f"/setlists/{sid}/editar", data={"nome": ""}, follow_redirects=True).get_data(as_text=True)
    assert "Preencha o campo nome do setlist." in html


def test_excluir_setlist_mantem_faixas_rn13(logado, app, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario)
    sid = criar_setlist(usuario, nome="Some", ids_faixas=[a])
    html = logado.post(f"/setlists/{sid}/excluir", follow_redirects=True).get_data(as_text=True)
    assert "As faixas continuam na sua biblioteca." in html
    with app.app_context():
        assert db.session.get(Setlist, sid) is None
        assert db.session.scalars(select(ItemSetlist)).all() == []
        assert db.session.get(Faixa, a) is not None


def test_listar_setlists_com_pontuacao(logado, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario, titulo="A", tom="8A", bpm=120)
    b = criar_faixa(usuario, titulo="B", tom="9A", bpm=122)
    criar_setlist(usuario, nome="Perfeito", ids_faixas=[a, b])
    html = logado.get("/setlists/").get_data(as_text=True)
    assert "Perfeito" in html and 'class="badge b-ok">100% suave' in html
    assert 'class="mini-ribbon"' in html                # miniatura da visão geral


def test_exportar_csv(logado, usuario, criar_faixa, criar_setlist):
    a = criar_faixa(usuario, titulo="Aurora", tom="8A", bpm=118, duracao=372)
    b = criar_faixa(usuario, titulo="Maré", tom="9A", bpm=120)
    sid = criar_setlist(usuario, nome="Meu Set!", ids_faixas=[a, b])
    resp = logado.get(f"/setlists/{sid}/exportar.csv")
    assert resp.mimetype == "text/csv"
    assert 'filename="meu-set.csv"' in resp.headers["Content-Disposition"]
    texto = resp.get_data(as_text=True)
    linhas = texto.lstrip("﻿").strip().splitlines()
    assert linhas[0].startswith("posicao;titulo")
    assert linhas[1].startswith("1;Aurora;Artista;118;8A;5;06:12")
    assert ";Suave;8A → 9A vizinho" in linhas[1]
    assert linhas[2].endswith(";;")


def test_painel_mostra_totais(logado, usuario, criar_faixa, criar_setlist, criar_evento):
    a = criar_faixa(usuario, bpm=120)
    criar_faixa(usuario, titulo="Outra", bpm=124)
    criar_setlist(usuario, nome="Set do painel", ids_faixas=[a])
    criar_evento(usuario, nome="Show futuro", data="2099-01-01")
    html = logado.get("/painel").get_data(as_text=True)
    assert "Set do painel" in html and "Show futuro" in html and "122,0" in html


def test_painel_vazio_orienta_o_usuario(logado):
    html = logado.get("/painel").get_data(as_text=True)
    assert "Sua biblioteca está vazia" in html and "Nenhum setlist ainda" in html
