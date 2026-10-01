"""Gera 5 logos SVG para o Dr. Fábio Matheus seguindo a Identidade Visual FM.

Texto convertido em contornos (Jost) para o SVG renderizar igual em qualquer lugar.
"""
import math
import os
import sys

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# Paleta monocromática do design system
ONIX = "#0E0E0E"
BRANCO = "#FFFFFF"
ESMALTE = "#F2F1EE"
NEVOA = "#BDBDBA"
GRAFITE = "#3A3A3A"
CINZA = "#5A5A57"


class Face:
    def __init__(self, wght):
        f = TTFont(os.path.join(HERE, "Jost.ttf"))
        self.font = instantiateVariableFont(f, {"wght": wght})
        self.gs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    def adv(self, ch):
        return self.hmtx[self.cmap[ord(ch)]][0]

    def glyph_d(self, ch, s, x=0.0, y=0.0):
        pen = SVGPathPen(self.gs)
        self.gs[self.cmap[ord(ch)]].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
        return pen.getCommands()

    def width(self, text, size, track=0.0):
        s = size / self.upm
        w = sum(self.adv(c) * s for c in text)
        return w + track * size * (len(text) - 1)

    def text(self, text, size, x, y, track=0.0, anchor="start", fill=ONIX):
        """Texto em linha reta; y é a linha de base."""
        s = size / self.upm
        w = self.width(text, size, track)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        ds = []
        for c in text:
            if c != " ":
                ds.append(self.glyph_d(c, s, x, y))
            x += self.adv(c) * s + track * size
        return f'<path fill="{fill}" d="{" ".join(ds)}"/>', w

    def arc(self, text, size, cx, cy, r, track=0.0, bottom=False, fill=ONIX):
        """Texto em arco centrado no topo (ou na base) de um círculo.

        Topo: linha de base no raio r, letras para fora.
        Base: linha de base no raio r, topo das letras para o centro.
        """
        s = size / self.upm
        cap = 0.7 * size
        rmid = r + cap / 2 if not bottom else r - cap / 2
        total = self.width(text, size, track)
        pos = -total / 2
        out = []
        for c in text:
            a = self.adv(c) * s
            centre = pos + a / 2
            ang = math.degrees(centre / rmid)
            if c != " ":
                d = self.glyph_d(c, s, -a / 2, 0)
                if not bottom:
                    t = f"translate({cx:.2f} {cy:.2f}) rotate({ang:.3f}) translate(0 {-r:.2f})"
                else:
                    t = f"translate({cx:.2f} {cy:.2f}) rotate({-ang:.3f}) translate(0 {r:.2f})"
                out.append(f'<path transform="{t}" d="{d}"/>')
            pos += a + track * size
        return f'<g fill="{fill}">{"".join(out)}</g>'


LIGHT = Face(300)
REG = Face(400)

# Monograma oficial (viewBox do design system: x 14..96, y 10..110)
MONO_PATH = "M14 110V10H44V110M14 54H34M44 10L70 80L96 10V110"
MONO_DOT = (70, 96)


def monogram(cx, top, height, color, stroke=1.6, dot_r=2.4, path=MONO_PATH, dot=MONO_DOT):
    s = height / 100.0
    x0 = cx - 55 * s
    y0 = top - 10 * s
    return (
        f'<g transform="translate({x0:.2f} {y0:.2f}) scale({s:.4f})">'
        f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{stroke}" '
        f'stroke-linecap="square" stroke-linejoin="miter"/>'
        f'<circle cx="{dot[0]}" cy="{dot[1]}" r="{dot_r}" fill="{color}"/></g>'
    )


def svg(w, h, bg, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f"<title>{title}</title>"
        f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>\n'
    )


def hline(x1, x2, y, color, w=1.6):
    return f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width="{w}"/>'


def lined_caption(face, text, size, track, cx, y, x_left, x_right, color, line_color, gap):
    """Legenda centralizada com um filete de cada lado (até x_left / x_right)."""
    p, w = face.text(text, size, cx, y, track, "middle", color)
    ly = y - size * 0.36
    return p + hline(x_left, cx - w / 2 - gap, ly, line_color) + hline(cx + w / 2 + gap, x_right, ly, line_color)


# 1 · Assinatura Cúspide — vertical, positivo -------------------------------
def logo1():
    W = H = 1200
    cx = 600
    body = [monogram(cx, 200, 330, ONIX, stroke=1.5, dot_r=2.4)]
    name = "FÁBIO MATHEUS"
    nw = LIGHT.width(name, 82, 0.14)
    left = cx - nw / 2
    dr, _ = LIGHT.text("Dr.", 32, left, 662, 0.04)
    nm, _ = LIGHT.text(name, 82, left, 760, 0.14)
    body += [dr, nm]
    body.append(lined_caption(REG, "CIRURGIÃO-DENTISTA", 24, 0.5, cx, 846, left, left + nw, ONIX, ONIX, 30))
    return svg(W, H, BRANCO, '<g transform="translate(0 64)">' + "".join(body) + "</g>", "Dr. Fábio Matheus — Assinatura Cúspide")


# 2 · Selo Esmalte — circular, negativo --------------------------------------
def logo2():
    W = H = 1200
    cx = cy = 600
    R = 430
    body = [
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{ESMALTE}" stroke-width="2"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{R - 118}" fill="none" stroke="{GRAFITE}" stroke-width="1.6"/>',
        LIGHT.arc("DR. FÁBIO MATHEUS", 40, cx, cy, R - 78, 0.32, False, ESMALTE),
        REG.arc("CIRURGIÃO-DENTISTA", 28, cx, cy, R - 58, 0.42, True, NEVOA),
    ]
    # Pontos laterais: o elemento "linha e ponto" do sistema
    rd = R - 64
    for sx in (-1, 1):
        body.append(f'<circle cx="{cx + sx * rd:.2f}" cy="{cy}" r="5" fill="{ESMALTE}"/>')
    body.append(monogram(cx, cy - 165, 330, ESMALTE, stroke=1.7, dot_r=2.6))
    return svg(W, H, ONIX, "".join(body), "Dr. Fábio Matheus — Selo Esmalte")


# 3 · Arco — horizontal com o monograma sob um arco ---------------------------
def logo3():
    W, H = 1600, 900
    cy = 450
    # Arco: semicírculo no topo, laterais retas, aberto na base (moldura de "coroa")
    ax, aw, ah = 250, 300, 420
    top = cy - ah / 2
    r = aw / 2
    arch = (
        f'<path d="M{ax:.2f} {top + ah:.2f}V{top + r:.2f}A{r:.2f} {r:.2f} 0 0 1 {ax + aw:.2f} {top + r:.2f}V{top + ah:.2f}" '
        f'fill="none" stroke="{ONIX}" stroke-width="2.4" stroke-linecap="square"/>'
    )
    mono = monogram(ax + aw / 2, top + r - 20, 220, ONIX, stroke=1.9, dot_r=2.8)
    base = hline(ax - 40, ax + aw + 40, top + ah, ONIX, 2.4)
    divx = ax + aw + 110
    div = f'<line x1="{divx}" y1="{cy - 120}" x2="{divx}" y2="{cy + 120}" stroke="{CINZA}" stroke-width="1.6"/>'
    tx = divx + 110
    nm, nw = LIGHT.text("FÁBIO MATHEUS", 68, tx, cy + 6, 0.12)
    sub, _ = REG.text("CIRURGIÃO-DENTISTA", 22, tx, cy + 76, 0.42, fill=GRAFITE)
    dr, _ = LIGHT.text("Dr.", 28, tx, cy - 82, 0.04)
    body = arch + mono + base + div + dr + nm + sub
    return svg(W, H, ESMALTE, body, "Dr. Fábio Matheus — Arco")


# 4 · Tipográfica Cúspide — o M de MATHEUS vira dente ------------------------
def logo4():
    W, H = 1600, 900
    cx = 800
    size = 112
    track = 0.12
    first, mrest = "FÁBIO ", "ATHEUS"
    s = size / LIGHT.upm
    # Largura do M desenhado à mão (proporcional ao M do Jost)
    m_adv = LIGHT.adv("M") * s
    total = LIGHT.width(first, size, track) + track * size + m_adv + track * size + LIGHT.width(mrest, size, track)
    x = cx - total / 2
    base = 470
    a, w1 = LIGHT.text(first, size, x, base, track)
    x += w1 + track * size
    # M monolinear: hastes até a linha de base, V afundando até a base (cúspide) + ponto abaixo
    cap = 0.7 * size
    stem = 5.6  # aproxima a haste do Jost Light neste tamanho
    sb = 0.09 * m_adv
    mx1, mx2 = x + sb + stem / 2, x + m_adv - sb - stem / 2
    mxm = (mx1 + mx2) / 2
    m = (
        f'<path d="M{mx1:.2f} {base:.2f}V{base - cap:.2f}L{mxm:.2f} {base - 10:.2f}L{mx2:.2f} {base - cap:.2f}V{base:.2f}" '
        f'fill="none" stroke="{ONIX}" stroke-width="{stem}" stroke-linejoin="miter" stroke-miterlimit="10"/>'
        f'<circle cx="{mxm:.2f}" cy="{base + 30:.2f}" r="6.5" fill="{ONIX}"/>'
    )
    x += m_adv + track * size
    b, _ = LIGHT.text(mrest, size, x, base, track)
    # Divisor linha e ponto + ODONTOLOGIA
    dy = 600
    half = 170
    divider = (
        hline(cx - half, cx - 22, dy, ONIX) + f'<circle cx="{cx}" cy="{dy}" r="5" fill="{ONIX}"/>' + hline(cx + 22, cx + half, dy, ONIX)
    )
    od, _ = REG.text("ODONTOLOGIA", 26, cx, dy + 78, 0.5, "middle", CINZA)
    return svg(W, H, BRANCO, a + m + b + divider + od, "Dr. Fábio Matheus — Tipográfica Cúspide")


# 5 · Traço Único — o braço do F corre direto para a cúspide do M -------------
TRACO_PATH = "M14 110V10H44L70 80L96 10V110M14 54H34"


def logo5():
    W = H = 1200
    cx = 600
    body = [monogram(cx, 210, 360, ESMALTE, stroke=1.4, dot_r=2.3, path=TRACO_PATH)]
    # Filete com ponto sob o símbolo
    nm, nw = LIGHT.text("FÁBIO MATHEUS", 72, cx, 760, 0.16, "middle", ESMALTE)
    body.append(nm)
    body.append(lined_caption(REG, "CIRURGIÃO-DENTISTA", 22, 0.5, cx, 840, cx - nw / 2, cx + nw / 2, NEVOA, CINZA, 28))
    return svg(W, H, GRAFITE, '<g transform="translate(0 64)">' + "".join(body) + "</g>", "Dr. Fábio Matheus — Traço Único")


LOGOS = {
    "01-assinatura-cuspide": logo1,
    "02-selo-esmalte": logo2,
    "03-arco": logo3,
    "04-tipografica-cuspide": logo4,
    "05-traco-unico": logo5,
}

if __name__ == "__main__":
    for name, fn in LOGOS.items():
        with open(os.path.join(OUT, f"{name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(fn())
        print("ok", name)
