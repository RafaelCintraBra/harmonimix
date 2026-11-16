from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash

from ..extensions import db


class Usuario(db.Model):
    """DJ cadastrado no sistema (tabela `usuario`)."""

    __tablename__ = "usuario"
    __table_args__ = (
        CheckConstraint("length(trim(nome)) >= 2", name="ck_usuario_nome"),
    )

    id: Mapped[int] = mapped_column("id_usuario", Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_artistico: Mapped[str | None] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    faixas = relationship("Faixa", back_populates="usuario", cascade="all, delete-orphan")
    eventos = relationship("Evento", back_populates="usuario", cascade="all, delete-orphan")
    setlists = relationship("Setlist", back_populates="usuario", cascade="all, delete-orphan")

    # RNF01: a senha nunca é guardada em texto puro
    def definir_senha(self, senha: str) -> None:
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha: str) -> bool:
        return check_password_hash(self.senha_hash, senha)

    @property
    def nome_exibicao(self) -> str:
        return self.nome_artistico or self.nome.split()[0]

    @property
    def iniciais(self) -> str:
        partes = self.nome_exibicao.replace("DJ ", "").split()
        return "".join(p[0] for p in partes[:2]).upper() or "DJ"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Usuario {self.email}>"
