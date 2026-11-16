"""ValidacaoService: valida e normaliza os dados dos formulários (RN01 a RN04).

Cada função recebe um dicionário (ex.: request.form) e devolve uma tupla (dados_limpos, erros),
em que `erros` mapeia o nome do campo para a mensagem que a tela mostra ao lado dele (RNF04).
"""
from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation

from .harmonia import tom_valido

RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BPM_MIN, BPM_MAX = 60, 200
DURACAO_MIN, DURACAO_MAX = 30, 1800

MSG_OBRIGATORIO = "Preencha o campo {campo}."


def _texto(dados: dict, chave: str) -> str:
    return (dados.get(chave) or "").strip()


# ---------------------------------------------------------------------------
# Conversões
# ---------------------------------------------------------------------------
def converter_duracao(texto: str) -> int | None:
    """'05:30' -> 330 · '1:02:03' -> 3723 · '330' -> 330. Retorna None se inválido."""
    texto = (texto or "").strip()
    if re.fullmatch(r"\d+", texto):
        return int(texto)
    partes = texto.split(":")
    if not 2 <= len(partes) <= 3 or not all(re.fullmatch(r"\d{1,2}", p) for p in partes):
        return None
    numeros = [int(p) for p in partes]
    if any(n >= 60 for n in numeros[1:]):
        return None
    total = 0
    for n in numeros:
        total = total * 60 + n
    return total


def converter_bpm(texto) -> Decimal | None:
    """Aceita '128', '123.5' ou '123,5'. Retorna None se não for número."""
    texto = str(texto or "").strip().replace(",", ".")
    try:
        valor = Decimal(texto)
    except InvalidOperation:
        return None
    if not valor.is_finite():
        return None
    return valor.quantize(Decimal("0.01"))


# ---------------------------------------------------------------------------
# Usuário (RN01)
# ---------------------------------------------------------------------------
def senha_forte(senha: str) -> bool:
    return (len(senha) >= 8 and any(c.isalpha() for c in senha)
            and any(c.isdigit() for c in senha))


def validar_usuario(dados: dict) -> tuple[dict, dict]:
    erros = {}
    nome = _texto(dados, "nome")
    nome_artistico = _texto(dados, "nome_artistico") or None
    email = _texto(dados, "email").lower()
    senha = dados.get("senha") or ""
    confirmacao = dados.get("confirmacao") or ""

    if len(nome) < 2:
        erros["nome"] = "Informe o seu nome (mínimo de 2 letras)."
    elif len(nome) > 100:
        erros["nome"] = "O nome pode ter no máximo 100 caracteres."
    if nome_artistico and len(nome_artistico) > 60:
        erros["nome_artistico"] = "O nome artístico pode ter no máximo 60 caracteres."
    if not email:
        erros["email"] = MSG_OBRIGATORIO.format(campo="e-mail")
    elif not RE_EMAIL.match(email) or len(email) > 120:
        erros["email"] = "Informe um e-mail válido, por exemplo nome@email.com."
    if not senha_forte(senha):
        erros["senha"] = "A senha deve ter pelo menos 8 caracteres, com letras e números."
    elif senha != confirmacao:
        erros["confirmacao"] = "As senhas não conferem."

    limpos = {"nome": nome, "nome_artistico": nome_artistico, "email": email, "senha": senha}
    return limpos, erros


# ---------------------------------------------------------------------------
# Faixa (RN02 a RN04)
# ---------------------------------------------------------------------------
def validar_faixa(dados: dict, ids_generos: set[int] | None = None) -> tuple[dict, dict]:
    erros = {}
    titulo = _texto(dados, "titulo")
    artista = _texto(dados, "artista")
    tom = _texto(dados, "cod_tom").upper()

    if not titulo:
        erros["titulo"] = MSG_OBRIGATORIO.format(campo="título")
    elif len(titulo) > 150:
        erros["titulo"] = "O título pode ter no máximo 150 caracteres."

    if not artista:
        erros["artista"] = MSG_OBRIGATORIO.format(campo="artista")
    elif len(artista) > 120:
        erros["artista"] = "O artista pode ter no máximo 120 caracteres."

    bpm = converter_bpm(dados.get("bpm"))
    if bpm is None:
        erros["bpm"] = "Informe o BPM como número (ex.: 128 ou 123,5)."
    elif not BPM_MIN <= bpm <= BPM_MAX:
        erros["bpm"] = f"O BPM deve estar entre {BPM_MIN} e {BPM_MAX}."

    if not tom_valido(tom):
        erros["cod_tom"] = "Selecione o tom da faixa."

    id_genero = None
    genero_txt = _texto(dados, "id_genero")
    if genero_txt:
        if not genero_txt.isdigit() or (ids_generos is not None and int(genero_txt) not in ids_generos):
            erros["id_genero"] = "Selecione um gênero da lista."
        else:
            id_genero = int(genero_txt)

    energia_txt = _texto(dados, "energia") or "5"
    if not energia_txt.isdigit() or not 1 <= int(energia_txt) <= 10:
        erros["energia"] = "A energia deve ser um número de 1 a 10."
        energia = None
    else:
        energia = int(energia_txt)

    duracao = converter_duracao(_texto(dados, "duracao"))
    if duracao is None:
        erros["duracao"] = "Informe a duração no formato mm:ss (ex.: 05:30)."
    elif not DURACAO_MIN <= duracao <= DURACAO_MAX:
        erros["duracao"] = "A duração deve estar entre 00:30 e 30:00."

    limpos = {"titulo": titulo, "artista": artista, "bpm": bpm, "cod_tom": tom,
              "id_genero": id_genero, "energia": energia, "duracao_seg": duracao}
    return limpos, erros


# ---------------------------------------------------------------------------
# Evento e setlist
# ---------------------------------------------------------------------------
def validar_evento(dados: dict) -> tuple[dict, dict]:
    erros = {}
    nome = _texto(dados, "nome")
    local = _texto(dados, "local") or None
    data_txt = _texto(dados, "data_evento")
    data_evento = None

    if not nome:
        erros["nome"] = MSG_OBRIGATORIO.format(campo="nome do evento")
    elif len(nome) > 120:
        erros["nome"] = "O nome pode ter no máximo 120 caracteres."
    if local and len(local) > 120:
        erros["local"] = "O local pode ter no máximo 120 caracteres."
    try:
        data_evento = datetime.strptime(data_txt, "%Y-%m-%d").date()
    except ValueError:
        erros["data_evento"] = "Informe uma data válida."

    return {"nome": nome, "local": local, "data_evento": data_evento}, erros


def validar_setlist(dados: dict) -> tuple[dict, dict]:
    erros = {}
    nome = _texto(dados, "nome")
    descricao = _texto(dados, "descricao") or None
    evento_txt = _texto(dados, "id_evento")

    if not nome:
        erros["nome"] = MSG_OBRIGATORIO.format(campo="nome do setlist")
    elif len(nome) > 100:
        erros["nome"] = "O nome pode ter no máximo 100 caracteres."
    if descricao and len(descricao) > 500:
        erros["descricao"] = "A descrição pode ter no máximo 500 caracteres."
    id_evento = int(evento_txt) if evento_txt.isdigit() else None
    if evento_txt and id_evento is None:
        erros["id_evento"] = "Selecione um evento da lista."

    return {"nome": nome, "descricao": descricao, "id_evento": id_evento}, erros

