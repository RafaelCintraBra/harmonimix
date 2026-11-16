"""Testes de INTEGRAÇÃO: eventos (UC05, RN14) e página de ajuda (RF14)."""
from sqlalchemy import select

from app.extensions import db
from app.models import Evento, Setlist


def test_crud_evento(logado, app):
    resp = logado.post("/eventos/novo", data={"nome": "Casamento", "data_evento": "2030-05-10", "local": "Sítio"},
                       follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "Evento “Casamento” cadastrado com sucesso." in html and "10/05/2030" in html
    with app.app_context():
        eid = db.session.scalar(select(Evento)).id

    form = logado.get(f"/eventos/{eid}/editar").get_data(as_text=True)
    assert 'value="2030-05-10"' in form
    resp = logado.post(f"/eventos/{eid}/editar", data={"nome": "Casamento Ana", "data_evento": "2030-05-11"},
                       follow_redirects=True)
    assert "Evento “Casamento Ana” atualizado com sucesso." in resp.get_data(as_text=True)


def test_evento_invalido(logado):
    html = logado.post("/eventos/novo", data={"nome": "", "data_evento": ""}).get_data(as_text=True)
    assert "Preencha o campo nome do evento." in html and "Informe uma data válida." in html


def test_excluir_evento_desvincula_setlists_rn14(logado, app, usuario, criar_evento, criar_setlist):
    eid = criar_evento(usuario, nome="Festa")
    sid = criar_setlist(usuario, nome="Set da festa", id_evento=eid)
    html = logado.post(f"/eventos/{eid}/excluir", follow_redirects=True).get_data(as_text=True)
    assert "1 setlist(s) ficaram sem evento, mas não foram apagados." in html
    with app.app_context():
        assert db.session.get(Evento, eid) is None
        assert db.session.get(Setlist, sid).id_evento is None


def test_lista_de_eventos(logado, usuario, criar_evento, criar_setlist):
    assert "Nenhum evento cadastrado." in logado.get("/eventos/").get_data(as_text=True)
    eid = criar_evento(usuario, nome="Réveillon")
    criar_setlist(usuario, nome="Virada", id_evento=eid)
    html = logado.get("/eventos/").get_data(as_text=True)
    assert "Réveillon" in html and "Virada" in html


def test_ajuda_camelot(logado):
    html = logado.get("/ajuda/camelot?tom=12b").get_data(as_text=True)
    assert 'data-tom="12B"' in html and "12B, 11B, 1B, 12A" in html
    html = logado.get("/ajuda/camelot?tom=XYZ").get_data(as_text=True)
    assert 'data-tom="8A"' in html
