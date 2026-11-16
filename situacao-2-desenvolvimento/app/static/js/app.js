/* HarmoniMix: comportamentos do front-end (sem dependências externas). */
(function () {
  "use strict";

  const NS = "http://www.w3.org/2000/svg";
  // Cor de cada número da Roda de Camelot (mesma regra das etiquetas de tom no CSS)
  const corDoTom = (codigo) => `hsl(${(parseInt(codigo, 10) - 1) * 30} 75% 68%)`;
  const COR_NIVEL = { suave: "#3ddc84", atencao: "#f5b83d", arriscada: "#ff5a4f" };
  const NOME_NIVEL = { suave: "Suave", atencao: "Atenção", arriscada: "Arriscada" };

  // Escapa texto vindo do usuário antes de montá-lo em SVG/HTML (proteção contra XSS)
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmtTempo = (seg) => `${Math.floor(seg / 60)}:${String(Math.round(seg % 60)).padStart(2, "0")}`;
  const fmtNum = (n) => (Math.round(n * 10) / 10).toString().replace(".", ",");

  // ---------------------------------------------------------------------------
  // 1. Confirmação antes de ações destrutivas (MSG14)
  // ---------------------------------------------------------------------------
  document.addEventListener("submit", (ev) => {
    const msg = ev.target.getAttribute("data-confirm");
    if (msg && !window.confirm(msg)) ev.preventDefault();
  });

  // ---------------------------------------------------------------------------
  // 2. Valor do controle deslizante de energia
  // ---------------------------------------------------------------------------
  document.querySelectorAll("input[type=range][data-saida]").forEach((input) => {
    const saida = document.getElementById(input.dataset.saida);
    const atualizar = () => { if (saida) saida.textContent = input.value; };
    input.addEventListener("input", atualizar);
    atualizar();
  });

  // ---------------------------------------------------------------------------
  // 3. Visão geral do set: cada faixa é um bloco (largura = duração, altura = energia,
  //    cor = tom); a linha clara é o BPM; os LEDs no topo marcam cada transição.
  // ---------------------------------------------------------------------------
  function desenharSet(el, mini) {
    const d = JSON.parse(el.dataset.curva);
    const n = d.bpm.length;
    if (!n) return;
    // largura real do elemento: o SVG não é esticado, então os textos não se deformam
    const W = mini ? 140 : Math.max(280, Math.round(el.clientWidth || 1000)), H = mini ? 26 : 168;
    const topo = mini ? 0 : 26, base = mini ? H : 132, alt = base - topo;
    const total = d.duracoes.reduce((a, b) => a + b, 0) || 1;
    const gap = mini ? 1 : 3;
    const xs = []; let acc = 0;
    d.duracoes.forEach((dur) => { xs.push(acc / total * W); acc += dur; });
    const larg = (i) => Math.max(1, d.duracoes[i] / total * W - gap);

    let s = `<svg viewBox="0 0 ${W} ${H}"${mini ? ' preserveAspectRatio="none"' : ""} xmlns="${NS}">`;
    if (!mini) {
      // grade de tempo (a cada 5 ou 10 minutos)
      const passo = total > 2400 ? 600 : 300;
      for (let t = 0; t <= total; t += passo) {
        const x = t / total * W;
        s += `<line x1="${x}" x2="${x}" y1="${topo}" y2="${base + 6}" stroke="#2c3138" stroke-width="1"/>`;
        s += `<text x="${x + 4}" y="${H - 14}" fill="#a3a9b3" font-size="13" font-family="Archivo, sans-serif">${fmtTempo(t)}</text>`;
      }
    }
    d.energia.forEach((e, i) => {
      const h = Math.max(mini ? 4 : 10, e / 10 * alt);
      const info = `${esc(d.titulos[i])} (${esc(d.tons[i])}, ${fmtNum(d.bpm[i])} BPM, energia ${esc(e)})`;
      s += `<rect x="${xs[i]}" y="${base - h}" width="${larg(i)}" height="${h}" rx="${mini ? 1 : 3}" fill="${corDoTom(d.tons[i])}"><title>${info}</title></rect>`;
      if (!mini && larg(i) > 46) {
        s += `<text x="${xs[i] + 6}" y="${base - 7}" fill="#15171a" font-size="13" font-weight="750" font-family="Archivo, sans-serif">${esc(d.tons[i])}</text>`;
      }
    });
    if (!mini && n > 1) {
      const minB = Math.min(...d.bpm) - 4, maxB = Math.max(...d.bpm) + 4;
      const y = (b) => base - 8 - (b - minB) / (maxB - minB) * (alt - 16);
      const pts = d.bpm.map((b, i) => `${xs[i] + larg(i) / 2},${y(b)}`).join(" ");
      s += `<polyline points="${pts}" fill="none" stroke="#17191d" stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>`;
      s += `<polyline points="${pts}" fill="none" stroke="#e8eaed" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>`;
      d.bpm.forEach((b, i) => {
        if (larg(i) > 46) s += `<text x="${xs[i] + larg(i) / 2}" y="${y(b) - 10}" fill="#e8eaed" font-size="12" text-anchor="middle" font-family="Archivo, sans-serif" paint-order="stroke" stroke="#17191d" stroke-width="4">${fmtNum(b)}</text>`;
      });
      (d.niveis || []).forEach((nivel, i) => {
        const x = xs[i + 1] - gap / 2;
        s += `<line x1="${x}" x2="${x}" y1="14" y2="${base}" stroke="${COR_NIVEL[nivel]}" stroke-opacity=".45" stroke-width="1.5"/>`;
        s += `<circle cx="${x}" cy="10" r="5" fill="${COR_NIVEL[nivel]}"><title>Transição ${i + 1} → ${i + 2}: ${NOME_NIVEL[nivel]}</title></circle>`;
      });
    }
    el.innerHTML = s + "</svg>";
    if (!mini) {
      el.querySelector("svg").setAttribute("role", "img");
      el.querySelector("svg").setAttribute("aria-label",
        `Visão geral do set: ${n} faixas, ${fmtTempo(total)} no total. BPM de ${fmtNum(Math.min(...d.bpm))} a ${fmtNum(Math.max(...d.bpm))}.`);
    }
  }
  const visao = document.getElementById("visao-geral");
  if (visao) {
    desenharSet(visao, false);
    let espera;
    window.addEventListener("resize", () => { clearTimeout(espera); espera = setTimeout(() => desenharSet(visao, false), 150); });
  }
  document.querySelectorAll(".mini-ribbon[data-curva]").forEach((el) => desenharSet(el, true));

  // ---------------------------------------------------------------------------
  // 4. Anel de Camelot: marca do site (24 segmentos, um por tom)
  // ---------------------------------------------------------------------------
  const arco = (C, r0, r1, a0, a1) => {
    const p = (r, a) => [C + r * Math.sin(a), C - r * Math.cos(a)];
    const [ax, ay] = p(r1, a0), [bx, by] = p(r1, a1), [cx, cy] = p(r0, a1), [dx, dy] = p(r0, a0);
    return `M${ax},${ay}A${r1},${r1} 0 0 1 ${bx},${by}L${cx},${cy}A${r0},${r0} 0 0 0 ${dx},${dy}Z`;
  };
  document.querySelectorAll("[data-anel]").forEach((el) => {
    let s = `<svg viewBox="0 0 100 100" xmlns="${NS}" width="100%" height="100%">`;
    for (let i = 1; i <= 12; i++) {
      const a0 = ((i * 30 - 15) * Math.PI) / 180, a1 = a0 + (30 * Math.PI) / 180;
      s += `<path d="${arco(50, 34, 49, a0, a1)}" fill="hsl(${(i - 1) * 30} 75% 68%)" stroke="#17191d" stroke-width="1.6"/>`;
      s += `<path d="${arco(50, 20, 34, a0, a1)}" fill="hsl(${(i - 1) * 30} 55% 48%)" stroke="#17191d" stroke-width="1.6"/>`;
    }
    el.innerHTML = s + "</svg>";
  });

  // ---------------------------------------------------------------------------
  // 5. Roda de Camelot interativa (página de ajuda)
  // ---------------------------------------------------------------------------
  const roda = document.getElementById("roda-camelot");
  if (roda) {
    const sel = roda.dataset.tom;
    const compat = JSON.parse(roda.dataset.compativeis);
    const base = roda.dataset.url;
    const C = 220, R1 = 210, R2 = 145, R3 = 80;
    let s = `<svg viewBox="0 0 440 440" width="100%" role="img" aria-label="Roda de Camelot com o tom ${esc(sel)} selecionado" xmlns="${NS}">`;
    for (let i = 1; i <= 12; i++) {
      const a0 = ((i * 30 - 15) * Math.PI) / 180, a1 = a0 + (30 * Math.PI) / 180, am = (a0 + a1) / 2;
      [["B", R2, R1], ["A", R3, R2]].forEach(([m, r0, r1]) => {
        const k = i + m, ok = compat.includes(k), atual = k === sel, rt = (r0 + r1) / 2;
        s += `<a href="${base}?tom=${k}" aria-label="Tom ${k}"><path d="${arco(C, r0, r1, a0, a1)}" fill="${ok ? corDoTom(k) : "#2c3138"}" stroke="#17191d" stroke-width="3"/>`;
        s += `<text x="${C + rt * Math.sin(am)}" y="${C - rt * Math.cos(am) + 5}" text-anchor="middle" font-family="Archivo, sans-serif" font-size="${atual ? 19 : 15}" font-weight="${atual ? 800 : 650}" fill="${ok ? "#15171a" : "#a3a9b3"}">${k}</text></a>`;
      });
    }
    s += `<circle cx="${C}" cy="${C}" r="${R3 - 4}" fill="#1c1f24"/><text x="${C}" y="${C + 4}" text-anchor="middle" fill="#e8eaed" font-family="Archivo, sans-serif" font-size="30" font-weight="800">${esc(sel)}</text>`;
    s += `<text x="${C}" y="${C + 26}" text-anchor="middle" fill="#a3a9b3" font-family="Archivo, sans-serif" font-size="13">${sel.endsWith("A") ? "menor" : "maior"}</text></svg>`;
    roda.innerHTML = s;
  }
})();
