"""Testes UNITÁRIOS do ValidacaoService (RN01 a RN04)."""
from decimal import Decimal

import pytest

from app.services import validacao as v

FAIXA_OK = {"titulo": "Aurora", "artista": "Lumen", "bpm": "118", "cod_tom": "8a",
            "id_genero": "", "energia": "4", "duracao": "06:12"}


@pytest.mark.parametrize("texto,seg", [("05:30", 330), ("5:30", 330), ("1:02:03", 3723), ("330", 330),
                                       ("00:30", 30)])
def test_converter_duracao_valida(texto, seg):
    assert v.converter_duracao(texto) == seg


@pytest.mark.parametrize("texto", ["", "5:3x", "5:60", "abc", "1:2:3:4", "123:00", None])
def test_converter_duracao_invalida(texto):
    assert v.converter_duracao(texto) is None


@pytest.mark.parametrize("texto,valor", [("128", Decimal("128.00")), ("123,5", Decimal("123.50")),
                                         (" 99.999 ", Decimal("100.00"))])
def test_converter_bpm(texto, valor):
    assert v.converter_bpm(texto) == valor


@pytest.mark.parametrize("texto", ["", "abc", "12a", "NaN", "inf"])
def test_converter_bpm_invalido(texto):
    assert v.converter_bpm(texto) is None


# ---------------------------------------------------------------- usuário (RN01)
@pytest.mark.parametrize("senha,ok", [("Senha123", True), ("abcdefgh", False), ("12345678", False),
                                      ("abc123", False)])
def test_senha_forte(senha, ok):
    assert v.senha_forte(senha) is ok


def test_validar_usuario_ok_normaliza_email():
    limpos, erros = v.validar_usuario({"nome": " Ana ", "email": " ANA@Mail.com ",
                                       "senha": "Senha123", "confirmacao": "Senha123"})
    assert erros == {}
    assert limpos["email"] == "ana@mail.com" and limpos["nome"] == "Ana"
    assert limpos["nome_artistico"] is None


def test_validar_usuario_com_erros():
    _, erros = v.validar_usuario({"nome": "A", "email": "sem-arroba", "senha": "123",
                                  "nome_artistico": "x" * 61})
    assert set(erros) == {"nome", "email", "senha", "nome_artistico"}


def test_validar_usuario_senhas_diferentes_e_email_vazio():
    _, erros = v.validar_usuario({"nome": "Ana", "email": "", "senha": "Senha123", "confirmacao": "Outra123"})
    assert erros["confirmacao"] == "As senhas não conferem."
    assert erros["email"] == "Preencha o campo e-mail."


def test_validar_usuario_nome_muito_longo():
    _, erros = v.validar_usuario({"nome": "A" * 101, "email": "a@b.co", "senha": "Senha123",
                                  "confirmacao": "Senha123"})
    assert "nome" in erros


# ---------------------------------------------------------------- faixa (RN02–RN04)
def test_validar_faixa_ok():
    limpos, erros = v.validar_faixa(FAIXA_OK)
    assert erros == {}
    assert limpos == {"titulo": "Aurora", "artista": "Lumen", "bpm": Decimal("118.00"), "cod_tom": "8A",
                      "id_genero": None, "energia": 4, "duracao_seg": 372}


def test_validar_faixa_energia_padrao_e_genero_valido():
    limpos, erros = v.validar_faixa({**FAIXA_OK, "energia": "", "id_genero": "3"}, ids_generos={3})
    assert erros == {} and limpos["energia"] == 5 and limpos["id_genero"] == 3


@pytest.mark.parametrize("campo,valor,trecho", [
    ("titulo", "", "Preencha o campo título."),
    ("titulo", "x" * 151, "no máximo 150"),
    ("artista", "", "Preencha o campo artista."),
    ("artista", "x" * 121, "no máximo 120"),
    ("bpm", "250", "entre 60 e 200"),
    ("bpm", "59.99", "entre 60 e 200"),
    ("bpm", "rápido", "como número"),
    ("cod_tom", "13A", "Selecione o tom"),
    ("energia", "11", "de 1 a 10"),
    ("energia", "0", "de 1 a 10"),
    ("duracao", "00:29", "entre 00:30 e 30:00"),
    ("duracao", "30:01", "entre 00:30 e 30:00"),
    ("duracao", "cinco", "formato mm:ss"),
    ("id_genero", "abc", "gênero da lista"),
])
def test_validar_faixa_erros(campo, valor, trecho):
    _, erros = v.validar_faixa({**FAIXA_OK, campo: valor})
    assert trecho in erros[campo]


def test_validar_faixa_genero_fora_da_lista():
    _, erros = v.validar_faixa({**FAIXA_OK, "id_genero": "99"}, ids_generos={1, 2})
    assert "id_genero" in erros


@pytest.mark.parametrize("bpm", ["60", "200"])
def test_validar_faixa_limites_de_bpm_aceitos(bpm):
    _, erros = v.validar_faixa({**FAIXA_OK, "bpm": bpm})
    assert "bpm" not in erros


# ---------------------------------------------------------------- evento e setlist
def test_validar_evento():
    limpos, erros = v.validar_evento({"nome": "Festa", "data_evento": "2026-12-12", "local": ""})
    assert erros == {} and limpos["data_evento"].isoformat() == "2026-12-12" and limpos["local"] is None
    _, erros = v.validar_evento({"nome": "", "data_evento": "12/12/2026", "local": "x" * 121})
    assert set(erros) == {"nome", "data_evento", "local"}
    _, erros = v.validar_evento({"nome": "x" * 121, "data_evento": "2026-12-12"})
    assert "nome" in erros


def test_validar_setlist():
    limpos, erros = v.validar_setlist({"nome": "Set", "id_evento": "3", "descricao": ""})
    assert erros == {} and limpos == {"nome": "Set", "descricao": None, "id_evento": 3}
    _, erros = v.validar_setlist({"nome": "", "id_evento": "abc", "descricao": "x" * 501})
    assert set(erros) == {"nome", "id_evento", "descricao"}
    _, erros = v.validar_setlist({"nome": "x" * 101})
    assert "nome" in erros
