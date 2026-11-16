# 🌐 Publicar o HarmoniMix na internet (para os testadores acessarem)

A Situação 3 pede que os colegas recebam **um endereço** para testar. A opção mais simples e gratuita para Flask é o
**PythonAnywhere**. Ele roda Python, tem MySQL incluso e não exige cartão de crédito.

> Os nomes dos botões podem mudar um pouco com o tempo. Em caso de dúvida, consulte a ajuda do próprio site
> ("Flask" na documentação do PythonAnywhere).

## Passo a passo

### 1. Criar a conta
Acesse **pythonanywhere.com** e crie uma conta gratuita (*Beginner*). O seu endereço será
`https://SEU_USUARIO.pythonanywhere.com`.

### 2. Baixar o projeto do GitHub
No painel, abra **Consoles → Bash** e rode (troque `SEU_GITHUB` pelo seu usuário):

```bash
git clone https://github.com/SEU_GITHUB/harmonimix.git
```

```bash
cd harmonimix/situacao-2-desenvolvimento
```

```bash
python3.10 -m venv ~/venv-harmonimix
```

```bash
source ~/venv-harmonimix/bin/activate
```

```bash
pip install -r requirements.txt
```

> Se o PythonAnywhere oferecer uma versão mais nova do Python (3.11, 3.12…), pode usá-la no lugar de `python3.10`.
> Use a mesma versão no passo 3.

### 3. Criar o aplicativo web
1. Aba **Web → Add a new web app → Manual configuration** (não escolha "Flask", que cria um projeto vazio) → mesma versão do Python.
2. Em **Virtualenv**, informe: `/home/SEU_USUARIO/venv-harmonimix`
3. Em **Source code**, informe: `/home/SEU_USUARIO/harmonimix/situacao-2-desenvolvimento`
4. Clique no link do **WSGI configuration file**, apague o conteúdo e cole:

```python
import os
import sys

projeto = "/home/SEU_USUARIO/harmonimix/situacao-2-desenvolvimento"
if projeto not in sys.path:
    sys.path.insert(0, projeto)

os.environ["SECRET_KEY"] = "troque-por-uma-frase-longa-e-aleatoria"
# Opcional, para usar MySQL em vez de SQLite (ver passo 5):
# os.environ["DATABASE_URL"] = "mysql+pymysql://SEU_USUARIO:SENHA@SEU_USUARIO.mysql.pythonanywhere-services.com/SEU_USUARIO$harmonimix?charset=utf8mb4"

from run import app as application
```

5. Em **Static files**, adicione: URL `/static/` → Directory `/home/SEU_USUARIO/harmonimix/situacao-2-desenvolvimento/app/static`

### 4. Criar o banco e a conta de demonstração
De volta ao console Bash (com o ambiente virtual ativado, como no passo 2):

```bash
cd ~/harmonimix/situacao-2-desenvolvimento
```

```bash
flask --app run init-db
```

```bash
flask --app run seed-demo
```

Na aba **Web**, clique em **Reload**. Pronto: abra `https://SEU_USUARIO.pythonanywhere.com` e entre com
`demo@harmonimix.dev` / `Demo1234`.

### 5. (Opcional) Usar MySQL
O SQLite funciona bem para o teste com 5 pessoas. Se o(a) tutor(a) exigir MySQL também na publicação:
1. Aba **Databases**: defina uma senha e crie o banco `harmonimix` (o nome final fica `SEU_USUARIO$harmonimix`).
2. No console MySQL dessa aba, rode o conteúdo de `situacao-1-planejamento/sql/01_schema_mysql.sql` **sem** as linhas
   `DROP DATABASE`, `CREATE DATABASE` e `USE`, porque o banco já existe. Depois rode `02_dados_iniciais.sql` sem a linha `USE`.
3. Descomente a linha `DATABASE_URL` no arquivo WSGI, coloque a sua senha e clique em **Reload**.

## Atualizar depois de uma correção

Depois de corrigir algo e enviar para o GitHub (`git push`), no console do PythonAnywhere rode:

```bash
cd ~/harmonimix && git pull
```

Depois clique em **Reload** na aba Web.

## Problemas comuns

| Sintoma | Solução |
|---------|---------|
| "Something went wrong" / erro 500 | Aba **Web → Error log**: a última linha mostra o erro (geralmente um caminho errado no arquivo WSGI) |
| Página sem estilo (tudo branco) | Confira o mapeamento de **Static files** (passo 3.5) |
| "ModuleNotFoundError: flask" | O campo **Virtualenv** não aponta para `venv-harmonimix`, ou o `pip install` não foi feito com o ambiente ativado |
| O site saiu do ar depois de alguns meses | Contas gratuitas precisam ser renovadas periodicamente pelo botão no painel Web |

## Alternativa sem publicar

Se não for possível publicar, cada testador pode rodar o sistema no próprio computador seguindo o
[README da Situação 2](../situacao-2-desenvolvimento/README.md). Isso exige ter o Python instalado, então só vale
para colegas de TI. Também dá para fazer a sessão de teste presencialmente, no seu computador.
