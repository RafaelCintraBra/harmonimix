# Situação 2: Desenvolvimento

Código-fonte do **HarmoniMix**: front-end (HTML, CSS, JavaScript) e back-end (Python + Flask) no padrão **MVC**,
com testes automatizados e tratamento de erros.

| Entrega pedida | Onde está |
|----------------|-----------|
| Front-end (HTML, CSS, JavaScript) | [`app/templates/`](app/templates/) · [`app/static/`](app/static/) |
| Back-end com design pattern MVC | [`app/models/`](app/models/) · [`app/controllers/`](app/controllers/) · [`app/services/`](app/services/) |
| Linguagem indicada | Python 3 (Flask) |
| Testes (front-end e back-end) e erros tratados | [`tests/`](tests/) · [relatório de testes](docs/RELATORIO-TESTES.md) |
| Bibliotecas | [`requirements.txt`](requirements.txt) (detalhes abaixo) |
| Manual de uso | [docs/MANUAL-DE-USO.md](docs/MANUAL-DE-USO.md) |
| Roteiro do vídeo | [docs/ROTEIRO-VIDEO.md](docs/ROTEIRO-VIDEO.md) |

---

## 🏛️ Arquitetura MVC

```
situacao-2-desenvolvimento/
├── run.py                    ← ponto de entrada
├── config.py                 ← configurações (banco via DATABASE_URL)
├── requirements.txt          ← bibliotecas
├── app/
│   ├── __init__.py           ← fábrica da aplicação, páginas de erro, comandos
│   ├── models/               ← MODEL: tabelas do banco (SQLAlchemy)
│   │   ├── usuario.py  dominio.py  faixa.py  evento.py  setlist.py
│   ├── controllers/          ← CONTROLLER: rotas (Blueprints do Flask)
│   │   ├── auth.py  painel.py  faixas.py  eventos.py  setlists.py  ajuda.py
│   ├── services/             ← regras de negócio (testadas isoladamente)
│   │   ├── harmonia.py       ← algoritmo da Roda de Camelot (RN06–RN11)
│   │   ├── validacao.py      ← validação dos formulários (RN01–RN04)
│   │   ├── setlist_service.py← adicionar, remover, reordenar
│   │   └── csv_service.py    ← importar faixas / exportar setlist
│   ├── templates/            ← VIEW: páginas HTML (Jinja2)
│   └── static/               ← VIEW: css/style.css e js/app.js
├── tests/                    ← 217 testes automatizados (pytest)
├── exemplos/                 ← planilhas CSV para importar
└── docs/                     ← manual, relatório de testes, roteiro do vídeo, prints
```

**Fluxo de uma requisição** (igual à Figura 2 do material da disciplina):

```mermaid
flowchart LR
    U[Usuário] -- requisição HTTP --> R[Router<br/>Flask]
    R --> C[Controller<br/>setlists.py]
    C <--> S[Services<br/>harmonia.py]
    C <--> M[Model<br/>SQLAlchemy]
    M <--> DB[(MySQL)]
    C -- dados --> V[View<br/>editor.html]
    V -- HTML --> U
```

---

## ▶️ Como rodar

### 1. Pré-requisitos
- Python 3.10 ou superior
- (Opcional) MySQL 8. Sem ele, o sistema usa SQLite automaticamente.

### 2. Instalar

```bash
cd situacao-2-desenvolvimento
```

```bash
python -m venv .venv
```

Ative o ambiente virtual. No Windows:

```bash
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 3. Criar o banco e os dados de demonstração

```bash
flask --app run init-db
```

```bash
flask --app run seed-demo
```

### 4. Iniciar

```bash
flask --app run run --debug
```

Acesse **http://127.0.0.1:5000** e entre com `demo@harmonimix.dev` / `Demo1234`, ou crie a sua conta.

### Usando MySQL em vez de SQLite

Crie o banco com o script da Situação 1 e aponte a variável `DATABASE_URL` para ele. No Linux ou macOS:

```bash
mysql -u root -p < ../situacao-1-planejamento/sql/01_schema_mysql.sql
```

```bash
export DATABASE_URL="mysql+pymysql://USUARIO:SENHA@localhost/harmonimix?charset=utf8mb4"
```

No Windows (PowerShell), use `$env:DATABASE_URL="mysql+pymysql://..."`.

---

## 🧪 Testes

```bash
python -m pytest
```

Com relatório de cobertura:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Para rodar os mesmos testes contra um MySQL de teste:

```bash
TEST_DATABASE_URL="mysql+pymysql://USUARIO:SENHA@localhost/harmonimix_test?charset=utf8mb4" python -m pytest
```

**Resultado atual:** 217 testes passando, **cobertura de 99%**, validados em **SQLite** e em **MariaDB 10.11**
(compatível com MySQL). Detalhes em [docs/RELATORIO-TESTES.md](docs/RELATORIO-TESTES.md).

---

## 📚 Bibliotecas

| Biblioteca | Versão | Para quê |
|------------|--------|----------|
| Flask | 3.1.3 | Framework web (rotas, templates, sessão) |
| Flask-SQLAlchemy / SQLAlchemy | 3.1.1 / 2.1.8 | ORM: camada Model, independente do SGBD |
| Flask-WTF | 1.3.0 | Proteção CSRF nos formulários |
| PyMySQL | 1.2.4 | Driver de conexão com o MySQL |
| Werkzeug (vem com o Flask) | 3.1 | Hash de senhas (PBKDF2/scrypt) |
| pytest / pytest-cov | 9.2.0 / 7.1.0 | Testes automatizados e cobertura |

O front-end **não usa bibliotecas externas**: o gráfico da curva de energia e a Roda de Camelot são desenhados em SVG
com JavaScript puro (`app/static/js/app.js`). Assim o sistema funciona até sem internet.
