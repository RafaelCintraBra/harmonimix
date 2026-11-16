"""Fábrica da aplicação HarmoniMix (Flask + padrão MVC).

    Model      -> app/models/       (SQLAlchemy, mapeia as tabelas do MySQL)
    View       -> app/templates/    (Jinja2 + HTML/CSS/JS em app/static/)
    Controller -> app/controllers/  (Blueprints: recebem a requisição e decidem o que fazer)
    Serviços   -> app/services/     (regras de negócio puras, testadas isoladamente)
"""
import logging

import click
from flask import Flask, render_template
from flask_wtf.csrf import CSRFError
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config
from .extensions import csrf, db


@event.listens_for(Engine, "connect")
def _ativar_fk_sqlite(conexao, _registro):
    """O SQLite só respeita chaves estrangeiras com este PRAGMA (no MySQL é automático)."""
    if conexao.__class__.__module__.startswith("sqlite3"):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    csrf.init_app(app)

    from .controllers import ajuda, auth, eventos, faixas, painel, setlists
    for modulo in (auth, painel, faixas, eventos, setlists, ajuda):
        app.register_blueprint(modulo.bp)

    _registrar_filtros(app)
    _registrar_erros(app)
    _registrar_comandos(app)

    with app.app_context():
        from .models.dominio import carregar_dominios
        db.create_all()
        carregar_dominios()

    return app


def _registrar_filtros(app: Flask) -> None:
    from .models.faixa import formatar_duracao
    from .services.harmonia import formatar_pct

    app.jinja_env.filters["duracao"] = formatar_duracao
    app.jinja_env.filters["pct"] = formatar_pct
    app.jinja_env.filters["num"] = lambda v, casas=1: (
        "—" if v is None else f"{v:.{casas}f}".replace(".", ","))


def _registrar_erros(app: Flask) -> None:
    """RNF11: páginas amigáveis, sem expor detalhes técnicos."""

    @app.errorhandler(404)
    def nao_encontrado(_erro):
        return render_template("erros/erro.html", codigo=404,
                               titulo="Página não encontrada",
                               mensagem="Ela pode ter sido removida ou você não tem acesso."), 404

    @app.errorhandler(CSRFError)
    def csrf_invalido(_erro):
        return render_template("erros/erro.html", codigo=400,
                               titulo="Formulário expirado",
                               mensagem="Recarregue a página e tente novamente."), 400

    @app.errorhandler(413)
    def arquivo_grande(_erro):
        return render_template("erros/erro.html", codigo=413,
                               titulo="Arquivo muito grande",
                               mensagem="O arquivo CSV pode ter no máximo 1 MB."), 413

    @app.errorhandler(500)
    def erro_interno(erro):
        db.session.rollback()
        logging.getLogger(__name__).exception("Erro interno: %s", erro)
        return render_template("erros/erro.html", codigo=500,
                               titulo="Algo deu errado do nosso lado",
                               mensagem="Tente novamente em instantes."), 500


def _registrar_comandos(app: Flask) -> None:
    @app.cli.command("init-db")
    @click.option("--reset", is_flag=True, help="Apaga e recria todas as tabelas.")
    def init_db(reset):
        """Cria as tabelas e carrega os tons Camelot e os gêneros."""
        from .models.dominio import carregar_dominios
        if reset:
            db.drop_all()
        db.create_all()
        carregar_dominios()
        click.echo("Banco de dados pronto.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Cria o usuário de demonstração com faixas, evento e setlists."""
        from .seed import criar_demo
        click.echo(criar_demo())
