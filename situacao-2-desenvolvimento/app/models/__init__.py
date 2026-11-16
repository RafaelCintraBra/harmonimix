"""Camada MODEL do padrão MVC.

Cada classe corresponde a uma tabela do projeto físico (situacao-1-planejamento/sql/01_schema_mysql.sql).
As restrições (CHECK, UNIQUE, FK) são repetidas aqui para que valham também no SQLite usado nos testes.
"""
from .usuario import Usuario
from .dominio import TomCamelot, Genero, TONS_CAMELOT, GENEROS_PADRAO
from .faixa import Faixa
from .evento import Evento
from .setlist import Setlist, ItemSetlist

__all__ = [
    "Usuario", "TomCamelot", "Genero", "Faixa", "Evento", "Setlist", "ItemSetlist",
    "TONS_CAMELOT", "GENEROS_PADRAO",
]
