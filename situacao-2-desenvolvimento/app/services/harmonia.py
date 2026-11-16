"""HarmoniaService: regras de mixagem harmônica (RN06 a RN11).

Este módulo é "puro": não acessa banco nem Flask. Recebe objetos que tenham os atributos
`cod_tom`, `bpm`, `energia` e `duracao_seg` (por exemplo, o model Faixa) e devolve resultados.
Por isso as regras podem ser testadas de forma isolada (testes unitários).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

TOLERANCIA_BPM = 6.0          # RN07: variação máxima aceitável, em %
LIMITE_SUGESTOES = 10         # RN11

MESMO_TOM = "mesmo tom"
VIZINHO = "vizinho"
RELATIVO = "relativo"
_ORDEM_TIPO = {MESMO_TOM: 0, VIZINHO: 1, RELATIVO: 2}

SUAVE = "suave"
ATENCAO = "atencao"
ARRISCADA = "arriscada"

_RE_TOM = re.compile(r"^(1[0-2]|[1-9])([AB])$")


# ---------------------------------------------------------------------------
# Tom (RN03 e RN06)
# ---------------------------------------------------------------------------
def tom_valido(codigo: str | None) -> bool:
    """RN03: número de 1 a 12 seguido de A (menor) ou B (maior)."""
    return bool(codigo) and bool(_RE_TOM.match(str(codigo).strip().upper()))


# Notação musical -> Camelot (tônica com sustenido ou bemol; maiúsculas/minúsculas são normalizadas)
_TONICA_PARA_SEMITOM = {
    "C": 0, "B#": 0, "C#": 1, "DB": 1, "D": 2, "D#": 3, "EB": 3, "E": 4, "FB": 4, "F": 5, "E#": 5,
    "F#": 6, "GB": 6, "G": 7, "G#": 8, "AB": 8, "A": 9, "A#": 10, "BB": 10, "B": 11, "CB": 11,
}
# Camelot de cada semitom: maior (B) e menor relativo (A). Ex.: C maior = 8B; A menor = 8A.
_SEMITOM_MAIOR = {0: 8, 7: 9, 2: 10, 9: 11, 4: 12, 11: 1, 6: 2, 1: 3, 8: 4, 3: 5, 10: 6, 5: 7}
_SEMITOM_MENOR = {9: 8, 4: 9, 11: 10, 6: 11, 1: 12, 8: 1, 3: 2, 10: 3, 5: 4, 0: 5, 7: 6, 2: 7}
_RE_MUSICAL = re.compile(
    r"^([A-G])\s*([#♯B♭]?)\s*(M|MIN|MINOR|MENOR|MAJ|MAJOR|MAIOR|-)?$")
_RE_OPEN_KEY = re.compile(r"^(1[0-2]|[1-9])\s*([DM])$")


def normalizar_tom(texto: str | None) -> str | None:
    """Converte o tom para o código Camelot, aceitando os formatos dos softwares de DJ.

    - Camelot ......... '8A', '12b'                  -> '8A', '12B'
    - Notação musical . 'Am', 'F#m', 'Dbm', 'C', 'Eb' -> '8A', '11A', '12A', '8B', '5B'
      (também 'A minor', 'Amin', 'C major', 'A♭m')
    - Open Key (Traktor) '1d', '1m'                  -> '8B', '8A'
    Devolve None se não reconhecer o formato.
    """
    if not texto:
        return None
    bruto = str(texto).strip()
    if tom_valido(bruto):
        return bruto.upper()

    open_key = _RE_OPEN_KEY.match(bruto.upper())
    if open_key:                      # Open Key n -> Camelot ((n + 6) mod 12) + 1
        n = int(open_key.group(1))
        return f"{(n + 6) % 12 + 1}{'B' if open_key.group(2) == 'D' else 'A'}"

    # 'm' minúsculo = menor; por isso o modo é lido ANTES de passar para maiúsculas
    menor_curto = bool(re.fullmatch(r"[A-Ga-g][#♯b♭]?\s*m", bruto))
    musical = _RE_MUSICAL.match(bruto.upper().replace(" ", ""))
    if not musical:
        return None
    tonica = musical.group(1) + musical.group(2).replace("♯", "#").replace("♭", "B")
    sufixo = musical.group(3) or ""
    if tonica not in _TONICA_PARA_SEMITOM:
        return None
    menor = menor_curto or sufixo in ("MIN", "MINOR", "MENOR", "-")
    if sufixo == "M" and not menor_curto:      # 'M' maiúsculo isolado = maior
        menor = False
    semitom = _TONICA_PARA_SEMITOM[tonica]
    if menor:
        return f"{_SEMITOM_MENOR[semitom]}A"
    return f"{_SEMITOM_MAIOR[semitom]}B"


def decompor_tom(codigo: str) -> tuple[int, str]:
    """'8A' -> (8, 'A'). Lança ValueError se o código for inválido."""
    if not tom_valido(codigo):
        raise ValueError(f"Tom inválido: {codigo!r}")
    codigo = codigo.strip().upper()
    return int(codigo[:-1]), codigo[-1]


def distancia_circular(n1: int, n2: int) -> int:
    """Distância entre duas posições da roda (12 é vizinho de 1)."""
    d = abs(n1 - n2) % 12
    return min(d, 12 - d)


def tipo_compatibilidade(tom1: str, tom2: str) -> str | None:
    """RN06: devolve 'mesmo tom', 'vizinho', 'relativo' ou None (incompatível)."""
    n1, m1 = decompor_tom(tom1)
    n2, m2 = decompor_tom(tom2)
    if n1 == n2 and m1 == m2:
        return MESMO_TOM
    if m1 == m2 and distancia_circular(n1, n2) == 1:
        return VIZINHO
    if n1 == n2:
        return RELATIVO
    return None


def tons_compativeis(tom1: str, tom2: str) -> bool:
    return tipo_compatibilidade(tom1, tom2) is not None


def tons_compativeis_com(tom: str) -> list[str]:
    """Lista os 4 tons compatíveis com `tom` (ele mesmo, 2 vizinhos e o relativo)."""
    n, m = decompor_tom(tom)
    anterior = 12 if n == 1 else n - 1
    proximo = 1 if n == 12 else n + 1
    outro_modo = "B" if m == "A" else "A"
    return [f"{n}{m}", f"{anterior}{m}", f"{proximo}{m}", f"{n}{outro_modo}"]


# ---------------------------------------------------------------------------
# BPM (RN07)
# ---------------------------------------------------------------------------
def variacao_bpm(bpm_origem: float, bpm_destino: float) -> float:
    """Variação percentual com sinal: (destino − origem) ÷ origem × 100."""
    bpm_origem, bpm_destino = float(bpm_origem), float(bpm_destino)
    if bpm_origem <= 0:
        raise ValueError("O BPM de origem deve ser maior que zero.")
    return (bpm_destino - bpm_origem) / bpm_origem * 100


def bpm_compativel(bpm_origem: float, bpm_destino: float) -> bool:
    # arredonda para evitar falsos negativos de ponto flutuante (ex.: 6,0000000001%)
    return round(abs(variacao_bpm(bpm_origem, bpm_destino)), 6) <= TOLERANCIA_BPM


# ---------------------------------------------------------------------------
# Transição (RN08)
# ---------------------------------------------------------------------------
@dataclass
class Transicao:
    origem: object
    destino: object
    tipo_tom: str | None
    variacao: float
    nivel: str = field(init=False)
    motivo: str = field(init=False)

    def __post_init__(self):
        tom_ok = self.tipo_tom is not None
        bpm_ok = round(abs(self.variacao), 6) <= TOLERANCIA_BPM
        criterios = int(tom_ok) + int(bpm_ok)
        self.nivel = {2: SUAVE, 1: ATENCAO, 0: ARRISCADA}[criterios]

        de, para = self.origem.cod_tom, self.destino.cod_tom
        txt_tom = (f"{de} → {para} {self.tipo_tom}" if tom_ok
                   else f"Tom incompatível ({de} → {para})")
        txt_bpm = f"BPM {formatar_pct(self.variacao)}"
        if not bpm_ok:
            txt_bpm += f" (acima de {TOLERANCIA_BPM:g}%)"
        self.motivo = f"{txt_tom} · {txt_bpm}"

    @property
    def tom_ok(self) -> bool:
        return self.tipo_tom is not None

    @property
    def bpm_ok(self) -> bool:
        return round(abs(self.variacao), 6) <= TOLERANCIA_BPM

    @property
    def rotulo(self) -> str:
        return {SUAVE: "🟢 Suave", ATENCAO: "🟡 Atenção", ARRISCADA: "🔴 Arriscada"}[self.nivel]


def classificar_transicao(origem, destino) -> Transicao:
    """RN08: Suave (2 critérios), Atenção (1) ou Arriscada (0)."""
    return Transicao(
        origem=origem,
        destino=destino,
        tipo_tom=tipo_compatibilidade(origem.cod_tom, destino.cod_tom),
        variacao=variacao_bpm(origem.bpm, destino.bpm),
    )


# ---------------------------------------------------------------------------
# Análise do setlist (RN09 + RF12/RF13)
# ---------------------------------------------------------------------------
@dataclass
class Analise:
    transicoes: list[Transicao]
    pontuacao: float | None          # None quando há menos de 2 faixas
    duracao_total: int
    bpm_medio: float | None
    qtd_faixas: int

    @property
    def qtd_suaves(self) -> int:
        return sum(1 for t in self.transicoes if t.nivel == SUAVE)

    @property
    def nivel_geral(self) -> str | None:
        """Cor do indicador geral: ≥ 80% suave, ≥ 50% atenção, abaixo disso arriscada."""
        if self.pontuacao is None:
            return None
        if self.pontuacao >= 80:
            return SUAVE
        if self.pontuacao >= 50:
            return ATENCAO
        return ARRISCADA


def analisar_setlist(faixas: list) -> Analise:
    transicoes = [classificar_transicao(a, b) for a, b in zip(faixas, faixas[1:])]
    pontuacao = None
    if transicoes:
        pontuacao = sum(1 for t in transicoes if t.nivel == SUAVE) / len(transicoes) * 100
    bpm_medio = sum(float(f.bpm) for f in faixas) / len(faixas) if faixas else None
    return Analise(
        transicoes=transicoes,
        pontuacao=pontuacao,
        duracao_total=sum(int(f.duracao_seg) for f in faixas),
        bpm_medio=bpm_medio,
        qtd_faixas=len(faixas),
    )


def curva_energia(faixas: list) -> dict:
    """Dados para o gráfico (RF12): posição, título, BPM e energia de cada faixa."""
    return {
        "rotulos": [str(i) for i in range(1, len(faixas) + 1)],
        "titulos": [f.titulo for f in faixas],
        "bpm": [float(f.bpm) for f in faixas],
        "energia": [int(f.energia) for f in faixas],
        "tons": [f.cod_tom for f in faixas],
    }


# ---------------------------------------------------------------------------
# Sugestões (RN11)
# ---------------------------------------------------------------------------
@dataclass
class Sugestao:
    faixa: object
    tipo_tom: str
    variacao: float


def sugerir_proximas(ultima, candidatas: list, limite: int = LIMITE_SUGESTOES) -> list[Sugestao]:
    """Faixas compatíveis em tom E BPM com `ultima`, ordenadas por:
    mesmo tom → vizinho → relativo; depois, menor variação absoluta de BPM.
    `candidatas` já deve excluir as faixas que estão no setlist.
    """
    if ultima is None:
        return []
    sugestoes = []
    for faixa in candidatas:
        if getattr(faixa, "id", None) is not None and faixa.id == getattr(ultima, "id", None):
            continue
        tipo = tipo_compatibilidade(ultima.cod_tom, faixa.cod_tom)
        if tipo is None:
            continue
        var = variacao_bpm(ultima.bpm, faixa.bpm)
        if round(abs(var), 6) > TOLERANCIA_BPM:
            continue
        sugestoes.append(Sugestao(faixa=faixa, tipo_tom=tipo, variacao=var))
    sugestoes.sort(key=lambda s: (_ORDEM_TIPO[s.tipo_tom], abs(s.variacao), s.faixa.titulo))
    return sugestoes[:limite]


# ---------------------------------------------------------------------------
# Utilidades de exibição
# ---------------------------------------------------------------------------
def formatar_pct(valor: float) -> str:
    """+3,3% / −2,5% / 0,0% (formato brasileiro, sinal de menos tipográfico)."""
    if abs(valor) < 0.05:
        return "0,0%"
    sinal = "+" if valor > 0 else "−"
    return f"{sinal}{abs(valor):.1f}%".replace(".", ",")
