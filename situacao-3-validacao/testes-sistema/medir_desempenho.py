"""Mede o tempo de resposta das telas principais com uma biblioteca grande (RNF07: até 1 s).

Uso (a partir desta pasta):  python medir_desempenho.py
Gera ../evidencias/desempenho.txt
"""
import random
import statistics
import sys
import tempfile
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "situacao-2-desenvolvimento"))

from app import create_app                                   # noqa: E402
from app.extensions import db                                # noqa: E402
from app.models import Faixa, ItemSetlist, Setlist, Usuario  # noqa: E402
from config import TestConfig                                # noqa: E402

QTD_FAIXAS, QTD_NO_SET, REPETICOES = 2000, 30, 7


def main():
    pasta = tempfile.mkdtemp()

    class Config(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{pasta}/desempenho.db"

    app = create_app(Config)
    aleatorio = random.Random(42)
    with app.app_context():
        u = Usuario(nome="Desempenho", email="perf@teste.com")
        u.definir_senha("Senha123")
        db.session.add(u)
        db.session.flush()
        tons = [f"{n}{m}" for n in range(1, 13) for m in "AB"]
        faixas = [Faixa(id_usuario=u.id, titulo=f"Faixa {i:04d}", artista=f"Artista {i % 150}",
                        bpm=Decimal(aleatorio.randint(9000, 14000)) / 100, cod_tom=aleatorio.choice(tons),
                        energia=aleatorio.randint(1, 10), duracao_seg=aleatorio.randint(150, 480))
                  for i in range(QTD_FAIXAS)]
        db.session.add_all(faixas)
        db.session.flush()
        s = Setlist(id_usuario=u.id, nome="Set grande")
        db.session.add(s)
        db.session.flush()
        for pos, f in enumerate(aleatorio.sample(faixas, QTD_NO_SET), start=1):
            db.session.add(ItemSetlist(id_setlist=s.id, posicao=pos, id_faixa=f.id))
        db.session.commit()
        id_set = s.id

    cliente = app.test_client()
    cliente.post("/login", data={"email": "perf@teste.com", "senha": "Senha123"})
    medidas = {
        "Listar biblioteca (página 1, 2.000 faixas)": "/faixas/",
        "Filtrar biblioteca (BPM 120–128 + busca)": "/faixas/?q=Artista 1&bpm_min=120&bpm_max=128",
        f"Abrir editor (set de {QTD_NO_SET} faixas + sugestões entre {QTD_FAIXAS - QTD_NO_SET})": f"/setlists/{id_set}",
        "Painel": "/painel",
    }
    linhas = [f"Medição de desempenho (RNF07) · {datetime.now():%d/%m/%Y %H:%M}",
              f"Biblioteca: {QTD_FAIXAS} faixas · SQLite · mediana de {REPETICOES} requisições", ""]
    aprovado = True
    for nome, url in medidas.items():
        cliente.get(url)  # aquecimento
        tempos = []
        for _ in range(REPETICOES):
            inicio = time.perf_counter()
            resposta = cliente.get(url)
            tempos.append((time.perf_counter() - inicio) * 1000)
            assert resposta.status_code == 200, (url, resposta.status_code)
        mediana = statistics.median(tempos)
        ok = mediana <= 1000
        aprovado &= ok
        linhas.append(f"{'OK ' if ok else 'FALHOU'}  {mediana:7.1f} ms  (máx. {max(tempos):7.1f} ms)  {nome}")
    linhas += ["", "Meta: até 1000 ms por tela · Resultado: " + ("APROVADO" if aprovado else "REPROVADO")]
    texto = "\n".join(linhas)
    saida = RAIZ / "situacao-3-validacao" / "evidencias" / "desempenho.txt"
    saida.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    with app.app_context():
        db.engine.dispose()


if __name__ == "__main__":
    main()
