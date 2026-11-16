"""Importação de faixas (RF16) e exportação de setlist (RF17) em CSV.

Formato de importação (primeira linha = cabeçalho; separador vírgula ou ponto e vírgula):
    titulo;artista;bpm;tom;genero;energia;duracao
    Aurora Boreal;Lumen Drift;118;8A;Deep House;4;06:12
`genero` e `energia` são opcionais. O gênero é criado automaticamente se ainda não existir.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field

from sqlalchemy import select

from ..extensions import db
from ..models import Faixa, Genero, Setlist
from .harmonia import analisar_setlist
from .validacao import validar_faixa

COLUNAS_OBRIGATORIAS = {"titulo", "artista", "bpm", "tom", "duracao"}
MAX_LINHAS = 2000


@dataclass
class ResultadoImportacao:
    importadas: int = 0
    ignoradas: int = 0                 # duplicadas (RN05)
    erros: list[str] = field(default_factory=list)


def _normalizar_cabecalho(nome: str) -> str:
    nome = (nome or "").strip().lower().lstrip("﻿")
    trocas = {"título": "titulo", "duração": "duracao", "gênero": "genero", "key": "tom",
              "title": "titulo", "artist": "artista", "duration": "duracao", "energy": "energia"}
    return trocas.get(nome, nome)


def importar_faixas(conteudo: str, id_usuario: int) -> ResultadoImportacao:
    resultado = ResultadoImportacao()
    if not conteudo.strip():
        resultado.erros.append("O arquivo está vazio.")
        return resultado

    primeira_linha = conteudo.splitlines()[0]
    separador = ";" if primeira_linha.count(";") >= primeira_linha.count(",") else ","
    leitor = csv.DictReader(io.StringIO(conteudo), delimiter=separador)
    leitor.fieldnames = [_normalizar_cabecalho(c) for c in (leitor.fieldnames or [])]
    faltando = COLUNAS_OBRIGATORIAS - set(leitor.fieldnames)
    if faltando:
        resultado.erros.append(
            "Colunas obrigatórias ausentes no cabeçalho: " + ", ".join(sorted(faltando)) + ".")
        return resultado

    generos = {g.nome.lower(): g for g in db.session.scalars(select(Genero)).all()}
    existentes = {(f.titulo.lower(), f.artista.lower()) for f in db.session.scalars(
        select(Faixa).where(Faixa.id_usuario == id_usuario)).all()}

    for contador, linha in enumerate(leitor, start=1):
        numero = leitor.line_num          # linha real do arquivo (conta linhas em branco)
        if contador > MAX_LINHAS:
            resultado.erros.append(f"O arquivo passou de {MAX_LINHAS} linhas; o restante foi ignorado.")
            break
        if not any((v or "").strip() for v in linha.values() if isinstance(v, str)):
            continue  # linha em branco

        genero_nome = (linha.get("genero") or "").strip()
        id_genero = ""
        if genero_nome:
            genero = generos.get(genero_nome.lower())
            if genero is None and len(genero_nome) <= 50:
                genero = Genero(nome=genero_nome)
                db.session.add(genero)
                db.session.flush()
                generos[genero_nome.lower()] = genero
            id_genero = str(genero.id) if genero else ""

        dados = {"titulo": linha.get("titulo"), "artista": linha.get("artista"),
                 "bpm": linha.get("bpm"), "cod_tom": linha.get("tom"), "id_genero": id_genero,
                 "energia": linha.get("energia"), "duracao": linha.get("duracao")}
        limpos, erros = validar_faixa(dados)
        if erros:
            resultado.erros.append(f"Linha {numero}: " + " ".join(erros.values()))
            continue
        chave = (limpos["titulo"].lower(), limpos["artista"].lower())
        if chave in existentes:
            resultado.ignoradas += 1
            continue
        existentes.add(chave)
        db.session.add(Faixa(id_usuario=id_usuario, **limpos))
        resultado.importadas += 1

    db.session.commit()
    return resultado


def exportar_setlist(setlist: Setlist) -> str:
    """Gera o CSV do setlist com a análise de cada transição."""
    faixas = setlist.faixas
    analise = analisar_setlist(faixas)
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";")
    escritor.writerow(["posicao", "titulo", "artista", "bpm", "tom", "energia", "duracao",
                       "transicao_para_proxima", "motivo"])
    for i, faixa in enumerate(faixas):
        transicao = analise.transicoes[i] if i < len(analise.transicoes) else None
        escritor.writerow([
            i + 1, faixa.titulo, faixa.artista, faixa.bpm_fmt, faixa.cod_tom, faixa.energia,
            faixa.duracao_fmt,
            transicao.rotulo.split(" ", 1)[1] if transicao else "",
            transicao.motivo if transicao else "",
        ])
    return "﻿" + saida.getvalue()  # BOM: o Excel abre os acentos corretamente
