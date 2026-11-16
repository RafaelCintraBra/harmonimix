"""Fixtures compartilhadas pelos testes (pytest).

Cada teste roda com um banco SQLite em memória novo, isolado dos demais.
Para rodar contra MySQL: TEST_DATABASE_URL=mysql+pymysql://... pytest
"""
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Evento, Faixa, ItemSetlist, Setlist, Usuario
from config import TestConfig

SENHA = "Senha123"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        _db.session.remove()
        _db.drop_all()
        _db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def ctx(app):
    with app.app_context():
        yield


@pytest.fixture
def criar_usuario(app):
    def _criar(email="dj@teste.com", nome="DJ Teste", artistico="DJ T"):
        with app.app_context():
            u = Usuario(nome=nome, nome_artistico=artistico, email=email)
            u.definir_senha(SENHA)
            _db.session.add(u)
            _db.session.commit()
            return u.id
    return _criar


@pytest.fixture
def usuario(criar_usuario):
    return criar_usuario()


@pytest.fixture
def logado(client, usuario):
    """Cliente já autenticado como `usuario`."""
    resp = client.post("/login", data={"email": "dj@teste.com", "senha": SENHA})
    assert resp.status_code == 302
    return client


@pytest.fixture
def criar_faixa(app):
    def _criar(id_usuario, titulo="Faixa", artista="Artista", bpm=120, tom="8A",
               energia=5, duracao=300, id_genero=None):
        with app.app_context():
            f = Faixa(id_usuario=id_usuario, titulo=titulo, artista=artista, bpm=Decimal(str(bpm)),
                      cod_tom=tom, energia=energia, duracao_seg=duracao, id_genero=id_genero)
            _db.session.add(f)
            _db.session.commit()
            return f.id
    return _criar


@pytest.fixture
def criar_setlist(app):
    def _criar(id_usuario, nome="Meu set", ids_faixas=(), id_evento=None):
        with app.app_context():
            s = Setlist(id_usuario=id_usuario, nome=nome, id_evento=id_evento)
            _db.session.add(s)
            _db.session.flush()
            for pos, id_faixa in enumerate(ids_faixas, start=1):
                _db.session.add(ItemSetlist(id_setlist=s.id, posicao=pos, id_faixa=id_faixa))
            _db.session.commit()
            return s.id
    return _criar


@pytest.fixture
def criar_evento(app):
    def _criar(id_usuario, nome="Festa", data="2030-01-15"):
        from datetime import date
        with app.app_context():
            e = Evento(id_usuario=id_usuario, nome=nome, data_evento=date.fromisoformat(data))
            _db.session.add(e)
            _db.session.commit()
            return e.id
    return _criar


def faixa_fake(tom="8A", bpm=120, energia=5, duracao=300, titulo="X", id=None):
    """Objeto simples com os atributos usados pelo HarmoniaService (para testes unitários puros)."""
    return SimpleNamespace(cod_tom=tom, bpm=bpm, energia=energia, duracao_seg=duracao,
                           titulo=titulo, id=id)
