"""Testes de SISTEMA (ponta a ponta): o HarmoniMix roda num servidor real e é usado
por um navegador Chromium controlado pelo Playwright, como um usuário faria.

Instalação (uma vez):
    pip install playwright pytest
    playwright install chromium
Execução (a partir desta pasta):
    python -m pytest
Se o Chromium já estiver instalado em outro lugar, informe: CHROMIUM_PATH=/caminho/do/chrome
"""
import os
import socket
import sys
import tempfile
import threading
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

RAIZ = Path(__file__).resolve().parents[2]
APP_DIR = RAIZ / "situacao-2-desenvolvimento"
EVIDENCIAS = RAIZ / "situacao-3-validacao" / "evidencias"
sys.path.insert(0, str(APP_DIR))

from app import create_app          # noqa: E402
from app.extensions import db       # noqa: E402
from app.seed import criar_demo     # noqa: E402
from config import TestConfig       # noqa: E402


def _porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def servidor():
    """Sobe a aplicação de verdade (com CSRF ligado) num banco SQLite temporário."""
    pasta = tempfile.mkdtemp()

    class Config(TestConfig):
        TESTING = False
        WTF_CSRF_ENABLED = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{pasta}/sistema.db"

    app = create_app(Config)
    with app.app_context():
        criar_demo()
    porta = _porta_livre()
    srv = make_server("127.0.0.1", porta, app, threaded=True)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{porta}"
    srv.shutdown()
    with app.app_context():
        db.engine.dispose()


@pytest.fixture(scope="session")
def navegador():
    with sync_playwright() as p:
        caminho = os.environ.get("CHROMIUM_PATH")
        yield p.chromium.launch(executable_path=caminho) if caminho else p.chromium.launch()


@pytest.fixture
def pagina(navegador, request):
    """Página nova a cada teste; guarda um print final como evidência (evidencias/CTS-xx.png)."""
    contexto = navegador.new_context(viewport={"width": 1280, "height": 800}, locale="pt-BR",
                                     accept_downloads=True)
    pg = contexto.new_page()
    erros_js = []
    pg.on("pageerror", lambda e: erros_js.append(str(e)))
    pg.erros_js = erros_js
    yield pg
    marcador = request.node.get_closest_marker("evidencia")
    if marcador:
        EVIDENCIAS.mkdir(exist_ok=True)
        pg.screenshot(path=str(EVIDENCIAS / f"{marcador.args[0]}.png"), full_page=True)
    contexto.close()
    assert not erros_js, f"Erros de JavaScript na página: {erros_js}"


@pytest.fixture
def entrar(servidor):
    def _entrar(pg, email="demo@harmonimix.dev", senha="Demo1234"):
        pg.goto(servidor + "/login")
        pg.fill("#f-email", email)
        pg.fill("#f-senha", senha)
        pg.click("button[type=submit]")
        pg.wait_for_url("**/painel")
    return _entrar


def pytest_configure(config):
    config.addinivalue_line("markers", "evidencia(nome): salva um print da tela final em evidencias/")
