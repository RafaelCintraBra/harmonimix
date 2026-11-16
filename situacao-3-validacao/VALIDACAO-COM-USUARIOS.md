# 👥 Validação com usuários (teste de aceitação)

> A validação responde: **"o produto atende quem vai usá-lo?"** Não importa o caminho, e sim se o alvo foi atingido.
> Por isso, 5 pessoas que não participaram do desenvolvimento usam o sistema como usuários reais.

## 1. Preparação (checklist)

- [ ] Sistema publicado na internet: siga [PUBLICAR-ONLINE.md](PUBLICAR-ONLINE.md) e anote o endereço
- [ ] Endereço preenchido no formulário ([formulario/Formulario-Teste-HarmoniMix.docx](formulario/Formulario-Teste-HarmoniMix.docx), campo "Endereço do sistema")
- [ ] Testado o login com a conta de demonstração no endereço publicado
- [ ] Escolhidos **5 testadores** (colegas de curso ou profissionais da área), de preferência com perfis diferentes:
      pelo menos 1 que mexa com música/DJ, 1 que use pelo celular e 1 colega de TI
- [ ] Enviado a cada um: **endereço + formulário (.docx) + `modelo-importacao.csv`** (para a tarefa T4)
- [ ] Combinado o prazo de devolução (sugestão: 3 dias)

### Mensagem sugerida para enviar aos testadores

> Oi, [nome]! Estou finalizando o meu Projeto Integrador, o **HarmoniMix**, um sistema para DJs montarem setlists com
> músicas que combinam entre si. Você pode me ajudar testando por uns 20 minutos?
>
> 🔗 Sistema: [ENDEREÇO]
> 👤 Conta de teste: demo@harmonimix.dev / Demo1234 (ou crie a sua)
>
> No formulário em anexo há um roteiro com 12 tarefas. Anote o que funcionou, o que deu errado e o que você não
> conseguiu testar, e cole prints dos erros. Pode ser bem sincero: os problemas que você achar vão me ajudar a melhorar
> o projeto. Depois é só salvar em PDF e me mandar até [DATA]. Muito obrigado! 🎧

## 2. Coleta

Salve cada formulário respondido em [`feedbacks/`](feedbacks/) com o nome `teste-1-NOME.pdf` … `teste-5-NOME.pdf`.
Depois, junte os cinco num único PDF para a entrega (`feedbacks/HarmoniMix-5-testes-de-usuarios.pdf`).

## 3. Consolidação dos resultados

> ⚠️ **Preencher com as respostas REAIS dos testadores.** As tabelas abaixo estão vazias de propósito.

### 3.1 Participantes

| # | Testador(a) | Data | Perfil (curso/área · experiência com DJ) | Dispositivo / navegador |
|---|-------------|------|------------------------------------------|-------------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### 3.2 Resultado por tarefa

Marque ✅ (funcionou), ❌ (não funcionou) ou ➖ (não testou).

| Tarefa | T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|
| Testador 1 | | | | | | | | | | | | |
| Testador 2 | | | | | | | | | | | | |
| Testador 3 | | | | | | | | | | | | |
| Testador 4 | | | | | | | | | | | | |
| Testador 5 | | | | | | | | | | | | |
| **Taxa de sucesso** | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 | /5 |

### 3.3 Avaliação (média de 1 a 5)

| Critério | T1 | T2 | T3 | T4 | T5 | Média |
|----------|:--:|:--:|:--:|:--:|:--:|:-----:|
| Facilidade de uso | | | | | | |
| Visual / aparência | | | | | | |
| Clareza dos textos e mensagens | | | | | | |
| Entendimento das etiquetas 🟢🟡🔴 e sugestões | | | | | | |
| Utilidade para um DJ | | | | | | |
| Nota geral | | | | | | |

### 3.4 Problemas e sugestões recebidos

Liste **todos**, inclusive os que você decidir não corrigir. Não esconda falhas: elas fazem parte da avaliação.

| ID | Testador | Tarefa | Problema ou sugestão (como relatado) | Gravidade (A/M/B) | Pertinente? | Decisão |
|----|----------|--------|--------------------------------------|:-----------------:|:-----------:|---------|
| F01 | | | | | | |
| F02 | | | | | | |
| F03 | | | | | | |

## 4. Triagem: o que corrigir

Cada item da tabela 3.4 recebe uma decisão:

| Decisão | Quando usar |
|---------|-------------|
| **Corrigir agora** | Gravidade A (impede o uso), ou M com correção simples |
| **Melhoria adotada** | Sugestão pertinente que melhora a experiência e cabe no prazo |
| **Adiada (backlog)** | Pertinente, mas grande demais para o prazo; registrar como trabalho futuro |
| **Não adotada** | Fora do escopo (ex.: "tocar a música"), conflita com um requisito ou é preferência individual. **Justificar.** |

Cada correção feita vai para [correcoes/REGISTRO-DE-CORRECOES.md](correcoes/REGISTRO-DE-CORRECOES.md), com o
antes/depois, e entra no vídeo de mudanças ([ROTEIRO-VIDEO-MUDANCAS.md](ROTEIRO-VIDEO-MUDANCAS.md)).

## 5. Conclusão da validação

*(Preencher ao final.)* Exemplo de estrutura:
> Dos 5 testadores, __ concluíram todas as tarefas. A taxa média de sucesso foi de __%. Foram relatados __ problemas
> (__ de gravidade A, __ M, __ B) e __ sugestões. Foram corrigidos __ e adotadas __ melhorias; __ itens ficaram para
> trabalhos futuros (justificados na seção 3.4). A nota geral média foi __/5.
