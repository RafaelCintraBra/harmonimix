# 🔧 Registro de correções e melhorias

Histórico de **todos** os defeitos encontrados e das melhorias adotadas, de qualquer origem: testes automatizados,
revisão de código ou testadores. Nenhuma falha foi escondida: elas mostram o processo de melhoria contínua.

## 1. Encontrados pelos testes (Situações 2 e 3)

| ID | Origem | Defeito | Correção | Arquivo(s) | Commit |
|----|--------|---------|----------|------------|--------|
| D01 | Teste de integração | Número da linha errado nos erros de importação de CSV com linhas em branco | Usar `leitor.line_num` | `app/services/csv_service.py` | Situação 2 |
| D02 | Teste de integração | Excluir usuário com setlists falhava (ordem de exclusão × RN12) | Excluir setlists antes do usuário | `app/seed.py` | Situação 2 |
| D03 | Teste no **MySQL** | Reordenar faixas estourava `SMALLINT` (posição temporária 65000) | Posição temporária = maior posição + 1 | `app/services/setlist_service.py` | Situação 2 |
| D04 | Execução | SQLite sem autoincremento em `genero.id_genero` (`SMALLINT`) | `SmallInteger().with_variant(Integer, "sqlite")` | `app/models/dominio.py` | Situação 2 |
| D05 | Revisão de segurança | Títulos inseridos no gráfico via `innerHTML` sem escape (XSS) | Função `esc()` + teste CTS-15 | `app/static/js/app.js` | Situação 2 |
| D06 | Teste de sistema CTS-13 | Rolagem horizontal em todas as páginas no celular (até 656 px em tela de 360 px) | `minmax(0,1fr)` e `min-width:0` na grade | `app/static/css/style.css`, protótipo | Situação 3 |
| D07 | Teste de sistema CTS-13 | Páginas com tabela ainda rolavam: o rótulo invisível "Ações" escapava da área rolável | `.table-wrap{position:relative}` | `app/static/css/style.css` | Situação 3 |

## 2. Vindos dos testadores (teste de aceitação)

> ⚠️ **Preencher depois de receber os 5 formulários.** Use o ID da tabela 3.4 de
> [VALIDACAO-COM-USUARIOS.md](../VALIDACAO-COM-USUARIOS.md) (F01, F02…).

| ID | Relatado por | Problema / sugestão | Decisão | O que foi feito (antes → depois) | Arquivo(s) | Teste que garante |
|----|--------------|---------------------|---------|----------------------------------|------------|-------------------|
| F01 | | | | | | |
| F02 | | | | | | |
| F03 | | | | | | |

### Modelo de registro detalhado (copie para cada correção importante)

```
### F0X: [título curto]
- Relatado por: [testador] em [data], tarefa [T?], gravidade [A/M/B]
- O que acontecia: [descrição + print "antes" em ../evidencias/F0X-antes.png]
- Causa: [o que estava errado no código ou na interface]
- Correção: [o que mudou]
- Como foi verificado: [teste automatizado criado/ajustado + print "depois" em ../evidencias/F0X-depois.png]
```

## 3. Itens não adotados / trabalhos futuros

| ID | Sugestão | Motivo |
|----|----------|--------|
| — | Detectar BPM e tom automaticamente a partir do arquivo de áudio | Fora do escopo definido na Situação 1 (seção 1.7); o Rekordbox já faz isso e o sistema importa a análise dele |
| — | Integração direta com o Spotify | Fora do escopo; a API do Spotify não fornece mais BPM/tom para aplicativos novos e a playlist pode ser trazida via Rekordbox/CSV |
