# 1. Escopo do Projeto: HarmoniMix

> **Projeto Integrador Transdisciplinar em Engenharia de Software II**
> Documento de Planejamento: versão 2.0 (revisada). Veja o [histórico de revisões](07-historico-revisoes.md).

---

## 1.1 Contexto

O DJ é o profissional responsável por conduzir a pista de dança de um evento por meio de uma sequência
de músicas (o **setlist**). A qualidade de uma apresentação depende muito das **transições** entre as
faixas: quando duas músicas em sequência têm **tonalidades** incompatíveis ou **andamentos (BPM)** muito
diferentes, a mixagem soa "desafinada" ou "atropelada" e a pista perde energia.

Para resolver isso, DJs profissionais usam a técnica de **mixagem harmônica**, apoiada na
**Roda de Camelot**, um sistema que codifica as 24 tonalidades musicais em códigos de **1A a 12B**:

- os **números (1 a 12)** formam um círculo, em que tons vizinhos são harmonicamente compatíveis;
- as **letras** indicam o modo: **A = menor**, **B = maior**;
- uma faixa em **8A** (Lá menor) combina com **8A**, **7A**, **9A** e **8B** (Dó maior, a sua relativa).

## 1.2 Problema

Hoje o DJ iniciante ou autônomo:

1. mantém a sua biblioteca de músicas espalhada em pastas e planilhas, sem informações padronizadas de BPM e tom;
2. monta setlists "de cabeça" ou por tentativa e erro, testando no fone quais músicas combinam;
3. não tem uma visão clara da **curva de energia** do set (se ele começa calmo, cresce e termina no pico);
4. descobre transições ruins só durante a apresentação, na frente do público.

As ferramentas profissionais que resolvem parte disso são pagas, em inglês e focadas em análise de áudio,
não no **planejamento** do set.

## 1.3 Solução proposta

O **HarmoniMix** é uma **aplicação web** em que o DJ:

- cadastra a sua **biblioteca de faixas** com BPM, tom (Camelot), gênero, energia e duração;
- cria **setlists**, opcionalmente vinculados a um **evento** (festa, casamento, formatura…);
- recebe **sugestões automáticas** da próxima faixa compatível em tom e BPM;
- vê a **análise de cada transição**, classificada como 🟢 **Suave**, 🟡 **Atenção** ou 🔴 **Arriscada**;
- acompanha a **curva de energia** do set num gráfico (BPM e energia ao longo do tempo) e a duração total.

## 1.4 Objetivos

### Objetivo geral
Apoiar DJs no **planejamento de setlists harmonicamente coerentes**, reduzindo transições ruins e o tempo
gasto na preparação de apresentações.

### Objetivos específicos
| # | Objetivo | Indicador de sucesso |
|---|----------|----------------------|
| OE1 | Centralizar a biblioteca de faixas do DJ | CRUD completo de faixas, com busca e filtros |
| OE2 | Automatizar a verificação de compatibilidade | 100% das transições do set classificadas automaticamente |
| OE3 | Sugerir faixas compatíveis | Sugestões geradas em até 1 segundo |
| OE4 | Dar visibilidade à curva de energia | Gráfico de BPM e energia por posição no set |
| OE5 | Garantir qualidade | Regras de negócio cobertas por testes automatizados (pytest) |

## 1.5 Partes interessadas (stakeholders)

| Parte interessada | Interesse no sistema |
|-------------------|----------------------|
| **DJ (usuário principal)** | Organizar a biblioteca, montar setlists e evitar transições ruins |
| **Contratante do evento** | Receber uma apresentação de qualidade (beneficiário indireto) |
| **Tutor(a) e professores** | Avaliar o projeto acadêmico |
| **Colegas testadores** | Validar a solução (Situação 3) |
| **Desenvolvedor(a), o(a) autor(a)** | Construir, manter e usar o projeto como portfólio |

## 1.6 Persona

> **Lucas, 24 anos, DJ de festas e eventos sociais**
> Toca em aniversários, formaturas e bares aos fins de semana. Tem cerca de 400 músicas no notebook
> e usa uma controladora de entrada. Sabe que "existe um negócio de tom", mas não domina teoria musical.
> **Dor:** já errou transições ao vivo e perdeu a pista.
> **Desejo:** "Queria abrir o computador e o sistema me dizer *qual música entra depois desta*."

## 1.7 Escopo

### ✅ Dentro do escopo (MVP)
1. Cadastro e autenticação de usuários (DJs)
2. CRUD de faixas: título, artista, BPM, tom Camelot, gênero, energia (1–10) e duração
3. Busca e filtro de faixas (texto, gênero, tom, faixa de BPM)
4. CRUD de eventos (nome, data, local)
5. CRUD de setlists, com vínculo opcional a um evento
6. Adicionar, remover e reordenar faixas no setlist
7. **Sugestão da próxima faixa** (algoritmo da Roda de Camelot + tolerância de BPM)
8. **Análise de transições** (Suave / Atenção / Arriscada) e **pontuação harmônica** do set
9. **Curva de energia** (gráfico) e **duração total** do set
10. Tela de ajuda explicando a Roda de Camelot

### ➕ Desejável (se houver tempo)
- Importar faixas por arquivo **CSV**
- Exportar o setlist (CSV / impressão)

### ❌ Fora do escopo
- Reprodução ou mixagem de áudio (o sistema **planeja**, não toca)
- **Detecção automática** de BPM ou tom a partir do arquivo de áudio
- Integração com Spotify, Beatport ou softwares de DJ (Rekordbox, Serato)
- Aplicativo mobile nativo (a interface web será **responsiva**)
- Pagamentos ou contratação de DJs

## 1.8 Premissas e restrições

| Tipo | Descrição |
|------|-----------|
| Premissa | O DJ conhece (ou consulta em outra ferramenta) o BPM e o tom das suas músicas |
| Premissa | Os colegas testadores terão acesso a um navegador moderno |
| Restrição | Projeto individual, com prazo do semestre letivo |
| Restrição | Tecnologias gratuitas e de código aberto |
| Restrição | Back-end no padrão **MVC**, em linguagem indicada pela disciplina (**Python**) |
| Restrição | SGBD popular e de fácil manutenção (**MySQL**) |

## 1.9 Tecnologias

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| Front-end | HTML5, CSS3, JavaScript, Chart.js | Padrão da web; Chart.js para o gráfico de energia |
| Back-end | Python 3 + Flask | Leve, legível e adequado ao padrão MVC |
| Persistência | SQLAlchemy (ORM) | Separa o *Model* do SGBD; permite trocar MySQL por SQLite nos testes |
| Banco de dados | **MySQL 8** (produção) / SQLite (testes) | SGBD popular, gratuito e bem documentado |
| Testes | pytest + pytest-cov | Testes unitários e de integração, com relatório de cobertura |
| Versionamento | Git + GitHub | Portfólio público e documentação centralizada |

## 1.10 Cronograma macro

| Fase | Entregas | Situação |
|------|----------|----------|
| Planejamento | Escopo, requisitos, UML, IHC, banco de dados | Situação 1 |
| Desenvolvimento | Front-end, back-end MVC, testes unitários, manual | Situação 2 |
| Validação | Testes de integração e sistema, teste com 5 pares, correções, vídeo | Situação 3 |
