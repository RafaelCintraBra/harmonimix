# 🎬 Roteiro do vídeo de demonstração (≈ 5 minutos)

> As instruções pedem um vídeo **narrado**. A Situação 3 fala em "até 5 minutos" e a orientação geral em
> "pelo menos 5 minutos": **confirme com o(a) tutor(a)**. Este roteiro dá cerca de 5 minutos.
>
> **Antes de gravar:** rode `flask --app run seed-demo` para ter os dados de demonstração e deixe o navegador em
> tela cheia. Para gravar, use o OBS Studio (gratuito) ou a gravação de tela do Windows (Win + Alt + R).

| Tempo | Tela | O que mostrar | Fala sugerida |
|-------|------|---------------|---------------|
| 0:00–0:30 | Slide ou README no GitHub | Nome, problema | "Olá, eu sou [nome] e este é o HarmoniMix, um sistema para DJs montarem setlists em que as músicas combinam. Quando duas músicas seguidas têm tons ou velocidades muito diferentes, a mixagem soa estranha e a pista esfria. O HarmoniMix resolve isso usando a Roda de Camelot." |
| 0:30–1:00 | Login e Painel | Entrar com a conta demo | "Eu entro com a minha conta. No painel vejo o resumo: 18 músicas, 2 setlists, o BPM médio e o próximo evento, a formatura." |
| 1:00–1:45 | Biblioteca → Nova faixa | Filtrar por BPM; cadastrar uma faixa com **erro** (BPM 250) e depois corrigir | "Na biblioteca ficam as músicas com BPM, tom, gênero e energia. Posso filtrar, por exemplo, de 120 a 125 BPM. Ao cadastrar uma faixa, o sistema valida os dados: se eu colocar BPM 250, ele mostra o erro ao lado do campo e mantém o que eu digitei. Corrijo e salvo." |
| 1:45–3:15 | Editor → "Rascunho" | Etiquetas 🟢🟡🔴, motivo, pontuação de 25%, gráfico, sugestões; **adicionar** uma sugestão; **reordenar** | "Esta é a tela principal. Entre cada par de músicas o sistema classifica a transição: verde quando o tom é compatível e o BPM varia até 6%; amarelo quando só um critério é atendido; vermelho quando nenhum é. Ele explica o motivo, por exemplo 'tom incompatível, 8A para 5A, BPM +10%'. Este set tem só 25% de transições suaves. Do lado direito, o sistema sugere as próximas músicas que combinam com a última. Vou adicionar 'Batida Urbana'. Também posso subir, descer e remover faixas. O gráfico mostra a curva de energia do set." |
| 3:15–3:45 | Editor → "Warm-up até o pico" | Set com 100% de harmonia e curva subindo | "Compare com este outro set: todas as transições estão verdes, 100%, e a curva de energia sobe do Deep House até o Techno, que é o ideal para uma festa." |
| 3:45–4:10 | Roda de Camelot | Clicar em 8A e depois em 12B | "Para quem não conhece a teoria, a página de ajuda mostra a roda: clicando num tom, ela destaca os compatíveis. Repare que o 12 é vizinho do 1." |
| 4:10–4:30 | Importar / Exportar | Importar a **sua playlist exportada do Rekordbox** (.txt); baixar o CSV de um setlist | "Para trazer as minhas músicas, eu exporto a playlist do Rekordbox e importo aqui: o sistema lê BPM, tom e duração e converte o tom de 'Am' para '8A' sozinho. Também dá para exportar o setlist com a análise para o Excel." |
| 4:30–5:00 | VS Code / terminal | Pastas do MVC; rodar `pytest` (217 testes passando, 99% de cobertura) | "Por dentro, o código segue o padrão MVC: models, controllers, templates e uma camada de serviços com as regras. São 217 testes automatizados com 99% de cobertura, rodando em SQLite e MySQL. Tudo está no GitHub. Obrigado!" |

## Checklist antes de enviar
- [ ] Áudio claro (teste o microfone antes)
- [ ] Mostrar pelo menos um **erro tratado** (formulário com BPM inválido)
- [ ] Mostrar o **algoritmo funcionando** (cores das transições e sugestões)
- [ ] Mostrar os **testes passando**
- [ ] Duração conferida com o(a) tutor(a)
- [ ] Link do vídeo (YouTube "não listado" ou Google Drive) colocado no README do repositório
