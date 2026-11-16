"""Casos de teste de SISTEMA (CTS) do HarmoniMix, executados num navegador real.

Cada teste corresponde a um caso documentado em ../PLANO-DE-TESTES.md (seção 5).
Os testes que alteram dados usam uma conta nova, para não depender da ordem de execução.
"""
import csv
import io
import itertools
import re
from pathlib import Path

import pytest
from playwright.sync_api import expect

MODELO_CSV = Path(__file__).resolve().parents[2] / "situacao-2-desenvolvimento" / "exemplos" / "modelo-importacao.csv"
_contador = itertools.count(1)


def nova_conta(pg, servidor, nome="Teste Sistema"):
    """Cria uma conta pela tela de cadastro e devolve o e-mail usado."""
    email = f"cts{next(_contador)}@teste.com"
    pg.goto(servidor + "/cadastro")
    pg.fill("#f-nome", nome)
    pg.fill("#f-email", email)
    pg.fill("#f-senha", "Senha123")
    pg.fill("#f-confirmacao", "Senha123")
    pg.click("button[type=submit]")
    pg.wait_for_url("**/painel")
    return email


def cadastrar_faixa(pg, servidor, titulo, artista, bpm, tom, duracao="05:00"):
    pg.goto(servidor + "/faixas/nova")
    pg.fill("#f-titulo", titulo)
    pg.fill("#f-artista", artista)
    pg.fill("#f-bpm", str(bpm))
    pg.select_option("#f-cod_tom", tom)
    pg.fill("#f-duracao", duracao)
    pg.click("button:has-text('Salvar faixa')")
    expect(pg.locator(".alert.ok")).to_contain_text("cadastrada com sucesso")


# --------------------------------------------------------------------------- CTS-01
@pytest.mark.evidencia("CTS-01-cadastro-login-logout")
def test_cts01_cadastro_login_e_logout(pagina, servidor):
    email = nova_conta(pagina, servidor, nome="Lucas Andrade")
    expect(pagina.locator("h1")).to_contain_text("Olá, Lucas")
    pagina.get_by_role("button", name="Sair").click()
    expect(pagina.locator(".alert")).to_contain_text("Você saiu da sua conta.")
    pagina.goto(servidor + "/painel")                          # rota protegida
    expect(pagina).to_have_url(re.compile(r"/login"))
    pagina.fill("#f-email", email)
    pagina.fill("#f-senha", "senha-errada1")
    pagina.click("button[type=submit]")
    expect(pagina.locator(".alert.bad")).to_contain_text("E-mail ou senha incorretos")
    pagina.fill("#f-senha", "Senha123")
    pagina.click("button[type=submit]")
    expect(pagina).to_have_url(re.compile(r"/painel$"))


# --------------------------------------------------------------------------- CTS-02
@pytest.mark.evidencia("CTS-02-validacao-formulario-faixa")
def test_cts02_validacao_do_formulario_de_faixa(pagina, servidor):
    nova_conta(pagina, servidor)
    pagina.goto(servidor + "/faixas/nova")
    pagina.fill("#f-titulo", "Aurora Boreal")
    pagina.fill("#f-artista", "Lumen Drift")
    pagina.fill("#f-bpm", "250")
    pagina.fill("#f-duracao", "6:1x")
    pagina.click("button:has-text('Salvar faixa')")
    expect(pagina.locator(".alert.bad")).to_contain_text("Corrija os 3 campos destacados")
    expect(pagina.locator("#e-bpm")).to_have_text("O BPM deve estar entre 60 e 200.")
    expect(pagina.locator("#f-titulo")).to_have_value("Aurora Boreal")    # não perde o que foi digitado
    # controle deslizante de energia atualiza o número na tela (JavaScript)
    pagina.locator("#f-energia").fill("8")
    expect(pagina.locator("#energia-valor")).to_have_text("8")
    pagina.fill("#f-bpm", "118")
    pagina.select_option("#f-cod_tom", "8A")
    pagina.fill("#f-duracao", "06:12")
    pagina.click("button:has-text('Salvar faixa')")
    expect(pagina.locator(".alert.ok")).to_contain_text("Faixa “Aurora Boreal” cadastrada com sucesso.")
    linha = pagina.locator("tr", has_text="Aurora Boreal")
    expect(linha).to_contain_text("118")
    expect(linha).to_contain_text("8A")
    expect(linha).to_contain_text("06:12")


# --------------------------------------------------------------------------- CTS-03
@pytest.mark.evidencia("CTS-03-busca-e-filtros")
def test_cts03_busca_filtros_e_ordenacao(pagina, servidor, entrar):
    entrar(pagina)
    pagina.goto(servidor + "/faixas/")
    expect(pagina.locator("tbody tr")).to_have_count(18)
    pagina.fill("#bpm_min", "120")
    pagina.fill("#bpm_max", "124")
    pagina.select_option("#tom", "9A")
    pagina.click("button:has-text('Filtrar')")
    expect(pagina.locator("tbody tr")).to_have_count(1)
    expect(pagina.locator("tbody")).to_contain_text("Maré Alta")
    pagina.click("a[title='Limpar filtros']")
    pagina.fill("#q", "lumen")
    pagina.click("button:has-text('Filtrar')")
    expect(pagina.locator("tbody tr")).to_have_count(3)
    pagina.click("th a:has-text('BPM')")                       # ordenar por BPM
    bpms = [float(t.replace(",", ".")) for t in pagina.locator("tbody tr td:nth-child(3)").all_inner_texts()]
    assert bpms == sorted(bpms)


# --------------------------------------------------------------------------- CTS-04
@pytest.mark.evidencia("CTS-04-importar-csv")
def test_cts04_importar_planilha_csv(pagina, servidor):
    nova_conta(pagina, servidor)
    pagina.goto(servidor + "/faixas/importar")
    pagina.set_input_files("#arquivo", str(MODELO_CSV))
    pagina.click("button:has-text('Importar')")
    expect(pagina.locator(".alert.ok")).to_contain_text("3 faixa(s) importada(s) com sucesso.")
    pagina.goto(servidor + "/faixas/")
    expect(pagina.locator("tbody tr")).to_have_count(3)


# --------------------------------------------------------------------------- CTS-05 e CTS-06
@pytest.mark.evidencia("CTS-06-montar-setlist-com-sugestoes")
def test_cts05_06_criar_evento_setlist_e_montar_com_sugestoes(pagina, servidor):
    nova_conta(pagina, servidor)
    for f in [("Garoa", "A", 121, "7A"), ("Aurora", "B", 118, "8A"), ("Maré", "C", 120, "9A"),
              ("Neon", "D", 122, "9B"), ("Funk", "E", 130, "5A")]:
        cadastrar_faixa(pagina, servidor, *f)

    pagina.goto(servidor + "/eventos/novo")                    # CTS-05: evento
    pagina.fill("#f-nome", "Formatura")
    pagina.fill("#f-data_evento", "2030-12-12")
    pagina.click("button:has-text('Salvar evento')")
    expect(pagina.locator("tbody")).to_contain_text("12/12/2030")

    pagina.goto(servidor + "/setlists/")
    pagina.fill("#f-nome", "Set da formatura")
    pagina.select_option("#f-id_evento", label="Formatura (12/12/2030)")
    pagina.click("button:has-text('Criar e abrir editor')")
    expect(pagina.locator("h1")).to_have_text("Set da formatura")
    expect(pagina.locator(".empty")).to_contain_text("O setlist está vazio")

    pagina.fill("input[name=busca]", "Garoa")                  # 1ª faixa pela busca
    pagina.click("button:has-text('Buscar')")
    pagina.locator(".sug", has_text="Garoa").locator("button").click()
    expect(pagina.locator(".alert.ok")).to_contain_text("“Garoa” adicionada na posição 1.")

    sugestoes = pagina.locator("#sugestoes")                   # CTS-06: sugestões compatíveis
    expect(sugestoes).to_contain_text("Aurora")
    expect(sugestoes).not_to_contain_text("Funk")              # 7A → 5A é incompatível
    sugestoes.locator(".sug", has_text="Aurora").locator("button").click()
    pagina.locator("#sugestoes .sug", has_text="Maré").locator("button").click()

    expect(pagina.locator(".trans")).to_have_count(2)
    expect(pagina.locator(".trans").first).to_contain_text("Suave")
    expect(pagina.locator(".trans").first).to_contain_text("7A → 8A vizinho · BPM −2,5%")
    expect(pagina.locator(".stat", has_text="pontuação harmônica")).to_contain_text("100%")
    expect(pagina.locator(".stat", has_text="duração total")).to_contain_text("15:00")


# --------------------------------------------------------------------------- CTS-07
@pytest.mark.evidencia("CTS-07-reordenar-remover")
def test_cts07_reordenar_remover_e_recalcular(pagina, servidor):
    nova_conta(pagina, servidor)
    for f in [("Aurora", "B", 118, "8A"), ("Funk", "E", 130, "5A"), ("Maré", "C", 120, "9A")]:
        cadastrar_faixa(pagina, servidor, *f)
    pagina.goto(servidor + "/setlists/")
    pagina.fill("#f-nome", "Rascunho")
    pagina.click("button:has-text('Criar e abrir editor')")
    for titulo in ("Aurora", "Funk", "Maré"):
        pagina.fill("input[name=busca]", titulo)
        pagina.click("button:has-text('Buscar')")
        pagina.locator(".sug", has_text=titulo).locator("button").click()
    expect(pagina.locator(".trans").first).to_contain_text("Arriscada")         # 8A → 5A, +10,2%

    pagina.get_by_role("button", name="Descer Funk").click()                      # Funk vai para o fim
    titulos = pagina.locator(".track .t-title").all_inner_texts()
    assert titulos == ["Aurora", "Maré", "Funk"]
    expect(pagina.locator(".trans").first).to_contain_text("Suave")
    expect(pagina.get_by_role("button", name="Subir Aurora")).to_be_disabled()     # 1ª faixa não sobe

    pagina.get_by_role("button", name="Remover Funk").click()
    expect(pagina.locator(".alert.ok")).to_contain_text("“Funk” removida do setlist.")
    expect(pagina.locator(".track")).to_have_count(2)
    expect(pagina.locator(".stat", has_text="pontuação harmônica")).to_contain_text("100%")


# --------------------------------------------------------------------------- CTS-08
@pytest.mark.evidencia("CTS-08-curva-de-energia")
def test_cts08_grafico_da_curva_de_energia(pagina, servidor, entrar):
    entrar(pagina)
    pagina.goto(servidor + "/setlists/")
    pagina.click("text=Warm-up até o pico")
    grafico = pagina.locator("#visao-geral svg")
    expect(grafico).to_be_visible()
    expect(grafico.locator("rect")).to_have_count(9)                       # 1 bloco por faixa (cor = tom)
    expect(grafico.locator("circle")).to_have_count(8)                     # 1 LED por transição
    expect(grafico.locator("polyline")).to_have_count(2)                   # linha de BPM (contorno + traço)
    expect(grafico.locator("rect").first.locator("title")).to_contain_text("Aurora Boreal (8A, 118 BPM, energia 4)")
    expect(grafico.locator("circle").first.locator("title")).to_have_text("Transição 1 → 2: Suave")
    # blocos proporcionais à duração: a faixa de 7:00 é mais larga que a de 5:18
    larguras = [float(r.get_attribute("width")) for r in grafico.locator("rect").all()]
    assert larguras[8] > larguras[4]


# --------------------------------------------------------------------------- CTS-09
@pytest.mark.evidencia("CTS-09-confirmacao-exclusao")
def test_cts09_exclusao_pede_confirmacao(pagina, servidor):
    nova_conta(pagina, servidor)
    cadastrar_faixa(pagina, servidor, "Descartável", "X", 120, "8A")
    mensagens = []

    pagina.once("dialog", lambda d: (mensagens.append(d.message), d.dismiss()))   # Cancelar
    pagina.locator("tr", has_text="Descartável").locator("button:has-text('Excluir')").click()
    expect(pagina.locator("tbody tr")).to_have_count(1)
    assert "Tem certeza que deseja excluir “Descartável”?" in mensagens[0]

    pagina.once("dialog", lambda d: d.accept())                                   # Confirmar
    pagina.locator("tr", has_text="Descartável").locator("button:has-text('Excluir')").click()
    expect(pagina.locator(".alert.ok")).to_contain_text("Faixa “Descartável” excluída.")
    expect(pagina.locator(".empty")).to_contain_text("Sua biblioteca está vazia.")


# --------------------------------------------------------------------------- CTS-10
@pytest.mark.evidencia("CTS-10-faixa-em-uso-nao-exclui")
def test_cts10_faixa_em_setlist_nao_pode_ser_excluida(pagina, servidor, entrar):
    entrar(pagina)
    pagina.goto(servidor + "/faixas/?q=Maré")
    pagina.once("dialog", lambda d: d.accept())
    pagina.locator("tr", has_text="Maré Alta").locator("button:has-text('Excluir')").click()
    alerta = pagina.locator(".alert.bad")
    expect(alerta).to_contain_text("Não é possível excluir")
    expect(alerta).to_contain_text("“Rascunho: precisa revisar”, “Warm-up até o pico”")
    expect(pagina.locator("tbody")).to_contain_text("Maré Alta")


# --------------------------------------------------------------------------- CTS-11
@pytest.mark.evidencia("CTS-11-exportar-csv")
def test_cts11_exportar_setlist_em_csv(pagina, servidor, entrar):
    entrar(pagina)
    pagina.goto(servidor + "/setlists/")
    pagina.click("text=Rascunho: precisa revisar")
    with pagina.expect_download() as info:
        pagina.click("text=Exportar CSV")
    download = info.value
    assert download.suggested_filename == "rascunho--precisa-revisar.csv"
    texto = Path(download.path()).read_text(encoding="utf-8-sig")
    linhas = list(csv.reader(io.StringIO(texto), delimiter=";"))
    assert linhas[0][:2] == ["posicao", "titulo"]
    assert [l[1] for l in linhas[1:]] == ["Garoa Paulista", "Aurora Boreal", "Funk do Satélite",
                                         "Céu de Néon", "Maré Alta"]
    assert [l[7] for l in linhas[1:]] == ["Suave", "Arriscada", "Atenção", "Arriscada", ""]


# --------------------------------------------------------------------------- CTS-12
@pytest.mark.evidencia("CTS-12-roda-de-camelot")
def test_cts12_roda_de_camelot_interativa(pagina, servidor, entrar):
    entrar(pagina)
    pagina.get_by_role("link", name="Roda de Camelot").click()
    roda = pagina.locator("#roda-camelot svg")
    expect(roda.locator("a")).to_have_count(24)
    roda.locator("a[aria-label='Tom 12B']").click()
    expect(pagina).to_have_url(re.compile(r"tom=12B"))
    expect(pagina.locator("main")).to_contain_text("Combina com 12B: 12B, 11B, 1B, 12A")


# --------------------------------------------------------------------------- CTS-13
@pytest.mark.evidencia("CTS-13-celular")
def test_cts13_layout_no_celular(navegador, servidor):
    contexto = navegador.new_context(viewport={"width": 360, "height": 740}, is_mobile=True,
                                     has_touch=True, device_scale_factor=2)
    pg = contexto.new_page()
    pg.goto(servidor + "/login")
    pg.fill("#f-email", "demo@harmonimix.dev")
    pg.fill("#f-senha", "Demo1234")
    pg.click("button[type=submit]")
    for url in ("/painel", "/faixas/", "/faixas/nova", "/faixas/importar", "/setlists/", "/setlists/1",
                "/setlists/2?busca=a", "/eventos/", "/eventos/novo", "/ajuda/camelot"):
        pg.goto(servidor + url)
        largura_conteudo = pg.evaluate("document.documentElement.scrollWidth")
        assert largura_conteudo <= 360, f"{url}: rolagem horizontal ({largura_conteudo}px > 360px)"   # RNF05
    expect(pg.locator("nav.nav")).to_be_visible()
    pg.screenshot(path=str(Path(__file__).resolve().parents[1] / "evidencias" / "CTS-13-celular.png"), full_page=True)
    contexto.close()


# --------------------------------------------------------------------------- CTS-14
@pytest.mark.evidencia("CTS-14-isolamento-entre-usuarios")
def test_cts14_usuario_nao_ve_dados_de_outro(pagina, servidor):
    nova_conta(pagina, servidor)
    pagina.goto(servidor + "/setlists/1")              # setlist da conta de demonstração
    expect(pagina.locator("h1")).to_have_text("Página não encontrada")
    pagina.goto(servidor + "/faixas/")
    expect(pagina.locator("main")).not_to_contain_text("Aurora Boreal")


# --------------------------------------------------------------------------- CTS-15
@pytest.mark.evidencia("CTS-15-xss")
def test_cts15_texto_malicioso_nao_executa(pagina, servidor):
    nova_conta(pagina, servidor)
    dialogos = []
    pagina.on("dialog", lambda d: (dialogos.append(d.message), d.dismiss()))
    cadastrar_faixa(pagina, servidor, "<img src=x onerror=alert('xss')>", "Hacker", 120, "8A")
    pagina.goto(servidor + "/setlists/")
    pagina.fill("#f-nome", "<script>alert('xss')</script>")
    pagina.click("button:has-text('Criar e abrir editor')")
    pagina.fill("input[name=busca]", "img")
    pagina.click("button:has-text('Buscar')")
    pagina.locator(".sug").first.locator("button").click()
    pagina.wait_for_timeout(300)
    assert dialogos == [], f"Código injetado foi executado: {dialogos}"
    expect(pagina.locator("h1")).to_have_text("<script>alert('xss')</script>")   # aparece como texto


# --------------------------------------------------------------------------- CTS-16
@pytest.mark.evidencia("CTS-16-acessibilidade")
def test_cts16_campos_tem_rotulo_e_status_tem_texto(pagina, servidor, entrar):
    entrar(pagina)
    for url in ("/faixas/nova", "/faixas/", "/setlists/", "/eventos/novo", "/setlists/2"):
        pagina.goto(servidor + url)
        sem_rotulo = pagina.evaluate("""() => [...document.querySelectorAll(
              'input:not([type=hidden]):not([type=submit]), select, textarea')]
            .filter(el => !(el.labels && el.labels.length) && !el.getAttribute('aria-label'))
            .map(el => el.name)""")
        assert sem_rotulo == [], f"{url}: campos sem rótulo {sem_rotulo}"                # RNF06
    badges = pagina.locator(".trans .badge").all_inner_texts()
    assert badges and all(re.search(r"(Suave|Atenção|Arriscada)", b) for b in badges)   # cor + texto
