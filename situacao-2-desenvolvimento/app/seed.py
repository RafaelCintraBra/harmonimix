"""Dados de demonstração (os mesmos de situacao-1-planejamento/sql/02_dados_iniciais.sql).
As faixas são FICTÍCIAS. Uso: flask --app run seed-demo
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from .extensions import db
from .models import Evento, Faixa, Genero, ItemSetlist, Setlist, Usuario
from .models.dominio import carregar_dominios

EMAIL_DEMO = "demo@harmonimix.dev"
SENHA_DEMO = "Demo1234"

FAIXAS_DEMO = [
    # titulo, artista, bpm, tom, genero, energia, duracao_seg
    ("Aurora Boreal", "Lumen Drift", 118, "8A", "Deep House", 4, 372),
    ("Maré Alta", "Coral Sound", 120, "9A", "Deep House", 5, 345),
    ("Neon Copacabana", "Rio Pulse", 122, "9B", "House", 6, 330),
    ("Pôr do Sol em Ipanema", "Lumen Drift", 122, "10B", "House", 6, 360),
    ("Batida Urbana", "Kaleo Beats", 124, "10A", "Tech House", 7, 318),
    ("Concreto", "Kaleo Beats", 125, "11A", "Tech House", 7, 342),
    ("Eletricidade", "Volt Sisters", 126, "11B", "Techno", 8, 390),
    ("Horizonte Vertical", "Volt Sisters", 128, "12B", "Techno", 9, 405),
    ("Ponto Final", "Nébula 9", 128, "1B", "Techno", 10, 420),
    ("Brisa", "Coral Sound", 100, "4A", "Downtempo", 3, 240),
    ("Funk do Satélite", "MC Órbita", 130, "5A", "Funk", 9, 180),
    ("Samba Digital", "Rio Pulse", 124, "3B", "Afro House", 7, 355),
    ("Céu de Néon", "Nébula 9", 140, "6A", "Trance", 8, 410),
    ("Cidade Acesa", "DJ Lumi", 123, "8B", "House", 6, 300),
    ("Garoa Paulista", "Coral Sound", 121, "7A", "Deep House", 5, 330),
    ("Tambores da Serra", "Rio Pulse", 120, "2A", "Afro House", 6, 365),
    ("Segunda Chance", "DJ Lumi", 95, "5B", "Pop", 5, 210),
    ("Madrugada", "Lumen Drift", 126, "12A", "Techno", 8, 380),
]

SET_PICO = ["Aurora Boreal", "Maré Alta", "Neon Copacabana", "Pôr do Sol em Ipanema",
            "Batida Urbana", "Concreto", "Eletricidade", "Horizonte Vertical", "Ponto Final"]
SET_RASCUNHO = ["Garoa Paulista", "Aurora Boreal", "Funk do Satélite", "Céu de Néon", "Maré Alta"]


def criar_demo() -> str:
    carregar_dominios()
    existente = db.session.scalar(select(Usuario).where(Usuario.email == EMAIL_DEMO))
    if existente:
        # Apaga primeiro os setlists (e seus itens): uma faixa em uso não pode ser apagada (RN12)
        for setlist in list(existente.setlists):
            db.session.delete(setlist)
        db.session.flush()
        db.session.expire(existente)   # recarrega a lista de setlists (já vazia)
        db.session.delete(existente)
        db.session.commit()

    usuario = Usuario(nome="Usuário Demonstração", nome_artistico="DJ Demo", email=EMAIL_DEMO)
    usuario.definir_senha(SENHA_DEMO)
    db.session.add(usuario)
    db.session.flush()

    generos = {g.nome: g.id for g in db.session.scalars(select(Genero)).all()}
    por_titulo = {}
    for titulo, artista, bpm, tom, genero, energia, duracao in FAIXAS_DEMO:
        faixa = Faixa(id_usuario=usuario.id, titulo=titulo, artista=artista, bpm=Decimal(bpm),
                      cod_tom=tom, id_genero=generos.get(genero), energia=energia,
                      duracao_seg=duracao)
        db.session.add(faixa)
        por_titulo[titulo] = faixa
    db.session.flush()

    evento = Evento(id_usuario=usuario.id, nome="Formatura Engenharia 2026",
                    data_evento=date(2026, 12, 12), local="Espaço Villa Verde")
    db.session.add(evento)
    db.session.flush()

    for nome, descricao, id_evento, titulos in (
        ("Warm-up até o pico", "Começa no Deep House e sobe gradualmente até o Techno.", evento.id, SET_PICO),
        ("Rascunho: precisa revisar", "Exemplo com transições de Atenção e Arriscadas.", None, SET_RASCUNHO),
    ):
        setlist = Setlist(id_usuario=usuario.id, id_evento=id_evento, nome=nome, descricao=descricao)
        db.session.add(setlist)
        db.session.flush()
        for posicao, titulo in enumerate(titulos, start=1):
            db.session.add(ItemSetlist(id_setlist=setlist.id, posicao=posicao,
                                       id_faixa=por_titulo[titulo].id))
    db.session.commit()
    return f"Demonstração criada: {EMAIL_DEMO} / {SENHA_DEMO} ({len(FAIXAS_DEMO)} faixas, 2 setlists)."
