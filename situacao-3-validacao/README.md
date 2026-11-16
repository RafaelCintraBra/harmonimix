# Situação 3: Testes, Validação e Correções

Verificação e validação do **HarmoniMix**: testes em todos os níveis do Modelo V, teste com 5 usuários, correções e
documentação final.

| Entrega pedida | Onde está | Status |
|----------------|-----------|:------:|
| Realizar e documentar os testes (verificação e validação) | [PLANO-DE-TESTES.md](PLANO-DE-TESTES.md) · [VERIFICACAO.md](VERIFICACAO.md) · [testes-sistema/](testes-sistema/) · [evidencias/](evidencias/) | ✅ |
| Formulário para os testadores (nome, data, o que funcionou, o que não funcionou, o que não foi testado, prints) | [formulario/Formulario-Teste-HarmoniMix.docx](formulario/Formulario-Teste-HarmoniMix.docx) | ✅ |
| Oferecer a solução a 5 colegas (endereço para testar) | [PUBLICAR-ONLINE.md](PUBLICAR-ONLINE.md) · [VALIDACAO-COM-USUARIOS.md](VALIDACAO-COM-USUARIOS.md) | ⏳ estudante |
| PDF com as 5 opiniões/testes | [feedbacks/](feedbacks/) | ⏳ estudante |
| Correções e melhorias incorporadas à documentação | [correcoes/REGISTRO-DE-CORRECOES.md](correcoes/REGISTRO-DE-CORRECOES.md) | ✅ D01–D07 · ⏳ testadores |
| Estrutura de diretórios no Git para todas as situações | [raiz do repositório](../README.md) | ✅ |
| Vídeo com a solução e as mudanças adotadas | [ROTEIRO-VIDEO-MUDANCAS.md](ROTEIRO-VIDEO-MUDANCAS.md) | ⏳ estudante |

## Resultados até agora

| Nível (Modelo V) | Testes | Resultado |
|------------------|:------:|:---------:|
| Unitário | 152 | ✅ 100% |
| Integração e segurança | 65 | ✅ 100% (SQLite e MariaDB) |
| Sistema (navegador real) | 15 | ✅ 100% |
| Desempenho (2.000 faixas) | 4 telas | ✅ ≤ 56 ms (meta: 1 s) |
| Aceitação (5 usuários) | 12 tarefas × 5 | ⏳ aguardando os testadores |

Cobertura de código: **99%**. Defeitos encontrados e corrigidos: **7** (D01–D07).

## Estrutura

```
situacao-3-validacao/
├── README.md
├── PLANO-DE-TESTES.md          ← estratégia (Modelo V), casos de teste de sistema e resultados
├── VERIFICACAO.md              ← revisões, inspeção de código, rastreabilidade, desempenho
├── VALIDACAO-COM-USUARIOS.md   ← procedimento e consolidação do teste com 5 pessoas
├── PUBLICAR-ONLINE.md          ← como colocar o sistema na internet (PythonAnywhere)
├── ROTEIRO-VIDEO-MUDANCAS.md   ← roteiro do vídeo final
├── testes-sistema/             ← 15 testes no navegador (Playwright) + medição de desempenho
├── evidencias/                 ← prints gerados pelos testes (CTS-01 … CTS-16) e desempenho.txt
├── formulario/                 ← formulário (.docx e .pdf) + CSV de exemplo para a tarefa T4
├── feedbacks/                  ← formulários respondidos pelos 5 testadores (PDF)
└── correcoes/                  ← registro de correções e melhorias
```

## Próximos passos (estudante)

1. Publicar o sistema ([PUBLICAR-ONLINE.md](PUBLICAR-ONLINE.md)) e colocar o endereço no formulário.
2. Enviar para os 5 testadores, com a mensagem pronta de [VALIDACAO-COM-USUARIOS.md](VALIDACAO-COM-USUARIOS.md).
3. Guardar os 5 PDFs em `feedbacks/` e preencher as tabelas de consolidação.
4. Corrigir o que for pertinente e registrar em `correcoes/`.
5. Gravar o vídeo ([ROTEIRO-VIDEO-MUDANCAS.md](ROTEIRO-VIDEO-MUDANCAS.md)).
