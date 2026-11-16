"""FaixaController: biblioteca de faixas (UC03, UC04, UC12)."""
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy import or_, select

from ..extensions import db
from ..models import Faixa, Genero, ItemSetlist, Setlist, TomCamelot
from ..services.csv_service import decodificar_arquivo, importar_faixas
from ..services.validacao import converter_bpm, validar_faixa
from .auth import login_obrigatorio

bp = Blueprint("faixas", __name__, url_prefix="/faixas")


def _faixa_do_usuario(id_faixa: int) -> Faixa:
    """RNF02: só devolve a faixa se ela pertencer ao usuário logado; senão, 404."""
    faixa = db.session.get(Faixa, id_faixa)
    if faixa is None or faixa.id_usuario != g.usuario.id:
        abort(404)
    return faixa


def _opcoes():
    return {
        "tons": db.session.scalars(select(TomCamelot).order_by(TomCamelot.numero, TomCamelot.modo)).all(),
        "generos": db.session.scalars(select(Genero).order_by(Genero.nome)).all(),
    }


@bp.route("/")
@login_obrigatorio
def listar():
    filtros = {k: (request.args.get(k) or "").strip()
               for k in ("q", "genero", "tom", "bpm_min", "bpm_max")}
    consulta = select(Faixa).where(Faixa.id_usuario == g.usuario.id)
    if filtros["q"]:
        termo = f"%{filtros['q']}%"
        consulta = consulta.where(or_(Faixa.titulo.ilike(termo), Faixa.artista.ilike(termo)))
    if filtros["genero"].isdigit():
        consulta = consulta.where(Faixa.id_genero == int(filtros["genero"]))
    if filtros["tom"]:
        consulta = consulta.where(Faixa.cod_tom == filtros["tom"].upper())
    bpm_min, bpm_max = converter_bpm(filtros["bpm_min"]), converter_bpm(filtros["bpm_max"])
    if filtros["bpm_min"] and bpm_min is not None:
        consulta = consulta.where(Faixa.bpm >= bpm_min)
    if filtros["bpm_max"] and bpm_max is not None:
        consulta = consulta.where(Faixa.bpm <= bpm_max)

    ordem = request.args.get("ordem", "titulo")
    colunas = {"titulo": Faixa.titulo, "artista": Faixa.artista, "bpm": Faixa.bpm,
               "tom": Faixa.cod_tom, "energia": Faixa.energia}
    consulta = consulta.order_by(colunas.get(ordem, Faixa.titulo), Faixa.titulo)

    pagina = db.paginate(consulta, page=request.args.get("pagina", 1, type=int),
                         per_page=20, error_out=False)
    total_biblioteca = db.session.query(Faixa).filter_by(id_usuario=g.usuario.id).count()
    return render_template("faixas/lista.html", pagina=pagina, filtros=filtros, ordem=ordem,
                           total_biblioteca=total_biblioteca, **_opcoes())


def _salvar(faixa: Faixa | None):
    """Fluxo comum de criação e edição (UC03)."""
    dados = request.form if request.method == "POST" else {}
    erros = {}
    if request.method == "POST":
        ids_generos = {g_.id for g_ in db.session.scalars(select(Genero)).all()}
        limpos, erros = validar_faixa(request.form, ids_generos)
        if not erros:
            duplicada = db.session.scalar(select(Faixa).where(
                Faixa.id_usuario == g.usuario.id,
                Faixa.titulo == limpos["titulo"], Faixa.artista == limpos["artista"],
                Faixa.id != (faixa.id if faixa else -1)))
            if duplicada:
                erros["titulo"] = f"Você já cadastrou “{limpos['titulo']}” de {limpos['artista']}."
        if not erros:
            nova = faixa is None
            if nova:
                faixa = Faixa(id_usuario=g.usuario.id)
                db.session.add(faixa)
            for campo, valor in limpos.items():
                setattr(faixa, campo, valor)
            db.session.commit()
            flash(f"Faixa “{faixa.titulo}” {'cadastrada' if nova else 'atualizada'} com sucesso.", "ok")
            if nova and request.form.get("continuar"):
                return redirect(url_for("faixas.nova"))
            return redirect(url_for("faixas.listar"))
        flash(f"Corrija {'o campo destacado' if len(erros) == 1 else f'os {len(erros)} campos destacados'} "
              "para salvar a faixa.", "bad")
    elif faixa is not None:
        dados = {"titulo": faixa.titulo, "artista": faixa.artista, "bpm": faixa.bpm_fmt,
                 "cod_tom": faixa.cod_tom, "id_genero": str(faixa.id_genero or ""),
                 "energia": str(faixa.energia), "duracao": faixa.duracao_fmt}
    return render_template("faixas/form.html", faixa=faixa, dados=dados, erros=erros, **_opcoes())


@bp.route("/nova", methods=["GET", "POST"])
@login_obrigatorio
def nova():
    return _salvar(None)


@bp.route("/<int:id_faixa>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar(id_faixa):
    return _salvar(_faixa_do_usuario(id_faixa))


@bp.route("/<int:id_faixa>/excluir", methods=["POST"])
@login_obrigatorio
def excluir(id_faixa):
    faixa = _faixa_do_usuario(id_faixa)
    nomes = db.session.scalars(
        select(Setlist.nome).join(ItemSetlist).where(ItemSetlist.id_faixa == faixa.id)
        .order_by(Setlist.nome)).all()
    if nomes:  # RN12
        flash(f"Não é possível excluir: “{faixa.titulo}” está nos setlists "
              f"{', '.join('“' + n + '”' for n in nomes)}. Remova-a deles primeiro.", "bad")
    else:
        db.session.delete(faixa)
        db.session.commit()
        flash(f"Faixa “{faixa.titulo}” excluída.", "ok")
    return redirect(url_for("faixas.listar"))


@bp.route("/importar", methods=["GET", "POST"])
@login_obrigatorio
def importar():
    resultado = None
    if request.method == "POST":
        arquivo = request.files.get("arquivo")
        if not arquivo or not arquivo.filename:
            flash("Selecione um arquivo CSV.", "bad")
        elif not arquivo.filename.lower().endswith((".csv", ".txt")):
            flash("O arquivo precisa ser .csv ou .txt (exportado do Rekordbox).", "bad")
        else:
            resultado = importar_faixas(decodificar_arquivo(arquivo.read()), g.usuario.id)
            if resultado.importadas:
                flash(f"{resultado.importadas} faixa(s) importada(s) com sucesso.", "ok")
            elif not resultado.erros:
                flash("Nenhuma faixa nova: todas já estavam na biblioteca.", "info")
    return render_template("faixas/importar.html", resultado=resultado)
