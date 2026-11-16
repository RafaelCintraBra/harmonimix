"""Testes de segurança (RNF02, RNF03, RNF11) e das restrições do banco (projeto físico)."""
from decimal import Decimal

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError

from app import create_app
from app.extensions import db
from app.models import Faixa, ItemSetlist
from config import TestConfig
from tests.conftest import SENHA


# ---------------------------------------------------------------- RNF02: isolamento entre usuários
def test_usuario_nao_acessa_dados_de_outro(logado, criar_usuario, criar_faixa, criar_setlist, criar_evento):
    outro = criar_usuario(email="outro@x.com")
    fid = criar_faixa(outro, titulo="Segredo")
    sid = criar_setlist(outro, ids_faixas=[fid])
    eid = criar_evento(outro)

    for url in (f"/faixas/{fid}/editar", f"/setlists/{sid}", f"/setlists/{sid}/exportar.csv", f"/eventos/{eid}/editar"):
        assert logado.get(url).status_code == 404, url
    for url in (f"/faixas/{fid}/excluir", f"/setlists/{sid}/excluir", f"/eventos/{eid}/excluir",
                f"/setlists/{sid}/itens/1/remover", f"/setlists/{sid}/editar"):
        assert logado.post(url).status_code == 404, url
    assert "Segredo" not in logado.get("/faixas/").get_data(as_text=True)


# ---------------------------------------------------------------- RNF03: CSRF e XSS
def test_csrf_bloqueia_formulario_sem_token():
    class ComCsrf(TestConfig):
        WTF_CSRF_ENABLED = True
    app = create_app(ComCsrf)
    with app.app_context():
        from app.models import Usuario
        u = Usuario(nome="Ana", email="ana@x.com")
        u.definir_senha(SENHA)
        db.session.add(u)
        db.session.commit()
    resp = app.test_client().post("/login", data={"email": "ana@x.com", "senha": SENHA})
    assert resp.status_code == 400
    assert "Formulário expirado" in resp.get_data(as_text=True)
    with app.app_context():
        db.drop_all()
        db.engine.dispose()


def test_textos_do_usuario_sao_escapados_xss(logado, usuario, criar_faixa, criar_setlist):
    fid = criar_faixa(usuario, titulo="<script>alert(1)</script>")
    sid = criar_setlist(usuario, ids_faixas=[fid])
    for url in ("/faixas/", f"/setlists/{sid}"):
        html = logado.get(url).get_data(as_text=True)
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html or "\\u003cscript\\u003e" in html


def test_busca_com_aspas_nao_quebra_sql(logado, usuario, criar_faixa):
    criar_faixa(usuario, titulo="Normal")
    resp = logado.get("/faixas/?q=' OR 1=1 --")
    assert resp.status_code == 200 and "Normal" not in resp.get_data(as_text=True)


# ---------------------------------------------------------------- RNF11: erros amigáveis
def test_pagina_404_amigavel(client):
    resp = client.get("/nao-existe")
    assert resp.status_code == 404 and "Página não encontrada" in resp.get_data(as_text=True)


def test_pagina_500_amigavel_sem_detalhes_tecnicos(app):
    @app.route("/explodir")
    def explodir():
        raise RuntimeError("detalhe interno secreto")
    app.config["PROPAGATE_EXCEPTIONS"] = False
    resp = app.test_client().get("/explodir")
    html = resp.get_data(as_text=True)
    assert resp.status_code == 500 and "Algo deu errado do nosso lado" in html
    assert "detalhe interno secreto" not in html and "Traceback" not in html


def test_upload_grande_demais(logado, app):
    import io
    app.config["MAX_CONTENT_LENGTH"] = 100
    resp = logado.post("/faixas/importar", data={"arquivo": (io.BytesIO(b"x" * 500), "a.csv")},
                       content_type="multipart/form-data")
    assert resp.status_code == 413 and "Arquivo muito grande" in resp.get_data(as_text=True)


# ---------------------------------------------------------------- restrições do banco (mesmas do MySQL)
@pytest.mark.parametrize("campo,valor", [("bpm", Decimal("250")), ("energia", 11), ("duracao_seg", 10),
                                         ("cod_tom", "13C")])
def test_banco_rejeita_valores_fora_do_dominio(app, ctx, usuario, campo, valor):
    dados = dict(id_usuario=usuario, titulo="T", artista="A", bpm=Decimal("120"), cod_tom="8A",
                 energia=5, duracao_seg=300)
    dados[campo] = valor
    db.session.add(Faixa(**dados))
    # SQLite acusa IntegrityError; MySQL/MariaDB acusam CHECK violado como OperationalError (4025/3819)
    with pytest.raises(DBAPIError):
        db.session.commit()
    db.session.rollback()


def test_banco_rejeita_faixa_repetida_no_setlist(app, ctx, usuario, criar_faixa, criar_setlist):
    fid = criar_faixa(usuario)
    sid = criar_setlist(usuario, ids_faixas=[fid])
    db.session.add(ItemSetlist(id_setlist=sid, posicao=2, id_faixa=fid))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_banco_impede_excluir_faixa_em_uso(app, ctx, usuario, criar_faixa, criar_setlist):
    fid = criar_faixa(usuario)
    criar_setlist(usuario, ids_faixas=[fid])
    with pytest.raises(IntegrityError):
        db.session.execute(db.text("DELETE FROM faixa WHERE id_faixa = :i"), {"i": fid})
        db.session.commit()
    db.session.rollback()


def test_seed_demo(app, ctx):
    from app.seed import criar_demo
    msg = criar_demo()
    assert "18 faixas" in msg
    assert "18 faixas" in criar_demo()      # pode rodar de novo (recria a demonstração)
    from app.models import Setlist
    from app.services.harmonia import analisar_setlist
    sets = {s.nome: analisar_setlist(s.faixas).pontuacao for s in db.session.query(Setlist).all()}
    assert sets == {"Warm-up até o pico": 100, "Rascunho: precisa revisar": 25}
