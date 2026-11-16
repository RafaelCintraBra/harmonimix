"""PainelController: página inicial com os totais do DJ (RF15)."""
from datetime import date

from flask import Blueprint, g, redirect, render_template, url_for
from sqlalchemy import func, select

from ..extensions import db
from ..models import Evento, Faixa, Setlist
from ..services.harmonia import analisar_setlist, curva_energia
from .auth import login_obrigatorio

bp = Blueprint("painel", __name__)


@bp.route("/")
def raiz():
    return redirect(url_for("painel.inicio") if g.usuario else url_for("auth.login"))


@bp.route("/painel")
@login_obrigatorio
def inicio():
    uid = g.usuario.id
    qtd_faixas = db.session.scalar(select(func.count()).select_from(Faixa).where(Faixa.id_usuario == uid))
    bpm_medio = db.session.scalar(select(func.avg(Faixa.bpm)).where(Faixa.id_usuario == uid))
    setlists = db.session.scalars(
        select(Setlist).where(Setlist.id_usuario == uid)
        .order_by(Setlist.atualizado_em.desc(), Setlist.id.desc())).all()
    proximos = db.session.scalars(
        select(Evento).where(Evento.id_usuario == uid, Evento.data_evento >= date.today())
        .order_by(Evento.data_evento).limit(5)).all()
    recentes = [(s, analisar_setlist(s.faixas), curva_energia(s.faixas)) for s in setlists[:6]]
    return render_template("painel.html", qtd_faixas=qtd_faixas,
                           bpm_medio=float(bpm_medio) if bpm_medio is not None else None,
                           qtd_setlists=len(setlists), recentes=recentes, proximos=proximos)
