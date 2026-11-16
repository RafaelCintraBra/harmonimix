"""Testes de INTEGRAÇÃO: cadastro, login e logout (UC01, UC02, RF01, RF02, RNF01)."""
from sqlalchemy import select

from app.extensions import db
from app.models import Usuario
from tests.conftest import SENHA

NOVO = {"nome": "Lucas Andrade", "nome_artistico": "DJ Lucca", "email": "lucas@email.com",
        "senha": "Senha123", "confirmacao": "Senha123"}


def test_cadastro_cria_conta_e_ja_entra(client, app):
    resp = client.post("/cadastro", data=NOVO, follow_redirects=True)
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "Bem-vindo(a), DJ Lucca!" in html and "Olá, DJ Lucca" in html
    with app.app_context():
        u = db.session.scalar(select(Usuario).where(Usuario.email == "lucas@email.com"))
        assert u is not None


def test_senha_guardada_como_hash(client, app):
    client.post("/cadastro", data=NOVO)
    with app.app_context():
        u = db.session.scalar(select(Usuario).where(Usuario.email == "lucas@email.com"))
        assert u.senha_hash != "Senha123" and "Senha123" not in u.senha_hash
        assert u.senha_hash.startswith(("pbkdf2:", "scrypt:"))
        assert u.verificar_senha("Senha123") and not u.verificar_senha("errada")


def test_cadastro_email_duplicado(client, usuario):
    resp = client.post("/cadastro", data={**NOVO, "email": "DJ@teste.com"})
    assert resp.status_code == 200
    assert "Este e-mail já está em uso" in resp.get_data(as_text=True)


def test_cadastro_senha_fraca_mantem_dados_digitados(client):
    resp = client.post("/cadastro", data={**NOVO, "senha": "123", "confirmacao": "123"})
    html = resp.get_data(as_text=True)
    assert "A senha deve ter pelo menos 8 caracteres" in html
    assert 'value="Lucas Andrade"' in html          # não perde o que foi digitado
    assert 'aria-invalid="true"' in html


def test_login_e_logout(client, usuario):
    resp = client.post("/login", data={"email": "DJ@TESTE.com", "senha": SENHA})
    assert resp.status_code == 302 and resp.location.endswith("/painel")
    assert client.get("/painel").status_code == 200
    resp = client.post("/logout", follow_redirects=True)
    assert "Você saiu da sua conta." in resp.get_data(as_text=True)
    assert client.get("/painel").status_code == 302


def test_login_invalido(client, usuario):
    resp = client.post("/login", data={"email": "dj@teste.com", "senha": "errada"})
    html = resp.get_data(as_text=True)
    assert resp.status_code == 200
    assert "E-mail ou senha incorretos" in html
    assert 'value="dj@teste.com"' in html


def test_rotas_protegidas_exigem_login(client):
    for url in ["/painel", "/faixas/", "/faixas/nova", "/setlists/", "/eventos/", "/ajuda/camelot"]:
        resp = client.get(url)
        assert resp.status_code == 302 and "/login" in resp.location, url


def test_login_volta_para_pagina_pedida(client, usuario):
    resp = client.post("/login?proximo=/faixas/", data={"email": "dj@teste.com", "senha": SENHA})
    assert resp.location.endswith("/faixas/")


def test_login_nao_redireciona_para_site_externo(client, usuario):
    resp = client.post("/login?proximo=//site-malicioso.com", data={"email": "dj@teste.com", "senha": SENHA})
    assert resp.location.endswith("/painel")


def test_usuario_logado_nao_ve_login_nem_cadastro(logado):
    assert logado.get("/login").location.endswith("/painel")
    assert logado.get("/cadastro").location.endswith("/painel")


def test_raiz_redireciona(client, logado):
    assert logado.get("/").location.endswith("/painel")
    logado.post("/logout")
    assert client.get("/").location.endswith("/login")
