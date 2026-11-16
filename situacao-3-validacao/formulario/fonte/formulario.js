// Gera o formulário de teste com usuários (Situação 3) em .docx
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle, LevelFormat, Footer, PageNumber, TableLayoutType,
} = require("docx");

const FONTE = "Arial";
const ROXO = "5B21B6";
const CINZA = "F3F4F6";
const LILAS = "EDE9FE";
const LARGURA = 9638; // A4 com margens de 2 cm: 11906 - 2*1134

const borda = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const bordas = { top: borda, bottom: borda, left: borda, right: borda };

const t = (texto, op = {}) => new TextRun({ text: texto, font: FONTE, size: op.size || 20, ...op });
const p = (filhos, op = {}) => new Paragraph({ children: Array.isArray(filhos) ? filhos : [t(filhos)], spacing: { after: 80 }, ...op });
const h1 = (texto) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: texto })] });
const h2 = (texto) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: texto })] });
const item = (filhos) => new Paragraph({ numbering: { reference: "marcadores", level: 0 }, children: Array.isArray(filhos) ? filhos : [t(filhos)], spacing: { after: 40 } });
const vazio = (n = 1) => Array.from({ length: n }, () => new Paragraph({ children: [t("")], spacing: { after: 0 } }));

function celula(conteudo, largura, op = {}) {
  const paragrafos = (Array.isArray(conteudo) ? conteudo : [conteudo]).map((c) =>
    c instanceof Paragraph ? c : new Paragraph({ children: [t(String(c), { bold: !!op.negrito, size: op.size || 19, color: op.cor })], spacing: { after: 0 } }));
  return new TableCell({
    children: paragrafos, width: { size: largura, type: WidthType.DXA }, borders: bordas,
    shading: op.fundo ? { fill: op.fundo, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    columnSpan: op.span,
  });
}

function tabela(larguras, linhas, op = {}) {
  return new Table({
    width: { size: larguras.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: larguras,
    layout: TableLayoutType.FIXED,
    rows: linhas.map((linha, i) => new TableRow({
      tableHeader: op.cabecalho && i === 0,
      cantSplit: true,
      height: op.altura && i > 0 ? { value: op.altura, rule: "atLeast" } : undefined,
      children: linha.map((c, j) => celula(c, larguras[j], {
        negrito: op.cabecalho && i === 0, fundo: op.cabecalho && i === 0 ? LILAS : (op.zebra && i % 2 === 0 ? CINZA : undefined),
      })),
    })),
  });
}

// Caixa grande para escrita livre
function caixa(dica, altura = 1800) {
  return new Table({
    width: { size: LARGURA, type: WidthType.DXA }, columnWidths: [LARGURA], layout: TableLayoutType.FIXED,
    rows: [new TableRow({ height: { value: altura, rule: "atLeast" }, cantSplit: true,
      children: [celula(new Paragraph({ children: [t(dica, { italics: true, color: "8A8A8A", size: 18 })], spacing: { after: 0 } }), LARGURA)] })],
  });
}

const SIM_NAO = "☐ Funcionou   ☐ Não funcionou   ☐ Não testei";

const tarefas = [
  ["T1", "Criar uma conta (Crie agora), sair (↩ Sair) e entrar de novo com e-mail e senha."],
  ["T2", "Biblioteca → + Nova faixa: tente salvar com BPM 250 (deve dar erro). Depois corrija e salve uma faixa válida."],
  ["T3", "Biblioteca: buscar por nome, filtrar por BPM (ex.: 118 a 125) e ordenar clicando na coluna BPM."],
  ["T4", "Biblioteca → ⬆ Importar CSV: importe o arquivo modelo-importacao.csv (enviado junto com este formulário)."],
  ["T5", "Eventos → + Novo evento: cadastre um evento com data e local."],
  ["T6", "Setlists: crie um setlist vinculado ao evento. No editor, adicione uma faixa pela busca e depois outras pelas 💡 Sugestões."],
  ["T7", "No editor: observe as etiquetas 🟢 Suave / 🟡 Atenção / 🔴 Arriscada. Use ▲ ▼ para reordenar e X para remover. A análise mudou?"],
  ["T8", "No editor: confira o gráfico Curva de energia, a duração total e a pontuação harmônica."],
  ["T9", "No editor: ⬇ Exportar CSV e abra o arquivo no Excel ou Planilhas."],
  ["T10", "Roda de Camelot: clique em alguns tons e veja quais combinam."],
  ["T11", "Tente excluir uma faixa que está num setlist (deve ser bloqueado, com explicação)."],
  ["T12", "Abra o sistema no celular e repita uma tarefa qualquer."],
];

function secaoPerfil(perfil) {
  if (!perfil) return [];
  const RES = ["☐ OK", "☐ Problema", "☐ Não verifiquei"];
  return [
    h1(`★ Seu critério de avaliação: ${perfil.criterio}`),
    tabela([2600, LARGURA - 2600], [
      ["Pergunta principal", perfil.pergunta],
      ["Perfil ideal do testador", perfil.perfil],
      ["Como avaliar", perfil.como],
    ]),
    p("Além do roteiro geral (seção 2), dê atenção especial aos itens abaixo. Descreva os problemas também na seção 4.", { spacing: { before: 120, after: 80 } }),
    tabela([600, 4700, 1700, LARGURA - 7000],
      [["#", "Verificação", "Resultado", "Observação"],
       ...perfil.itens.map((txt, i) => [`C${i + 1}`, txt, RES.map((r) => new Paragraph({ children: [t(r, { size: 18 })], spacing: { after: 0 } })), ""])],
      { cabecalho: true, zebra: true }),
    p("", { spacing: { after: 120 } }),   // separa as tabelas (o Word junta tabelas coladas)
    tabela([4600, 1007, 1007, 1008, 1008, 1008], [
      [`Nota para o critério "${perfil.criterio}" (1 = ruim · 5 = ótimo)`, "1", "2", "3", "4", "5"],
      ["Minha nota", "☐", "☐", "☐", "☐", "☐"],
    ], { cabecalho: true }),
  ];
}

function gerar(perfil, arquivo) {
const subtitulo = perfil ? `Testador ${perfil.n} · Critério: ${perfil.criterio}` : "HarmoniMix: montador de setlists com mixagem harmônica para DJs";
const doc = new Document({
  creator: "HarmoniMix",
  title: "Formulário de Teste de Usuário - HarmoniMix",
  styles: {
    default: { document: { run: { font: FONTE, size: 20 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: FONTE, size: 40, bold: true, color: ROXO }, paragraph: { spacing: { before: 0, after: 80 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONTE, size: 26, bold: true, color: ROXO }, paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONTE, size: 22, bold: true, color: "333333" }, paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "marcadores", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      t(`HarmoniMix · Formulário de Teste de Usuário${perfil ? " · Testador " + perfil.n + " (" + perfil.criterio + ")" : ""} · página `, { size: 16, color: "8A8A8A" }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONTE, size: 16, color: "8A8A8A" })] })] }) },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Formulário de Teste de Usuário")] }),
      p([t(subtitulo, { size: 22, color: "555555", bold: !!perfil })], { spacing: { after: 200 } }),

      p([t("Obrigado por testar! ", { bold: true }), t("Você vai usar o sistema como um usuário de verdade e anotar o que funcionou, o que deu errado e o que não conseguiu testar. Reporte tudo, inclusive erros pequenos: as falhas encontradas são usadas para melhorar o projeto. Tempo estimado: 20 a 30 minutos.")]),
      tabela([2600, LARGURA - 2600], [
        ["Endereço do sistema", "______________________________________________"],
        ["Conta de demonstração", "E-mail: demo@harmonimix.dev   Senha: Demo1234   (ou crie a sua conta na tarefa T1)"],
        ["Como enviar", "Preencha, cole os prints na seção 7, salve como PDF e envie para o(a) autor(a)."],
      ]),

      ...secaoPerfil(perfil),

      h1("1. Identificação"),
      tabela([3000, LARGURA - 3000], [
        ["Nome de quem testou *", ""],
        ["Data do teste *", "____ / ____ / ________"],
        ["Curso / área de atuação", ""],
        ["Dispositivo e navegador", "☐ Computador   ☐ Celular   ·   Navegador: ☐ Chrome  ☐ Edge  ☐ Firefox  ☐ Safari  ☐ Outro: ______"],
        ["Experiência com DJ / música eletrônica", "☐ Nenhuma   ☐ Pouca   ☐ Toco ou já toquei como DJ"],
      ], { altura: 420 }),

      h1("2. Roteiro de tarefas"),
      p("Faça as tarefas na ordem e marque o resultado de cada uma. Use a coluna Observação para qualquer detalhe."),
      tabela([700, 4300, 2100, LARGURA - 7100],
        [["#", "Tarefa", "Resultado", "Observação"], ...tarefas.map(([n, txt]) => [n, txt, SIM_NAO.split("   ").map((s) => new Paragraph({ children: [t(s, { size: 18 })], spacing: { after: 0 } })), ""])],
        { cabecalho: true, zebra: true }),

      h1("3. O que testei e FUNCIONOU *"),
      p("Descreva as funcionalidades que funcionaram como esperado (pode citar as tarefas, ex.: \"T6: as sugestões apareceram e consegui adicionar\")."),
      caixa("Escreva aqui…", 2200),

      h1("4. O que testei e NÃO FUNCIONOU *"),
      p("Para cada problema: qual funcionalidade, o que aconteceu, o que deveria acontecer (o que corrigir) e o número do print na seção 7. Inclua também textos confusos, telas difíceis de entender e lentidão."),
      tabela([2000, 2700, 2700, 900, LARGURA - 8300], [
        ["Funcionalidade / tarefa", "O que aconteceu", "O que deveria acontecer / o que corrigir", "Print nº", "Gravidade*"],
        ...Array.from({ length: 5 }, () => ["", "", "", "", ""]),
      ], { cabecalho: true, altura: 900 }),
      p([t("* Gravidade: ", { bold: true, size: 17 }), t("A = impede o uso · M = atrapalha, mas dá para contornar · B = detalhe visual ou de texto.", { size: 17 })], { spacing: { before: 60, after: 80 } }),

      h1("5. Funcionalidade NÃO TESTADA *"),
      p("Liste o que você não testou e por quê (não encontrei a opção, faltou tempo, um erro anterior impediu, não entendi o que fazer, a função existe mas não consegui realizar…)."),
      tabela([3300, LARGURA - 3300], [
        ["Funcionalidade / tarefa", "Motivo"],
        ...Array.from({ length: 4 }, () => ["", ""]),
      ], { cabecalho: true, altura: 560 }),

      h1("6. Avaliação geral e sugestões"),
      tabela([4600, 1007, 1007, 1008, 1008, 1008], [
        ["Critério (1 = ruim · 5 = ótimo)", "1", "2", "3", "4", "5"],
        ...["Facilidade de uso", "Visual / aparência", "Clareza dos textos e mensagens de erro",
          "Entendi as etiquetas 🟢 🟡 🔴 e as sugestões", "Utilidade para um DJ", "Nota geral do sistema"]
          .map((c) => [c, "☐", "☐", "☐", "☐", "☐"]),
      ], { cabecalho: true }),
      h2("Sugestões de melhoria"),
      caixa("O que você mudaria, acrescentaria ou tiraria?", 1600),

      h1("7. Prints das telas (snapshots)"),
      p("Cole aqui os prints, principalmente dos erros. Numere cada um e use esse número na seção 4."),
      p([t("Como tirar print: ", { bold: true }), t("Windows: Win + Shift + S · Mac: Cmd + Shift + 4 · Celular: botão de volume + liga/desliga.")]),
      ...[1, 2, 3].flatMap((n) => [h2(`Print ${n}: ________________________________ (o que mostra)`), caixa("Cole a imagem aqui", 2600)]),

      h1("8. Autorização"),
      p("☐ Autorizo o uso destas respostas e prints no relatório do Projeto Integrador (o nome pode aparecer no relatório)."),
      ...vazio(1),
      p("Assinatura ou nome: _______________________________________________"),
    ],
  }],
});

return Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(arquivo, buf); console.log("ok", arquivo); });
}

const pasta = process.argv[2];
const perfis = JSON.parse(fs.readFileSync(__dirname + "/perfis.json", "utf8"));
(async () => {
  await gerar(null, `${pasta}/Formulario-Teste-HarmoniMix.docx`);
  for (const perfil of perfis) await gerar(perfil, `${pasta}/${perfil.arquivo}.docx`);
})();
