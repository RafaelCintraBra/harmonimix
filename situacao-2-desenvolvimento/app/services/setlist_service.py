"""Operações sobre os itens de um setlist (RF07, RF08, RN10).

A chave primária de `item_setlist` é (id_setlist, posicao), por isso trocar posições exige
cuidado: usamos uma posição temporária (a maior posição + 1) para nunca violar a chave durante a troca.
"""
from __future__ import annotations

from sqlalchemy import func, select

from ..extensions import db
from ..models import Faixa, ItemSetlist, Setlist


class RegraNegocioError(Exception):
    """Erro de regra de negócio, com uma mensagem pronta para mostrar ao usuário."""


def adicionar_faixa(setlist: Setlist, faixa: Faixa) -> ItemSetlist:
    """Adiciona `faixa` no final do setlist (RF07). Bloqueia repetição (RN10)."""
    if faixa.id_usuario != setlist.id_usuario:
        raise RegraNegocioError("Faixa não encontrada na sua biblioteca.")
    existente = next((i for i in setlist.itens if i.id_faixa == faixa.id), None)
    if existente:
        raise RegraNegocioError(
            f"“{faixa.titulo}” já está neste setlist (posição {existente.posicao}).")
    ultima = db.session.scalar(
        select(func.max(ItemSetlist.posicao)).where(ItemSetlist.id_setlist == setlist.id)) or 0
    item = ItemSetlist(id_setlist=setlist.id, posicao=ultima + 1, id_faixa=faixa.id)
    db.session.add(item)
    db.session.commit()
    db.session.refresh(setlist)
    return item


def _item(setlist: Setlist, posicao: int) -> ItemSetlist:
    item = db.session.get(ItemSetlist, (setlist.id, posicao))
    if item is None:
        raise RegraNegocioError("Item não encontrado no setlist.")
    return item


def remover_item(setlist: Setlist, posicao: int) -> Faixa:
    """Remove o item e reorganiza as posições seguintes (RF08)."""
    item = _item(setlist, posicao)
    faixa = item.faixa
    db.session.delete(item)
    db.session.flush()
    seguintes = db.session.scalars(
        select(ItemSetlist)
        .where(ItemSetlist.id_setlist == setlist.id, ItemSetlist.posicao > posicao)
        .order_by(ItemSetlist.posicao)).all()
    for seguinte in seguintes:          # em ordem crescente: a posição anterior já está livre
        seguinte.posicao -= 1
        db.session.flush()
    db.session.commit()
    db.session.refresh(setlist)
    return faixa


def mover_item(setlist: Setlist, posicao: int, direcao: str) -> int:
    """Troca o item com o vizinho de cima ('subir') ou de baixo ('descer'). Retorna a nova posição."""
    if direcao not in ("subir", "descer"):
        raise RegraNegocioError("Direção inválida.")
    destino = posicao - 1 if direcao == "subir" else posicao + 1
    item = _item(setlist, posicao)
    vizinho = db.session.get(ItemSetlist, (setlist.id, destino))
    if vizinho is None:
        raise RegraNegocioError("Esta faixa já está no limite do setlist.")

    # Posição livre e dentro do limite do tipo SMALLINT (um valor fixo alto estourava no MySQL)
    temporaria = db.session.scalar(
        select(func.max(ItemSetlist.posicao)).where(ItemSetlist.id_setlist == setlist.id)) + 1
    item.posicao = temporaria
    db.session.flush()
    vizinho.posicao = posicao
    db.session.flush()
    item.posicao = destino
    db.session.commit()
    db.session.refresh(setlist)
    return destino


def candidatas_para(setlist: Setlist) -> list[Faixa]:
    """Faixas do dono do setlist que ainda não estão nele (base para as sugestões, RN11)."""
    ids_no_set = {i.id_faixa for i in setlist.itens}
    faixas = db.session.scalars(
        select(Faixa).where(Faixa.id_usuario == setlist.id_usuario).order_by(Faixa.titulo)).all()
    return [f for f in faixas if f.id not in ids_no_set]
