# 🎧 HarmoniMix

**Montador de setlists com mixagem harmônica para DJs.**

O DJ cadastra a sua biblioteca de músicas com **BPM** e **tom** (Roda de Camelot), monta setlists e o sistema:
- **sugere a próxima faixa** compatível;
- classifica cada transição como 🟢 **Suave**, 🟡 **Atenção** ou 🔴 **Arriscada**;
- mostra a **curva de energia** e a duração total do set.

> Projeto Integrador Transdisciplinar em Engenharia de Software II

![Editor de setlist (protótipo)](situacao-1-planejamento/img/T07-editor.png)

## 📂 Organização do repositório

| Pasta | Conteúdo | Status |
|-------|----------|--------|
| [`situacao-1-planejamento/`](situacao-1-planejamento/) | Escopo, requisitos, UML, IHC e protótipo, banco de dados (conceitual, lógico, físico) e dicionário de dados | ✅ v2.0 |
| [`situacao-2-desenvolvimento/`](situacao-2-desenvolvimento/) | Código-fonte (front-end + back-end MVC), testes, manual de uso | ⏳ |
| [`situacao-3-validacao/`](situacao-3-validacao/) | Plano e relatório de testes, formulário de teste com usuários, feedbacks e correções | ⏳ |

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Front-end | HTML5, CSS3, JavaScript, Chart.js |
| Back-end | Python 3 + Flask (padrão **MVC**) |
| Banco de dados | **MySQL 8** (SQLite nos testes) |
| ORM | SQLAlchemy |
| Testes | pytest + pytest-cov |

## 🗄️ Banco de dados (início rápido)

```bash
mysql -u root -p < situacao-1-planejamento/sql/01_schema_mysql.sql
mysql -u root -p < situacao-1-planejamento/sql/02_dados_iniciais.sql
```

Usuário de demonstração: `demo@harmonimix.dev` / `Demo1234`

## 🎡 O que é a Roda de Camelot?

Um sistema que codifica as 24 tonalidades musicais em códigos de **1A a 12B**. Faixas com o **mesmo código**, com
**números vizinhos** (8A → 7A/9A) ou com o **mesmo número** (8A ↔ 8B) combinam harmonicamente.
