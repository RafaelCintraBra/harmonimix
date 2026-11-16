"""Testes de INTEGRAÇÃO: biblioteca de faixas (UC03, UC04, UC12, RN05, RN12)."""
import io

from sqlalchemy import select

from app.extensions import db
from app.models import Faixa, Genero

FORM = {"titulo": "Cidade Acesa", "artista": "DJ Lumi", "bpm": "123,5", "cod_tom": "8B",
        "id_genero": "", "energia": "6", "duracao": "05:00"}


def _faixas(app):
    with app.app_context():
        return db.session.scalars(select(Faixa).order_by(Faixa.id)).all()


def test_cadastrar_faixa(logado, app):
    resp = logado.post("/faixas/nova", data=FORM, follow_redirects=True)
    assert "Faixa “Cidade Acesa” cadastrada com sucesso." in resp.get_data(as_text=True)
    [f] = _faixas(app)
    assert (f.titulo, float(f.bpm), f.cod_tom, f.energia, f.duracao_seg) == ("Cidade Acesa", 123.5, "8B", 6, 300)


def test_salvar_e_cadastrar_outra(logado):
    resp = logado.post("/faixas/nova", data={**FORM, "continuar": "1"})
    assert resp.location.endswith("/faixas/nova")


def test_cadastrar_faixa_invalida_mostra_erros_por_campo(logado, app):
    resp = logado.post("/faixas/nova", data={**FORM, "bpm": "250", "cod_tom": ""})
    html = resp.get_data(as_text=True)
    assert "Corrija os 2 campos destacados" in html
    assert "O BPM deve estar entre 60 e 200." in html and "Selecione o tom da faixa." in html
    assert _faixas(app) == []


def test_faixa_duplicada_rn05(logado, app, usuario, criar_faixa):
    criar_faixa(usuario, titulo="Cidade Acesa", artista="DJ Lumi")
    resp = logado.post("/faixas/nova", data=FORM)
    assert "Você já cadastrou “Cidade Acesa” de DJ Lumi." in resp.get_data(as_text=True)
    assert len(_faixas(app)) == 1


def test_editar_faixa(logado, app, usuario, criar_faixa):
    fid = criar_faixa(usuario, titulo="Velho", bpm=120)
    form = logado.get(f"/faixas/{fid}/editar").get_data(as_text=True)
    assert 'value="Velho"' in form and 'value="120"' in form
    resp = logado.post(f"/faixas/{fid}/editar", data={**FORM, "titulo": "Novo"}, follow_redirects=True)
    assert "Faixa “Novo” atualizada com sucesso." in resp.get_data(as_text=True)
    assert _faixas(app)[0].titulo == "Novo"


def test_editar_mantendo_mesmo_titulo_nao_acusa_duplicidade(logado, usuario, criar_faixa):
    fid = criar_faixa(usuario, titulo="Cidade Acesa", artista="DJ Lumi")
    resp = logado.post(f"/faixas/{fid}/editar", data=FORM)
    assert resp.status_code == 302


def test_excluir_faixa(logado, app, usuario, criar_faixa):
    fid = criar_faixa(usuario)
    resp = logado.post(f"/faixas/{fid}/excluir", follow_redirects=True)
    assert "excluída" in resp.get_data(as_text=True)
    assert _faixas(app) == []


def test_excluir_faixa_em_setlist_e_bloqueado_rn12(logado, app, usuario, criar_faixa, criar_setlist):
    fid = criar_faixa(usuario, titulo="Em uso")
    criar_setlist(usuario, nome="Set A", ids_faixas=[fid])
    criar_setlist(usuario, nome="Set B", ids_faixas=[fid])
    resp = logado.post(f"/faixas/{fid}/excluir", follow_redirects=True)
    html = resp.get_data(as_text=True)
    assert "Não é possível excluir" in html and "“Set A”, “Set B”" in html
    assert len(_faixas(app)) == 1


def test_listar_filtrar_e_ordenar(logado, usuario, criar_faixa):
    criar_faixa(usuario, titulo="Aurora", artista="Lumen", bpm=118, tom="8A")
    criar_faixa(usuario, titulo="Brisa", artista="Coral", bpm=100, tom="4A")
    criar_faixa(usuario, titulo="Concreto", artista="Kaleo", bpm=125, tom="11A")

    html = logado.get("/faixas/").get_data(as_text=True)
    assert all(t in html for t in ("Aurora", "Brisa", "Concreto"))

    html = logado.get("/faixas/?q=cor").get_data(as_text=True)        # busca no artista
    assert "Brisa" in html and "Aurora" not in html

    html = logado.get("/faixas/?bpm_min=110&bpm_max=120").get_data(as_text=True)
    assert "Aurora" in html and "Brisa" not in html and "Concreto" not in html

    html = logado.get("/faixas/?tom=11a").get_data(as_text=True)
    assert "Concreto" in html and "Aurora" not in html

    html = logado.get("/faixas/?ordem=bpm").get_data(as_text=True)
    assert html.index("Brisa") < html.index("Aurora") < html.index("Concreto")

    html = logado.get("/faixas/?q=inexistente").get_data(as_text=True)
    assert "Nenhuma faixa encontrada com esses filtros." in html


def test_filtrar_por_genero(logado, app, usuario, criar_faixa):
    with app.app_context():
        techno = db.session.scalar(select(Genero).where(Genero.nome == "Techno")).id
    criar_faixa(usuario, titulo="Pesada", id_genero=techno)
    criar_faixa(usuario, titulo="Leve")
    html = logado.get(f"/faixas/?genero={techno}").get_data(as_text=True)
    assert "Pesada" in html and "Leve" not in html


def test_paginacao(logado, usuario, criar_faixa):
    for i in range(25):
        criar_faixa(usuario, titulo=f"Faixa {i:02d}")
    html = logado.get("/faixas/").get_data(as_text=True)
    assert "Mostrando 20 de 25" in html and "Faixa 24" not in html
    html = logado.get("/faixas/?pagina=2").get_data(as_text=True)
    assert "Faixa 24" in html


def test_biblioteca_vazia(logado):
    assert "Sua biblioteca está vazia." in logado.get("/faixas/").get_data(as_text=True)


# ---------------------------------------------------------------- importação CSV (RF16)
def _enviar(cliente, texto, nome="faixas.csv", codificacao="utf-8"):
    return cliente.post("/faixas/importar", data={"arquivo": (io.BytesIO(texto.encode(codificacao)), nome)},
                        content_type="multipart/form-data", follow_redirects=True)


def test_importar_csv(logado, app, usuario, criar_faixa):
    criar_faixa(usuario, titulo="Já Existe", artista="X")
    csv = ("titulo;artista;bpm;tom;genero;energia;duracao\n"
           "Aurora Boreal;Lumen Drift;118;8A;Deep House;4;06:12\n"
           "Nova Vibe;MC Teste;95,5;5b;Gênero Novo;;03:30\n"
           "Já Existe;X;120;8A;;;05:00\n"
           "\n"
           "Quebrada;Y;300;8A;;;05:00\n")
    html = _enviar(logado, csv).get_data(as_text=True)
    assert "2 faixa(s) importada(s) com sucesso." in html
    assert "1 já existia(m)" in html
    assert "Linha 6: O BPM deve estar entre 60 e 200." in html
    with app.app_context():
        nova = db.session.scalar(select(Faixa).where(Faixa.titulo == "Nova Vibe"))
        assert nova.cod_tom == "5B" and nova.energia == 5 and nova.genero.nome == "Gênero Novo"


def test_importar_csv_virgula_cabecalho_ingles_e_latin1(logado, app):
    csv = "Title,Artist,BPM,Key,Duration\nCanção,Zé,128,9A,04:00\n"
    html = _enviar(logado, csv, codificacao="latin-1").get_data(as_text=True)
    assert "1 faixa(s) importada(s)" in html
    assert _faixas(app)[0].titulo == "Canção"


def test_importar_csv_sem_colunas_obrigatorias(logado):
    html = _enviar(logado, "nome;cantor\nA;B\n").get_data(as_text=True)
    assert "Colunas obrigatórias ausentes" in html


def test_importar_csv_vazio_ou_sem_arquivo(logado):
    assert "O arquivo está vazio." in _enviar(logado, "  ").get_data(as_text=True)
    assert "O arquivo precisa ser .csv." in _enviar(logado, "x", nome="musica.mp3").get_data(as_text=True)
    html = logado.post("/faixas/importar", data={}, follow_redirects=True).get_data(as_text=True)
    assert "Selecione um arquivo CSV." in html


def test_importar_csv_so_duplicadas(logado, usuario, criar_faixa):
    criar_faixa(usuario, titulo="A", artista="B")
    html = _enviar(logado, "titulo;artista;bpm;tom;duracao\nA;B;120;8A;05:00\n").get_data(as_text=True)
    assert "Nenhuma faixa nova" in html
