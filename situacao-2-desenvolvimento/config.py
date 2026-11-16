"""Configurações da aplicação HarmoniMix.

O banco é escolhido pela variável de ambiente DATABASE_URL (RNF10):
  - MySQL (produção):  mysql+pymysql://usuario:senha@localhost/harmonimix?charset=utf8mb4
  - SQLite (padrão):   sqlite:///harmonimix.db  (facilita rodar o projeto sem instalar um servidor)
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "harmonimix.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    WTF_CSRF_ENABLED = True
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # upload de CSV limitado a 1 MB
    ITENS_POR_PAGINA = 20


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    SQLALCHEMY_ENGINE_OPTIONS = {}
    WTF_CSRF_ENABLED = False
