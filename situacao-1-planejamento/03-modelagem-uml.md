# 3. Modelagem UML: HarmoniMix

> Os diagramas estão em **Mermaid**, formato que o GitHub desenha automaticamente ao abrir este arquivo.
> Documento de Planejamento: versão 2.0.

---

## 3.1 Diagrama de Casos de Uso

> O Mermaid não tem uma notação própria de casos de uso. Por isso usamos a convenção: **atores** à esquerda,
> **casos de uso** em formato oval dentro da fronteira do sistema, e setas `<<include>>` e `<<extend>>` pontilhadas.

```mermaid
flowchart LR
    V["🧍 Visitante"]
    DJ["🎧 DJ<br/>(usuário autenticado)"]

    subgraph S["Sistema HarmoniMix"]
        UC01([UC01 Criar conta])
        UC02([UC02 Autenticar-se])
        UC03([UC03 Manter faixas])
        UC04([UC04 Buscar/filtrar faixas])
        UC05([UC05 Manter eventos])
        UC06([UC06 Manter setlists])
        UC07([UC07 Adicionar faixa ao setlist])
        UC08([UC08 Remover/reordenar faixas])
        UC09([UC09 Sugerir próxima faixa])
        UC10([UC10 Analisar transições])
        UC11([UC11 Visualizar curva de energia])
        UC12([UC12 Importar faixas CSV])
        UC13([UC13 Exportar setlist])
        VAL([Validar compatibilidade<br/>harmônica])
    end

    V --- UC01
    V --- UC02
    DJ --- UC03
    DJ --- UC04
    DJ --- UC05
    DJ --- UC06
    DJ --- UC07
    DJ --- UC08
    DJ --- UC10
    DJ --- UC11
    DJ --- UC12
    DJ --- UC13

    UC09 -. "&lt;&lt;extend&gt;&gt;" .-> UC07
    UC09 -. "&lt;&lt;include&gt;&gt;" .-> VAL
    UC10 -. "&lt;&lt;include&gt;&gt;" .-> VAL
    UC12 -. "&lt;&lt;extend&gt;&gt;" .-> UC03
```

**Herança de atores:** o *DJ* é um *Visitante* que já se autenticou. Todos os casos de uso do DJ exigem o UC02.

### 3.1.1 Descrição dos principais casos de uso

#### UC03: Manter faixas
| Item | Descrição |
|------|-----------|
| **Ator** | DJ |
| **Pré-condição** | Usuário autenticado |
| **Fluxo principal** | 1. O DJ acessa **Biblioteca** → **Nova faixa**. 2. O sistema exibe o formulário (título, artista, BPM, tom, gênero, energia, duração mm:ss). 3. O DJ preenche e salva. 4. O sistema valida (RN02–RN05), grava e exibe "Faixa cadastrada com sucesso". |
| **Fluxos alternativos** | **A1. Editar:** o DJ escolhe uma faixa → *Editar* → altera → salva. **A2. Excluir:** o DJ escolhe *Excluir* → o sistema pede confirmação → exclui. |
| **Exceções** | **E1.** Dados inválidos → o formulário é reexibido com os dados digitados e a mensagem ao lado do campo (MSG03–MSG07). **E2.** Faixa duplicada → MSG08. **E3.** Faixa usada em setlist → exclusão bloqueada, com a lista dos setlists (MSG09). |
| **Pós-condição** | Faixa gravada, alterada ou excluída da biblioteca do DJ |

#### UC07: Adicionar faixa ao setlist (com extensão UC09: Sugerir próxima faixa)
| Item | Descrição |
|------|-----------|
| **Ator** | DJ |
| **Pré-condição** | Usuário autenticado; setlist existente; ao menos uma faixa cadastrada |
| **Fluxo principal** | 1. O DJ abre o **Editor de setlist**. 2. O sistema exibe as faixas do set, a análise das transições e o painel **Sugestões**. 3. O DJ escolhe uma faixa (pela busca ou pelas sugestões) → **Adicionar**. 4. O sistema verifica a duplicidade (RN10), insere a faixa na última posição e recalcula a análise, a pontuação e o gráfico. |
| **Extensão (UC09)** | No passo 2, se o setlist já tiver ao menos uma faixa, o sistema calcula as sugestões compatíveis com a **última faixa** (RN11) e mostra o grau de compatibilidade de cada uma (ex.: "8A → 9A · vizinho · +2,1% BPM"). Se não houver compatíveis: MSG12. |
| **Exceções** | **E1.** Faixa já está no setlist → MSG10. **E2.** Setlist de outro usuário → erro 404. |
| **Pós-condição** | Faixa adicionada ao final do setlist e análise atualizada |

#### UC10: Analisar transições
| Item | Descrição |
|------|-----------|
| **Ator** | DJ |
| **Fluxo principal** | 1. O DJ abre o setlist. 2. Para cada par de faixas consecutivas, o sistema aplica RN06–RN08 e mostra 🟢/🟡/🔴 com o motivo (ex.: "Tom incompatível: 8A → 3B"). 3. O sistema exibe a pontuação harmônica (RN09). |
| **Exceção** | Setlist com menos de 2 faixas → "Adicione pelo menos 2 faixas para analisar as transições." |

---

## 3.2 Diagrama de Classes de Domínio (persistência)

Classes que serão **persistidas** no banco de dados. Este diagrama é a base dos projetos conceitual, lógico e físico
([04-banco-de-dados.md](04-banco-de-dados.md)).

```mermaid
classDiagram
    direction LR

    class Usuario {
        -int id
        -str nome
        -str nome_artistico
        -str email
        -str senha_hash
        -datetime criado_em
        +definir_senha(senha: str) void
        +verificar_senha(senha: str) bool
    }

    class TomCamelot {
        -str codigo
        -int numero
        -str modo
        -str nome_musical
        +eh_compativel(outro: TomCamelot) bool
        +vizinhos() list~str~
    }

    class Genero {
        -int id
        -str nome
    }

    class Faixa {
        -int id
        -str titulo
        -str artista
        -Decimal bpm
        -int energia
        -int duracao_seg
        -datetime criado_em
        +duracao_formatada() str
    }

    class Evento {
        -int id
        -str nome
        -date data_evento
        -str local
    }

    class Setlist {
        -int id
        -str nome
        -str descricao
        -datetime criado_em
        -datetime atualizado_em
        +duracao_total() int
        +pontuacao_harmonica() float
    }

    class ItemSetlist {
        -int posicao
    }

    Usuario "1" --> "0..*" Faixa : possui
    Usuario "1" --> "0..*" Evento : organiza
    Usuario "1" --> "0..*" Setlist : cria
    Faixa "0..*" --> "1" TomCamelot : está no tom
    Faixa "0..*" --> "0..1" Genero : classificada em
    Evento "0..1" o-- "0..*" Setlist : agrega
    Setlist "1" *-- "0..*" ItemSetlist : compõe
    ItemSetlist "0..*" --> "1" Faixa : referencia
```

**Leitura dos relacionamentos:**
- **Composição** (`*--`) entre *Setlist* e *ItemSetlist*: o item não existe sem o setlist (RN13: exclusão em cascata).
- **Agregação** (`o--`) entre *Evento* e *Setlist*: o setlist continua existindo se o evento for excluído (RN14).
- *ItemSetlist* é a **classe associativa** que resolve o relacionamento N:N entre *Setlist* e *Faixa* e guarda a **posição**.

---

## 3.3 Diagrama de Classes de Projeto (arquitetura MVC)

Mostra como o código será organizado na Situação 2, separando **Model**, **View** e **Controller**,
mais uma camada de **Serviço**, que concentra as regras de negócio. Isso deixa as regras fáceis de testar sem precisar
do navegador nem do banco.

```mermaid
classDiagram
    direction TB

    namespace Controllers {
        class AuthController {
            +cadastro()
            +login()
            +logout()
        }
        class FaixaController {
            +listar()
            +nova()
            +editar(id)
            +excluir(id)
        }
        class SetlistController {
            +listar()
            +novo()
            +abrir(id)
            +adicionar_faixa(id)
            +remover_item(id, pos)
            +mover_item(id, pos, direcao)
        }
        class EventoController {
            +listar()
            +novo()
            +editar(id)
            +excluir(id)
        }
    }

    namespace Services {
        class HarmoniaService {
            +tons_compativeis(a, b) bool
            +tipo_compatibilidade(a, b) str
            +variacao_bpm(bpm1, bpm2) float
            +classificar_transicao(f1, f2) Transicao
            +analisar_setlist(faixas) Analise
            +sugerir_proximas(ultima, candidatas) list
        }
        class ValidacaoService {
            +validar_faixa(dados) dict
            +validar_usuario(dados) dict
        }
    }

    namespace Models {
        class Faixa
        class Setlist
        class ItemSetlist
        class Usuario
        class Evento
    }

    namespace Views {
        class Templates {
            biblioteca.html
            faixa_form.html
            setlist_editor.html
            ...
        }
    }

    FaixaController ..> ValidacaoService
    FaixaController ..> Faixa
    SetlistController ..> HarmoniaService
    SetlistController ..> Setlist
    SetlistController ..> ItemSetlist
    AuthController ..> Usuario
    EventoController ..> Evento
    FaixaController ..> Templates : render
    SetlistController ..> Templates : render
```

---

## 3.4 Diagrama de Sequência: abrir o editor e adicionar uma faixa sugerida (UC07 + UC09)

```mermaid
sequenceDiagram
    autonumber
    actor DJ
    participant V as View (navegador)
    participant C as SetlistController
    participant H as HarmoniaService
    participant M as Model (SQLAlchemy)
    participant DB as MySQL

    DJ->>V: Abre "Editor de setlist"
    V->>C: GET /setlists/7
    C->>M: buscar setlist 7 do usuário logado
    M->>DB: SELECT ... WHERE id=7 AND id_usuario=?
    DB-->>M: setlist + itens + faixas
    alt setlist não pertence ao usuário
        C-->>V: 404 "Setlist não encontrado"
    else setlist encontrado
        C->>H: analisar_setlist(faixas)
        H-->>C: transições 🟢🟡🔴 + pontuação
        C->>M: faixas do usuário fora do setlist
        M-->>C: candidatas
        C->>H: sugerir_proximas(ultima_faixa, candidatas)
        H-->>C: até 10 sugestões ordenadas
        C-->>V: render setlist_editor.html
        V-->>DJ: Exibe set, análise, gráfico e sugestões
    end

    DJ->>V: Clica "Adicionar" em uma sugestão
    V->>C: POST /setlists/7/itens {id_faixa: 42}
    C->>M: faixa 42 já está no setlist?
    alt duplicada
        C-->>V: redirect + MSG10 "Esta faixa já está no setlist"
    else ok
        C->>M: INSERT ItemSetlist(posicao = n+1)
        M->>DB: INSERT
        C-->>V: redirect + MSG11 "Faixa adicionada"
        V-->>DJ: Editor atualizado (nova análise e gráfico)
    end
```

---

## 3.5 Diagrama de Sequência: cadastrar faixa (UC03)

```mermaid
sequenceDiagram
    autonumber
    actor DJ
    participant V as View
    participant C as FaixaController
    participant VS as ValidacaoService
    participant M as Model
    DJ->>V: Preenche formulário e clica "Salvar"
    V->>C: POST /faixas/nova
    C->>VS: validar_faixa(dados)
    alt há erros
        VS-->>C: {bpm: "O BPM deve estar entre 60 e 200"}
        C-->>V: reexibe o formulário com erros + dados digitados
    else válido
        C->>M: existe título+artista para este usuário?
        alt duplicada
            C-->>V: MSG08
        else nova
            C->>M: INSERT Faixa
            C-->>V: redirect /faixas + "Faixa cadastrada com sucesso"
        end
    end
```

---

## 3.6 Diagrama de Atividades: montar um setlist

```mermaid
flowchart TD
    A([Início]) --> B[DJ cria um novo setlist]
    B --> C{Vincular a um evento?}
    C -- Sim --> D[Selecionar evento]
    C -- Não --> E
    D --> E[Abrir editor do setlist]
    E --> F{Setlist vazio?}
    F -- Sim --> G[Buscar faixa na biblioteca]
    F -- Não --> H[Sistema calcula sugestões<br/>compatíveis com a última faixa]
    H --> I{Há sugestões?}
    I -- Sim --> J[DJ escolhe uma sugestão]
    I -- Não --> G
    G --> K[DJ escolhe faixa]
    J --> L{Faixa já está no set?}
    K --> L
    L -- Sim --> M[/Exibe MSG10/] --> E
    L -- Não --> N[Adiciona no final do set]
    N --> O[Sistema recalcula transições,<br/>pontuação e curva de energia]
    O --> P{Transição 🔴 Arriscada?}
    P -- Sim --> Q[DJ decide: reordenar,<br/>remover ou manter]
    P -- Não --> R
    Q --> R{Set completo?}
    R -- Não --> E
    R -- Sim --> S([Fim: setlist pronto])
```

---

## 3.7 Diagrama de Atividades: algoritmo de classificação da transição (RN06–RN08)

```mermaid
flowchart TD
    A([Faixa atual X e próxima Y]) --> B{"tom(X) = tom(Y)?"}
    B -- Sim --> T1[tom OK · 'mesmo tom']
    B -- Não --> C{"mesma letra e<br/>números vizinhos?<br/>(12 ↔ 1)"}
    C -- Sim --> T2[tom OK · 'vizinho']
    C -- Não --> D{"mesmo número e<br/>letra diferente?"}
    D -- Sim --> T3[tom OK · 'relativo']
    D -- Não --> T4[tom incompatível]
    T1 & T2 & T3 & T4 --> E["Δ% = |BPM_Y − BPM_X| ÷ BPM_X × 100"]
    E --> F{"Δ% ≤ 6?"}
    F -- Sim --> G[BPM OK]
    F -- Não --> H[BPM fora]
    G & H --> I{Quantos critérios OK?}
    I -- 2 --> V([🟢 Suave])
    I -- 1 --> AM([🟡 Atenção])
    I -- 0 --> VM([🔴 Arriscada])
```
