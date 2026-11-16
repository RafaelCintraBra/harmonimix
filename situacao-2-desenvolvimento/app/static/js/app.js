/* HarmoniMix: comportamentos do front-end (sem dependências externas). */
(function () {
  "use strict";

  // Cor de cada número da Roda de Camelot (mesma regra usada nas etiquetas de tom)
  const corDoTom = (n) => `hsl(${(n - 1) * 30} 85% 72%)`;

  // Escapa texto vindo do usuário antes de montá-lo em SVG/HTML (proteção contra XSS)
  const esc = (t) => String(t).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------------------------------------------------------------------------
  // 1. Confirmação antes de ações destrutivas (MSG14)
  // ---------------------------------------------------------------------------
  document.addEventListener("submit", (ev) => {
    const form = ev.target;
    const msg = form.getAttribute("data-confirm");
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
  // 3. Gráfico da curva de energia (SVG): BPM em linha, energia em barras
  // ---------------------------------------------------------------------------
  const grafico = document.getElementById("grafico-energia");
  if (grafico) {
    const dados = JSON.parse(grafico.dataset.curva);
    const n = dados.bpm.length;
    if (n >= 1) {
      const W = 560, H = 210, P = 36;
      const minB = Math.floor((Math.min(...dados.bpm) - 5) / 10) * 10;
      const maxB = Math.ceil((Math.max(...dados.bpm) + 5) / 10) * 10;
      const x = (i) => (n === 1 ? W / 2 : P + (i * (W - 2 * P)) / (n - 1));
      const yb = (b) => H - P - ((b - minB) / (maxB - minB)) * (H - 2 * P);
      const ye = (e) => H - P - (e / 10) * (H - 2 * P);
      const bw = Math.max(8, Math.min(28, (W - 2 * P) / Math.max(n, 1) - 6));
      let s = `<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="Gráfico de BPM e energia por posição no set">`;
      for (let b = minB; b <= maxB; b += 10) {
        s += `<line x1="${P}" x2="${W - P}" y1="${yb(b)}" y2="${yb(b)}" stroke="#2c2e52"/>`;
        s += `<text x="4" y="${yb(b) + 4}" fill="#9a9cba" font-size="11">${b}</text>`;
      }
      [0, 5, 10].forEach((e) => {
        s += `<text x="${W - 4}" y="${ye(e) + 4}" fill="#a78bfa" font-size="11" text-anchor="end">${e}</text>`;
      });
      dados.energia.forEach((e, i) => {
        s += `<rect x="${x(i) - bw / 2}" y="${ye(e)}" width="${bw}" height="${H - P - ye(e)}" rx="4" fill="#8b5cf6" opacity=".45"><title>${esc(dados.titulos[i])}: energia ${esc(e)}</title></rect>`;
        s += `<text x="${x(i)}" y="${H - 12}" fill="#9a9cba" font-size="11" text-anchor="middle">${i + 1}</text>`;
      });
      if (n > 1) {
        s += `<polyline fill="none" stroke="#22d3ee" stroke-width="3" points="${dados.bpm.map((b, i) => `${x(i)},${yb(b)}`).join(" ")}"/>`;
      }
      dados.bpm.forEach((b, i) => {
        s += `<circle cx="${x(i)}" cy="${yb(b)}" r="5" fill="#22d3ee"><title>${esc(dados.titulos[i])} · ${esc(dados.tons[i])} · ${esc(b)} BPM</title></circle>`;
        if (n <= 16) s += `<text x="${x(i)}" y="${yb(b) - 10}" fill="#ecedf5" font-size="11" text-anchor="middle">${Math.round(b * 10) / 10}</text>`;
      });
      grafico.innerHTML = s + "</svg>";
    }
  }

  // ---------------------------------------------------------------------------
  // 4. Roda de Camelot interativa (página de ajuda)
  // ---------------------------------------------------------------------------
  const roda = document.getElementById("roda-camelot");
  if (roda) {
    const sel = roda.dataset.tom;
    const compat = JSON.parse(roda.dataset.compativeis);
    const base = roda.dataset.url;
    const C = 220, R1 = 210, R2 = 145, R3 = 80;
    const ponto = (r, a) => [C + r * Math.sin(a), C - r * Math.cos(a)];
    const arco = (r0, r1, a0, a1) => {
      const [ax, ay] = ponto(r1, a0), [bx, by] = ponto(r1, a1), [cx, cy] = ponto(r0, a1), [dx, dy] = ponto(r0, a0);
      return `M${ax},${ay}A${r1},${r1} 0 0 1 ${bx},${by}L${cx},${cy}A${r0},${r0} 0 0 0 ${dx},${dy}Z`;
    };
    let s = `<svg viewBox="0 0 440 440" width="100%" role="img" aria-label="Roda de Camelot com o tom ${sel} selecionado">`;
    for (let i = 1; i <= 12; i++) {
      const a0 = ((i * 30 - 15) * Math.PI) / 180, a1 = a0 + (30 * Math.PI) / 180, am = (a0 + a1) / 2;
      [["B", R2, R1], ["A", R3, R2]].forEach(([m, r0, r1]) => {
        const k = i + m, ok = compat.includes(k), atual = k === sel, rt = (r0 + r1) / 2;
        s += `<a href="${base}?tom=${k}" aria-label="Tom ${k}"><path d="${arco(r0, r1, a0, a1)}" fill="${ok ? corDoTom(i) : "#20223f"}" stroke="#0e0f1d" stroke-width="3"/>`;
        s += `<text x="${C + rt * Math.sin(am)}" y="${C - rt * Math.cos(am) + 5}" text-anchor="middle" font-size="${atual ? 18 : 15}" font-weight="700" fill="${ok ? "#0e0f1d" : "#9a9cba"}">${k}</text></a>`;
      });
    }
    s += `<circle cx="${C}" cy="${C}" r="${R3 - 4}" fill="#171830"/><text x="${C}" y="${C - 4}" text-anchor="middle" fill="#ecedf5" font-size="26" font-weight="800">${sel}</text>`;
    s += `<text x="${C}" y="${C + 18}" text-anchor="middle" fill="#9a9cba" font-size="12">${sel.endsWith("A") ? "menor" : "maior"}</text></svg>`;
    roda.innerHTML = s;
  }
})();
