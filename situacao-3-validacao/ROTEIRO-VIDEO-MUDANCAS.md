# 🎬 Roteiro do vídeo da Situação 3: mudanças adotadas (até 5 minutos)

> A Situação 3 pede um vídeo mostrando a solução funcionando e **quais mudanças foram adotadas** a partir dos testes.
> Grave **depois** de aplicar as correções vindas dos testadores. Ferramentas: OBS Studio ou Win + Alt + R.

| Tempo | Tela | O que mostrar | Fala sugerida |
|-------|------|---------------|---------------|
| 0:00–0:30 | README no GitHub | Projeto e organização das pastas | "Este é o HarmoniMix. Nesta etapa eu testei o sistema em todos os níveis do Modelo V e coloquei cinco pessoas para usá-lo de verdade." |
| 0:30–1:15 | `PLANO-DE-TESTES.md` + terminal | Rodar os testes de sistema; o navegador sendo controlado (opcional: `headless=False`) | "Além de 217 testes unitários e de integração, criei 15 testes de sistema que abrem o sistema num navegador de verdade e fazem o que um usuário faria. Todos passam." |
| 1:15–1:50 | Celular (antes/depois) | Print da rolagem horizontal (D06) e a tela corrigida | "Esses testes acharam um problema que eu não tinha visto: no celular, todas as páginas rolavam para o lado. A causa era o menu. Corrigi e o teste agora garante que isso não volta." |
| 1:50–2:20 | Formulário + pasta `feedbacks/` | O formulário e os 5 PDFs recebidos | "Para a validação, enviei o sistema publicado e este formulário para cinco colegas: [nomes]. Eles registraram o que funcionou, o que não funcionou e o que não testaram, com prints." |
| 2:20–4:00 | Sistema (antes → depois) | Para **cada mudança adotada** (F01, F02…): o print do problema e a tela corrigida | "O [testador] apontou que [problema]. Eu [correção]. Agora fica assim: [mostrar]." *(repetir para as 2 a 4 mudanças principais)* |
| 4:00–4:30 | `REGISTRO-DE-CORRECOES.md` | Itens não adotados e o motivo | "Algumas sugestões, como [x], ficaram para o futuro porque [motivo]." |
| 4:30–5:00 | Sistema rodando | Editor de setlist com o set da sua playlist | "Com as correções, o HarmoniMix está pronto. Obrigado a todos que testaram!" |

## Checklist
- [ ] Mostrar os testes automatizados passando
- [ ] Mostrar pelo menos 2 mudanças vindas dos testadores (antes → depois)
- [ ] Citar os testadores (com a autorização marcada no formulário)
- [ ] Duração conferida com o(a) tutor(a)
- [ ] Link do vídeo no README principal
