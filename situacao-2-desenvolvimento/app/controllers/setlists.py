"""SetlistController: setlists e editor com análise harmônica (UC06 a UC11, UC13)."""
from flask import (Blueprint, Response, abort, flash, g, redirect, render_template, request,
                   url_for)
from sqlalchemy import select

from ..extensions import db
from ..models import Evento, Faixa, Setlist
from ..services import harmonia
from ..services.csv_service import exportar_setlist
from ..services.setlist_service import (RegraNegocioError, adicionar_faixa, candidatas_para,
                                        mover_item, remover_item)
from ..services.validacao import validar_setlist
from .auth import login_obrigatorio

bp = Blueprint("setlists", __name__, url_prefix="/setlists")


def _setlist_do_usuario(id_setlist: int) -> Setlist:
    setlist = db.session.get(Setlist, id_setlist)
    if setlist is None or setlist.id_usuario != g.usuario.id:
        abort(404)
    return setlist


def _eventos_do_usuario():
    return db.session.scalars(select(Evento).where(Evento.id_usuario == g.usuario.id)
                              .order_by(Evento.data_evento.desc())).all()


def _validar_vinculo_evento(limpos: dict, erros: dict) -> None:
    """RN15: o evento precisa ser do mesmo usuário."""
    if limpos["id_evento"] is not None:
        evento = db.session.get(Evento, limpos["id_evento"])
        if evento is None or evento.id_usuario != g.usuario.id:
            erros["id_evento"] = "Selecione um evento da lista."


@bp.route("/")
@login_obrigatorio
def listar():
    setlists = db.session.scalars(select(Setlist).where(Setlist.id_usuario == g.usuario.id)
                                  .order_by(Setlist.atualizado_em.desc(), Setlist.id.desc())).all()
    linhas = [(s, harmonia.analisar_setlist(s.faixas)) for s in setlists]
    return render_template("setlists/lista.html", linhas=linhas, eventos=_eventos_do_usuario(),
                           dados={"id_evento": request.args.get("evento", "")}, erros={})


@bp.route("/novo", methods=["POST"])
@login_obrigatorio
def novo():
    limpos, erros = validar_setlist(request.form)
    _validar_vinculo_evento(limpos, erros)
    if erros:
        flash("Corrija os campos destacados para criar o setlist.", "bad")
        setlists = db.session.scalars(select(Setlist).where(Setlist.id_usuario == g.usuario.id)).all()
        linhas = [(s, harmonia.analisar_setlist(s.faixas)) for s in setlists]
        return render_template("setlists/lista.html", linhas=linhas, eventos=_eventos_do_usuario(),
                               dados=request.form, erros=erros), 400
    setlist = Setlist(id_usuario=g.usuario.id, **limpos)
    db.session.add(setlist)
    db.session.commit()
    flash(f"Setlist “{setlist.nome}” criado. Agora adicione as faixas.", "ok")
    return redirect(url_for("setlists.editor", id_setlist=setlist.id))


@bp.route("/<int:id_setlist>")
@login_obrigatorio
def editor(id_setlist):
    setlist = _setlist_do_usuario(id_setlist)
    faixas = setlist.faixas
    analise = harmonia.analisar_setlist(faixas)
    candidatas = candidatas_para(setlist)
    ultima = faixas[-1] if faixas else None
    sugestoes = harmonia.sugerir_proximas(ultima, candidatas)

    busca = (request.args.get("busca") or "").strip()
    resultados = []
    if busca:
        termo = busca.lower()
        resultados = [f for f in candidatas
                      if termo in f.titulo.lower() or termo in f.artista.lower()][:15]
    compativeis = {s.faixa.id for s in harmonia.sugerir_proximas(ultima, candidatas, limite=10_000)}

    return render_template(
        "setlists/editor.html", setlist=setlist, faixas=faixas, analise=analise,
        sugestoes=sugestoes, ultima=ultima, busca=busca, resultados=resultados,
        compativeis=compativeis, curva=harmonia.curva_energia(faixas),
        eventos=_eventos_do_usuario(), tem_biblioteca=bool(candidatas or faixas))


@bp.route("/<int:id_setlist>/editar", methods=["POST"])
@login_obrigatorio
def editar(id_setlist):
    setlist = _setlist_do_usuario(id_setlist)
    limpos, erros = validar_setlist(request.form)
    _validar_vinculo_evento(limpos, erros)
    if erros:
        flash(" ".join(erros.values()), "bad")
    else:
        for campo, valor in limpos.items():
            setattr(setlist, campo, valor)
        db.session.commit()
        flash("Setlist atualizado.", "ok")
    return redirect(url_for("setlists.editor", id_setlist=setlist.id))


@bp.route("/<int:id_setlist>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_setlist):
    setlist = _setlist_do_usuario(id_setlist)
    nome = setlist.nome
    db.session.delete(setlist)   # RN13: itens saem junto; faixas continuam na biblioteca
    db.session.commit()
    flash(f"Setlist “{nome}” excluído. As faixas continuam na sua biblioteca.", "ok")
    return redirect(url_for("setlists.listar"))


@bp.route("/<int:id_setlist>/itens", methods=["POST"])
@login_obrigatorio
def adicionar(id_setlist):
    setlist = _setlist_do_usuario(id_setlist)
    id_faixa = request.form.get("id_faixa", type=int)
    faixa = db.session.get(Faixa, id_faixa) if id_faixa else None
    if faixa is None or faixa.id_usuario != g.usuario.id:
        flash("Faixa não encontrada na sua biblioteca.", "bad")
        return redirect(url_for("setlists.editor", id_setlist=setlist.id))
    ultima = setlist.faixas[-1] if setlist.faixas else None
    try:
        item = adicionar_faixa(setlist, faixa)
    except RegraNegocioError as erro:
        flash(str(erro), "info")
    else:
        msg = f"“{faixa.titulo}” adicionada na posição {item.posicao}."
        categoria = "ok"
        if ultima is not None:
            transicao = harmonia.classificar_transicao(ultima, faixa)
            if transicao.nivel != harmonia.SUAVE:
                msg += f" Transição {transicao.rotulo}: {transicao.motivo}."
                categoria = "info"
        flash(msg, categoria)
    return redirect(url_for("setlists.editor", id_setlist=setlist.id) + "#ordem")


@bp.route("/<int:id_setlist>/itens/<int:posicao>/remover", methods=["POST"])
@login_obrigatorio
def remover(id_setlist, posicao):
    setlist = _setlist_do_usuario(id_setlist)
    try:
        faixa = remover_item(setlist, posicao)
        flash(f"“{faixa.titulo}” removida do setlist.", "ok")
    except RegraNegocioError as erro:
        flash(str(erro), "bad")
    return redirect(url_for("setlists.editor", id_setlist=setlist.id) + "#ordem")


@bp.route("/<int:id_setlist>/itens/<int:posicao>/<direcao>", methods=["POST"])
@login_obrigatorio
def mover(id_setlist, posicao, direcao):
    setlist = _setlist_do_usuario(id_setlist)
    try:
        mover_item(setlist, posicao, direcao)
    except RegraNegocioError as erro:
        flash(str(erro), "info")
    return redirect(url_for("setlists.editor", id_setlist=setlist.id) + "#ordem")


@bp.route("/<int:id_setlist>/exportar.csv")
@login_obrigatorio
def exportar(id_setlist):
    setlist = _setlist_do_usuario(id_setlist)
    nome_arquivo = "".join(c if c.isalnum() else "-" for c in setlist.nome).strip("-").lower() or "setlist"
    return Response(exportar_setlist(setlist), mimetype="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}.csv"'})
