"""EventoController: cadastro de eventos (UC05)."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy import select

from ..extensions import db
from ..models import Evento
from ..services.validacao import validar_evento
from .auth import login_obrigatorio

bp = Blueprint("eventos", __name__, url_prefix="/eventos")


def _evento_do_usuario(id_evento: int) -> Evento:
    evento = db.session.get(Evento, id_evento)
    if evento is None or evento.id_usuario != g.usuario.id:
        abort(404)
    return evento


@bp.route("/")
@login_obrigatorio
def listar():
    eventos = db.session.scalars(select(Evento).where(Evento.id_usuario == g.usuario.id)
                                 .order_by(Evento.data_evento.desc())).all()
    return render_template("eventos/lista.html", eventos=eventos)


def _salvar(evento: Evento | None):
    dados, erros = {}, {}
    if request.method == "POST":
        dados = request.form
        limpos, erros = validar_evento(request.form)
        if not erros:
            novo = evento is None
            if novo:
                evento = Evento(id_usuario=g.usuario.id)
                db.session.add(evento)
            for campo, valor in limpos.items():
                setattr(evento, campo, valor)
            db.session.commit()
            flash(f"Evento “{evento.nome}” {'cadastrado' if novo else 'atualizado'} com sucesso.", "ok")
            return redirect(url_for("eventos.listar"))
        flash("Corrija os campos destacados para salvar o evento.", "bad")
    elif evento is not None:
        dados = {"nome": evento.nome, "local": evento.local or "",
                 "data_evento": evento.data_evento.isoformat()}
    return render_template("eventos/form.html", evento=evento, dados=dados, erros=erros)


@bp.route("/novo", methods=["GET", "POST"])
@login_obrigatorio
def novo():
    return _salvar(None)


@bp.route("/<int:id_evento>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar(id_evento):
    return _salvar(_evento_do_usuario(id_evento))


@bp.route("/<int:id_evento>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_evento):
    evento = _evento_do_usuario(id_evento)
    qtd = len(evento.setlists)
    for setlist in evento.setlists:   # RN14: desvincula (o banco também faz SET NULL)
        setlist.id_evento = None
    db.session.delete(evento)
    db.session.commit()
    extra = f" {qtd} setlist(s) ficaram sem evento, mas não foram apagados." if qtd else ""
    flash(f"Evento “{evento.nome}” excluído.{extra}", "ok")
    return redirect(url_for("eventos.listar"))
