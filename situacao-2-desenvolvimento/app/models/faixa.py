from datetime import datetime
from decimal import Decimal

from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric,
                        SmallInteger, String, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Faixa(db.Model):
    """Música da biblioteca de um DJ (tabela `faixa`)."""

    __tablename__ = "faixa"
    __table_args__ = (
        UniqueConstraint("id_usuario", "titulo", "artista", name="uq_faixa_usuario_titulo_artista"),  # RN05
        CheckConstraint("bpm BETWEEN 60 AND 200", name="ck_faixa_bpm"),                                # RN02
        CheckConstraint("energia BETWEEN 1 AND 10", name="ck_faixa_energia"),                          # RN04
        CheckConstraint("duracao_seg BETWEEN 30 AND 1800", name="ck_faixa_duracao"),                   # RN04
        Index("ix_faixa_usuario_bpm", "id_usuario", "bpm"),
        Index("ix_faixa_usuario_tom", "id_usuario", "cod_tom"),
    )

    id: Mapped[int] = mapped_column("id_faixa", Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    cod_tom: Mapped[str] = mapped_column(
        ForeignKey("tom_camelot.codigo", ondelete="RESTRICT"), nullable=False)
    id_genero: Mapped[int | None] = mapped_column(
        ForeignKey("genero.id_genero", ondelete="SET NULL"))
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    artista: Mapped[str] = mapped_column(String(120), nullable=False)
    bpm: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    energia: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=5)
    duracao_seg: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="faixas")
    tom = relationship("TomCamelot")
    genero = relationship("Genero")
    itens = relationship("ItemSetlist", back_populates="faixa", passive_deletes="all")

    @property
    def bpm_float(self) -> float:
        return float(self.bpm)

    @property
    def bpm_fmt(self) -> str:
        """BPM sem casas decimais desnecessárias: 128 ou 123,5."""
        v = float(self.bpm)
        return f"{v:.0f}" if v.is_integer() else f"{v:.2f}".rstrip("0").replace(".", ",")

    @property
    def duracao_fmt(self) -> str:
        return formatar_duracao(self.duracao_seg)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Faixa {self.titulo} {self.cod_tom} {self.bpm}>"


def formatar_duracao(segundos: int) -> str:
    """Converte segundos em mm:ss (ou h:mm:ss quando passa de 1 hora)."""
    segundos = int(segundos or 0)
    h, resto = divmod(segundos, 3600)
    m, s = divmod(resto, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
