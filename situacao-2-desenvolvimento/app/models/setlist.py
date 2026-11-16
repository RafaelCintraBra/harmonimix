from datetime import datetime

from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Index, Integer, SmallInteger,
                        String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Setlist(db.Model):
    """Sequência planejada de faixas (tabela `setlist`)."""

    __tablename__ = "setlist"

    id: Mapped[int] = mapped_column("id_setlist", Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_evento: Mapped[int | None] = mapped_column(
        ForeignKey("evento.id_evento", ondelete="SET NULL"))
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(500))
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="setlists")
    evento = relationship("Evento", back_populates="setlists")
    # Composição (RN13): os itens são excluídos junto com o setlist
    itens = relationship("ItemSetlist", back_populates="setlist", order_by="ItemSetlist.posicao",
                         cascade="all, delete-orphan", passive_deletes=True)

    @property
    def faixas(self):
        """Faixas do setlist na ordem de execução."""
        return [item.faixa for item in self.itens]


class ItemSetlist(db.Model):
    """Entidade associativa Setlist N:N Faixa, com a posição (tabela `item_setlist`)."""

    __tablename__ = "item_setlist"
    __table_args__ = (
        UniqueConstraint("id_setlist", "id_faixa", name="uq_item_setlist_faixa"),  # RN10
        CheckConstraint("posicao >= 1", name="ck_item_posicao"),
        Index("ix_item_faixa", "id_faixa"),
    )

    id_setlist: Mapped[int] = mapped_column(
        ForeignKey("setlist.id_setlist", ondelete="CASCADE"), primary_key=True)
    posicao: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=False)
    id_faixa: Mapped[int] = mapped_column(
        ForeignKey("faixa.id_faixa", ondelete="RESTRICT"), nullable=False)  # RN12

    setlist = relationship("Setlist", back_populates="itens")
    faixa = relationship("Faixa", back_populates="itens")
