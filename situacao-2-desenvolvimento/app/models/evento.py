from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db


class Evento(db.Model):
    """Apresentação para a qual o DJ prepara setlists (tabela `evento`)."""

    __tablename__ = "evento"
    __table_args__ = (Index("ix_evento_usuario_data", "id_usuario", "data_evento"),)

    id: Mapped[int] = mapped_column("id_evento", Integer, primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    data_evento: Mapped[date] = mapped_column(Date, nullable=False)
    local: Mapped[str | None] = mapped_column(String(120))
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="eventos")
    # RN14: ao excluir o evento, os setlists são apenas desvinculados (ON DELETE SET NULL)
    setlists = relationship("Setlist", back_populates="evento", passive_deletes=True)

    @property
    def data_fmt(self) -> str:
        return self.data_evento.strftime("%d/%m/%Y")

    @property
    def dias_restantes(self) -> int:
        return (self.data_evento - date.today()).days
