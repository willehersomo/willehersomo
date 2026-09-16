#!/usr/bin/env python3
"""
Gera um banner SVG animado com aspecto de terminal para o README do GitHub.

Uso:
    python3 gen.py                          # gera terminal.svg (tema dark)
    python3 gen.py --theme light -o luz.svg
    python3 gen.py --user seunick --host github

Para mudar o conteudo, edite a lista LINES logo abaixo.
Tipos de linha:
    ("cmd", "...")  -> digitada caractere a caractere, com prompt na frente
    ("out", "...")  -> saida do comando, aparece de uma vez (cor apagada)
    ("acc", "...")  -> saida em destaque (cor de acento)
"""

import argparse
import html
import re

# ---------------------------------------------------------------- conteudo --
USER = "wille"
HOST = "root"
SHELL = "bash"

LINES = [
    ("cmd", "whoami"),
    ("out", "Breno Wille -- Ciencia da Computacao"),
    ("out", "IFSP Presidente Epitacio | 2023-2026"),
    ("cmd", "cat pesquisa.txt"),
    ("out", "Iniciacao Cientifica @ IFSP"),
    ("acc", "Esteganografia com GANs"),
    ("cmd", "ls ~/stack"),
    ("out", "C  Java  Python  Rust  SQL  Assembly"),
    ("cmd", "./contato.sh"),
    ("acc", "-> github.com/willehersomo"),
]

# ------------------------------------------------------------------ layout --
W        = 760     # largura total
FS       = 15      # tamanho da fonte do terminal
CH       = FS * 0.6  # largura de 1 caractere (monoespacada)
LH       = 26      # altura da linha
PAD_X    = 26      # padding lateral
CHROME   = 38      # altura da barra de titulo
TOP      = 28      # espaco entre a barra e a 1a linha (ate a baseline)
BOT      = 24      # espaco depois da ultima linha

# ------------------------------------------------------------------ tempos --
TYPE  = 0.055  # segundos por caractere digitado
PAUSE = 0.42   # pausa depois de digitar um comando
FADE  = 0.16   # fade-in de uma linha de saida
GAP   = 0.10   # intervalo entre linhas de saida
HOLD  = 2.60   # tempo parado no final antes de reiniciar

FONT = ("ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, "
        "'DejaVu Sans Mono', 'Liberation Mono', monospace")

THEMES = {
    "dark": dict(
        bg="#0d1117", chrome="#161b22", border="#30363d", title="#7d8590",
        user="#3fb950", path="#58a6ff", sym="#7d8590",
        cmd="#e6edf3", out="#8b949e", acc="#d2a8ff", cursor="#58a6ff",
    ),
    "light": dict(
        bg="#ffffff", chrome="#f6f8fa", border="#d0d7de", title="#59636e",
        user="#1a7f37", path="#0969da", sym="#59636e",
        cmd="#1f2328", out="#59636e", acc="#8250df", cursor="#0969da",
    ),
}


def build(user, host, theme, lines, shell=SHELL):
    c = THEMES[theme]
    sym = "#" if user == "root" else "$"
    prompt = f"{user}@{host}:~{sym} "
    pw = len(prompt) * CH          # largura do prompt
    tx = PAD_X + pw                # onde o comando comeca

    # ---- linha do tempo ----------------------------------------------------
    t = 0.35
    ev = []                        # (tipo, texto, inicio, fim, fim_do_cursor)
    for kind, text in lines:
        if kind == "cmd":
            dur = max(len(text), 1) * TYPE
            ev.append([kind, text, t, t + dur, t + dur + PAUSE * 0.8])
            t += dur + PAUSE
        else:
            ev.append([kind, text, t, t + FADE, 0.0])
            t += FADE + GAP
    final_at = t + 0.10
    total = final_at + HOLD

    def p(sec):                    # segundos -> % do ciclo
        return round(max(0.02, min(99.98, 100.0 * sec / total)), 3)

    n = len(lines)
    height = CHROME + TOP + n * LH + BOT

    css, body, clips = [], [], []

    css.append(f".tx{{font-family:{FONT};font-size:{FS}px;"
               "font-variant-ligatures:none;white-space:pre}")
    css.append(f".cur{{fill:{c['cursor']}}}")
    css.append("@keyframes bl{0%,49%{opacity:1}50%,100%{opacity:0}}")

    for i, (kind, text, s, e, ce) in enumerate(ev):
        y = CHROME + TOP + i * LH
        a, b = p(s), p(e)
        if b <= a:
            b = a + 0.02
        a2 = round(a + 0.01, 3)
        esc = html.escape(text)

        if kind == "cmd":
            cw = len(text) * CH
            nch = max(len(text), 1)
            cf, ce_ = p(ce), round(p(ce) + 0.01, 3)

            css.append(f"@keyframes v{i}{{0%,{a}%{{opacity:0}}"
                       f"{a2}%,100%{{opacity:1}}}}")
            css.append(f".v{i}{{animation:v{i} {total:.2f}s linear infinite}}")
            css.append(f"@keyframes t{i}{{0%,{a}%{{width:0}}"
                       f"{b}%,100%{{width:{cw:.1f}px}}}}")
            css.append(f".t{i}{{animation:t{i} {total:.2f}s "
                       f"steps({nch}) infinite}}")
            css.append(f"@keyframes x{i}{{0%,{a}%{{x:{tx:.1f}px}}"
                       f"{b}%,100%{{x:{tx + cw:.1f}px}}}}")
            css.append(f".x{i}{{animation:x{i} {total:.2f}s "
                       f"steps({nch}) infinite}}")
            css.append(f"@keyframes k{i}{{0%,{a}%{{opacity:0}}"
                       f"{a2}%,{cf}%{{opacity:1}}{ce_}%,100%{{opacity:0}}}}")
            css.append(f".k{i}{{animation:k{i} {total:.2f}s steps(1) infinite}}")

            clips.append(
                f'<clipPath id="c{i}"><rect class="t{i}" x="{tx:.1f}" '
                f'y="{y - FS + 1}" width="0" height="{FS + 6}"/></clipPath>')
            body.append(
                f'  <g class="v{i}">\n'
                f'    <text class="tx" x="{PAD_X}" y="{y}" '
                f'textLength="{pw:.1f}" lengthAdjust="spacing">'
                f'<tspan fill="{c["user"]}">{html.escape(user)}@'
                f'{html.escape(host)}</tspan>'
                f'<tspan fill="{c["sym"]}">:</tspan>'
                f'<tspan fill="{c["path"]}">~</tspan>'
                f'<tspan fill="{c["sym"]}">{sym} </tspan></text>\n'
                f'    <g clip-path="url(#c{i})">'
                f'<text class="tx" x="{tx:.1f}" y="{y}" fill="{c["cmd"]}" '
                f'textLength="{cw:.1f}" lengthAdjust="spacing">{esc}</text></g>\n'
                f'  </g>\n'
                f'  <g class="k{i}"><rect class="cur x{i}" x="{tx:.1f}" '
                f'y="{y - FS + 2}" width="{CH - 0.5:.1f}" height="{FS + 3}" '
                f'rx="1"/></g>')
        else:
            fill = c["acc"] if kind == "acc" else c["out"]
            css.append(f"@keyframes v{i}{{0%,{a}%{{opacity:0}}"
                       f"{b}%,100%{{opacity:1}}}}")
            css.append(f".v{i}{{animation:v{i} {total:.2f}s linear infinite}}")
            body.append(
                f'  <text class="tx v{i}" x="{PAD_X}" y="{y}" fill="{fill}" '
                f'textLength="{len(text) * CH:.1f}" lengthAdjust="spacing">'
                f'{esc}</text>')

    # prompt final com cursor piscando
    fy = CHROME + TOP + n * LH
    fa = p(final_at)
    css.append(f"@keyframes vf{{0%,{fa}%{{opacity:0}}"
               f"{round(fa + 0.01, 3)}%,100%{{opacity:1}}}}")
    css.append(f".vf{{animation:vf {total:.2f}s steps(1) infinite}}")
    body.append(
        f'  <g class="vf">\n'
        f'    <text class="tx" x="{PAD_X}" y="{fy}" textLength="{pw:.1f}" '
        f'lengthAdjust="spacing">'
        f'<tspan fill="{c["user"]}">{html.escape(user)}@{html.escape(host)}'
        f'</tspan><tspan fill="{c["sym"]}">:</tspan>'
        f'<tspan fill="{c["path"]}">~</tspan>'
        f'<tspan fill="{c["sym"]}">{sym} </tspan></text>\n'
        f'    <rect class="cur" x="{tx:.1f}" y="{fy - FS + 2}" '
        f'width="{CH - 0.5:.1f}" height="{FS + 3}" rx="1" '
        f'style="animation:bl 1.06s steps(1) infinite"/>\n'
        f'  </g>')

    title = html.escape(f"{user}@{host}: ~ — {shell}")
    nl = "\n"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" \
height="{height}" viewBox="0 0 {W} {height}" role="img" \
aria-label="terminal de {html.escape(user)}">
  <title>{title}</title>
  <defs>
    <style><![CDATA[
{nl.join("      " + r for r in css)}
    ]]></style>
{nl.join("    " + r for r in clips)}
  </defs>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="10"
        fill="{c["bg"]}" stroke="{c["border"]}"/>
  <path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v{CHROME - 10}H0.5z"
        fill="{c["chrome"]}"/>
  <path d="M0.5 {CHROME}.5h{W - 1}" stroke="{c["border"]}"/>
  <circle cx="22" cy="19" r="6" fill="#ff5f56"/>
  <circle cx="42" cy="19" r="6" fill="#ffbd2e"/>
  <circle cx="62" cy="19" r="6" fill="#27c93f"/>
  <text x="{W / 2}" y="23.5" text-anchor="middle" fill="{c["title"]}"
        font-family="{FONT}" font-size="12">{title}</text>
{nl.join(body)}
</svg>
'''


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=USER)
    ap.add_argument("--host", default=HOST)
    ap.add_argument("--shell", default=SHELL)
    ap.add_argument("--theme", default="dark", choices=list(THEMES))
    ap.add_argument("-o", "--out", default="terminal.svg")
    args = ap.parse_args()
    svg = build(args.user, args.host, args.theme, LINES, args.shell)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(svg)
    dur = re.search(r"animation:vf ([0-9.]+)s", svg).group(1)
    print(f"{args.out}  ({len(svg)} bytes, tema {args.theme}, ciclo {dur}s)")
