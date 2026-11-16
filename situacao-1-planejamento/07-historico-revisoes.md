# 7. Histórico de Revisões: ciclo de melhoria contínua (Kaizen)

> A Situação 1 pede para revisar o planejamento e torná-lo mais robusto. Este projeto **não tem um PI I anterior**:
> o planejamento foi criado nesta disciplina. Por isso, o ciclo de melhoria foi aplicado sobre a **versão 1.0**
> (a proposta inicial do tema), que gerou a **versão 2.0** (este conjunto de documentos), e segue aberto para as
> críticas dos colegas (seção 7.3).

## 7.1 Versões

| Versão | Descrição |
|--------|-----------|
| 1.0 | Proposta inicial: ideia do HarmoniMix, lista de funcionalidades (MVP), regras de tom e BPM em alto nível e lista de 7 tabelas |
| 2.0 | Planejamento completo e revisado: escopo, requisitos com rastreabilidade, UML, IHC com protótipo, banco conceitual/lógico/físico verificado e dicionário de dados |
| 2.x | *(reservado)* Incorporação das críticas dos colegas |

## 7.2 Alterações da versão 1.0 para a 2.0 (revisão do autor)

| ID | Artefato | Como era (v1.0) | Como ficou (v2.0) | Motivo |
|----|----------|-----------------|-------------------|--------|
| R01 | Requisitos | Classificação "perfeita / aceitável / arriscada" sem critério definido | **Suave / Atenção / Arriscada**, com regra objetiva (RN08: quantos dos 2 critérios foram atendidos) | Requisito precisa ter **um só significado** e ser testável |
| R02 | Requisitos | "Sugerir próxima faixa" sem ordem nem limite | RN11: só faixas do usuário, fora do set, compatíveis em tom **e** BPM, ordenadas por tipo de compatibilidade e diferença de BPM, máx. 10 | Eliminar ambiguidade e permitir teste automatizado |
| R03 | Requisitos | Regras de exclusão não definidas | RN12 (faixa em uso não é excluída), RN13 (setlist exclui itens), RN14 (evento só desvincula setlists) | Faltavam requisitos; detectado ao modelar as FKs |
| R04 | Requisitos / Banco | Sem atributo de energia; "curva de energia" usava só BPM | Atributo **energia (1–10)** na faixa; gráfico com BPM + energia | BPM sozinho não representa a intensidade (ex.: um funk a 130 BPM pode ser mais intenso que um techno a 130) |
| R05 | Escopo | Importar CSV e exportar PDF no MVP | Movidos para **desejável** (RF16/RF17, prioridade *Could*); exportação em CSV | Reduzir o risco de prazo e focar no núcleo (harmonia) |
| R06 | Requisitos | Sem requisitos não funcionais | 11 RNFs (segurança, usabilidade, acessibilidade, desempenho, testabilidade…) com forma de verificação | Qualidade precisa ser **mensurável** |
| R07 | Banco físico | `tom_camelot.numero` como `TINYINT UNSIGNED` | `TINYINT` com sinal + `CHECK (1..12)` | **Defeito encontrado na verificação:** `numero₁ − numero₂` negativo gerava `BIGINT UNSIGNED value is out of range` |
| R08 | Banco / IHC | Setlist de demonstração do banco diferente do mostrado no protótipo | Dados de demonstração iguais aos do protótipo (mesmas faixas, duração 27:17, pontuação 25%) | Consistência entre os artefatos, para facilitar a validação |
| R09 | IHC | Roda de Camelot desenhada com o 1 no topo | **12 no topo**, como no padrão usado por DJs | Usuários que já conhecem a roda estranhariam |
| R10 | IHC | Badges de status quebravam linha; gráfico sem escala de energia | Badges sem quebra; eixo de energia (0–10) à direita do gráfico | Legibilidade |
| R11 | IHC | Busca do editor só mostrava faixas compatíveis | O DJ pode adicionar **qualquer** faixa; se for incompatível, recebe o aviso MSG15 | Princípio do **controle do usuário**: o sistema sugere, não impõe |
| R12 | UML | Sem diagrama de arquitetura | Diagrama de classes de projeto com **MVC + camada de serviços** (`HarmoniaService`) | Preparar a Situação 2 e isolar as regras para teste |

## 7.3 Críticas dos colegas

> ⚠️ **A preencher pelo(a) estudante.** Envie o protótipo ([`prototipo/index.html`](prototipo/index.html)) e o
> [formulário de crítica](formulario-critica-colegas.md) para colegas e registre aqui as sugestões **reais** recebidas,
> inclusive as que você decidiu **não** adotar (e por quê).

| ID | Colega | Data | Sugestão / crítica | Decisão | Justificativa / onde foi aplicada |
|----|--------|------|--------------------|---------|-----------------------------------|
| C01 | | | | ☐ Adotada ☐ Adiada ☐ Não adotada | |
| C02 | | | | ☐ Adotada ☐ Adiada ☐ Não adotada | |
| C03 | | | | ☐ Adotada ☐ Adiada ☐ Não adotada | |
| C04 | | | | ☐ Adotada ☐ Adiada ☐ Não adotada | |
| C05 | | | | ☐ Adotada ☐ Adiada ☐ Não adotada | |
