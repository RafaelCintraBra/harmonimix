"""Tabelas de domínio: tons da Roda de Camelot e gêneros musicais."""
from sqlalchemy import CheckConstraint, Integer, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db

# As 24 tonalidades da Roda de Camelot (A = menor, B = maior)
TONS_CAMELOT = [
    ("1A", "Lá bemol menor (A♭m)"), ("1B", "Si maior (B)"),
    ("2A", "Mi bemol menor (E♭m)"), ("2B", "Fá sustenido maior (F♯)"),
    ("3A", "Si bemol menor (B♭m)"), ("3B", "Ré bemol maior (D♭)"),
    ("4A", "Fá menor (Fm)"), ("4B", "Lá bemol maior (A♭)"),
    ("5A", "Dó menor (Cm)"), ("5B", "Mi bemol maior (E♭)"),
    ("6A", "Sol menor (Gm)"), ("6B", "Si bemol maior (B♭)"),
    ("7A", "Ré menor (Dm)"), ("7B", "Fá maior (F)"),
    ("8A", "Lá menor (Am)"), ("8B", "Dó maior (C)"),
    ("9A", "Mi menor (Em)"), ("9B", "Sol maior (G)"),
    ("10A", "Si menor (Bm)"), ("10B", "Ré maior (D)"),
    ("11A", "Fá sustenido menor (F♯m)"), ("11B", "Lá maior (A)"),
    ("12A", "Ré bemol menor (D♭m)"), ("12B", "Mi maior (E)"),
]

GENEROS_PADRAO = [
    "Afro House", "Deep House", "Downtempo", "Funk", "House",
    "Pop", "Tech House", "Techno", "Trance",
]


class TomCamelot(db.Model):
    __tablename__ = "tom_camelot"
    __table_args__ = (
        UniqueConstraint("numero", "modo", name="uq_tom_numero_modo"),
        CheckConstraint("numero BETWEEN 1 AND 12", name="ck_tom_numero"),
        CheckConstraint("modo IN ('A', 'B')", name="ck_tom_modo"),
    )

    codigo: Mapped[str] = mapped_column(String(3), primary_key=True)
    numero: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    modo: Mapped[str] = mapped_column(String(1), nullable=False)
    nome_musical: Mapped[str] = mapped_column(String(30), nullable=False)


class Genero(db.Model):
    __tablename__ = "genero"

    # SMALLINT no MySQL; INTEGER no SQLite (que só faz autoincremento em INTEGER PRIMARY KEY)
    id: Mapped[int] = mapped_column("id_genero", SmallInteger().with_variant(Integer, "sqlite"),
                                    primary_key=True)
    nome: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)


def carregar_dominios() -> None:
    """Insere os 24 tons e os gêneros padrão, se ainda não existirem (idempotente)."""
    if db.session.query(TomCamelot).count() == 0:
        for codigo, nome in TONS_CAMELOT:
            db.session.add(TomCamelot(codigo=codigo, numero=int(codigo[:-1]),
                                      modo=codigo[-1], nome_musical=nome))
    existentes = {g.nome for g in db.session.query(Genero).all()}
    for nome in GENEROS_PADRAO:
        if nome not in existentes:
            db.session.add(Genero(nome=nome))
    db.session.commit()
