"""AuthController: cadastro, login e logout (UC01, UC02)."""
from functools import wraps

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import select

from ..extensions import db
from ..models import Usuario
from ..services.validacao import validar_usuario

bp = Blueprint("auth", __name__)


@bp.before_app_request
def carregar_usuario_logado():
    id_usuario = session.get("id_usuario")
    g.usuario = db.session.get(Usuario, id_usuario) if id_usuario else None


def login_obrigatorio(view):
    """Decorador: redireciona para o login quando não há usuário na sessão."""
    @wraps(view)
    def envoltorio(*args, **kwargs):
        if g.get("usuario") is None:
            flash("Faça login para continuar.", "info")
            return redirect(url_for("auth.login", proximo=request.path))
        return view(*args, **kwargs)
    return envoltorio


def _destino_seguro(proximo: str | None) -> str:
    """Evita redirecionamento aberto: só aceita caminhos internos."""
    if proximo and proximo.startswith("/") and not proximo.startswith("//"):
        return proximo
    return url_for("painel.inicio")


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if g.usuario:
        return redirect(url_for("painel.inicio"))
    dados, erros = {}, {}
    if request.method == "POST":
        dados, erros = validar_usuario(request.form)
        if not erros and db.session.scalar(select(Usuario).where(Usuario.email == dados["email"])):
            erros["email"] = "Este e-mail já está em uso. Faça login ou use outro e-mail."
        if not erros:
            usuario = Usuario(nome=dados["nome"], nome_artistico=dados["nome_artistico"],
                              email=dados["email"])
            usuario.definir_senha(dados["senha"])
            db.session.add(usuario)
            db.session.commit()
            session.clear()
            session["id_usuario"] = usuario.id
            flash(f"Bem-vindo(a), {usuario.nome_exibicao}! Comece cadastrando as suas faixas.", "ok")
            return redirect(url_for("painel.inicio"))
        flash("Corrija os campos destacados para criar a conta.", "bad")
    return render_template("auth/cadastro.html", dados=dados, erros=erros)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.usuario:
        return redirect(url_for("painel.inicio"))
    email = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        senha = request.form.get("senha") or ""
        usuario = db.session.scalar(select(Usuario).where(Usuario.email == email))
        if usuario and usuario.verificar_senha(senha):
            session.clear()
            session["id_usuario"] = usuario.id
            return redirect(_destino_seguro(request.args.get("proximo")))
        flash("E-mail ou senha incorretos. Verifique os dados e tente novamente.", "bad")
    return render_template("auth/login.html", email=email)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("auth.login"))
