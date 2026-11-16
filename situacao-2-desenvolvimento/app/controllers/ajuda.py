"""AjudaController: página da Roda de Camelot (RF14)."""
from flask import Blueprint, render_template, request
from sqlalchemy import select

from ..extensions import db
from ..models import TomCamelot
from ..services.harmonia import TOLERANCIA_BPM, tom_valido, tons_compativeis_com
from .auth import login_obrigatorio

bp = Blueprint("ajuda", __name__, url_prefix="/ajuda")


@bp.route("/camelot")
@login_obrigatorio
def camelot():
    tom = (request.args.get("tom") or "8A").upper()
    if not tom_valido(tom):
        tom = "8A"
    tons = db.session.scalars(select(TomCamelot).order_by(TomCamelot.numero, TomCamelot.modo)).all()
    return render_template("ajuda/camelot.html", tom=tom, tons=tons,
                           compativeis=tons_compativeis_com(tom), tolerancia=TOLERANCIA_BPM)
