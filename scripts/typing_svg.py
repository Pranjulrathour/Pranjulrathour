"""Self-hosted animated "typing" SVG for the README (SMIL, no external service): assets/typing-dark.svg / -light.svg.

Each line types in character by character (a widening clip), holds, then the next line replaces it. The cursor
blinks the whole time. GitHub renders SMIL animations inside <img> SVGs, so nothing else is needed.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
LINES = [
    "GenAI engineer in Kanpur, India",
    "Production RAG that refuses to hallucinate",
    "Fine-tuning open models on a budget",
    "Vision, OCR and speech in real products",
    "CTO & co-founder, SCULT INDIA",
    "3x hackathon first prizes in 2025",
    "Mentor to 200+ students, speaker at colleges",
    "Open to GenAI roles, talks and hackathon judging",
]
W, H, FS = 900, 60, 26
CHAR_W = FS * 0.6          # JetBrains Mono / Fira Code advance ~0.6em; the clip widens by this per character
TYPE_S, HOLD_S, GAP_S = 0.045, 2.2, 0.35


def build(theme: str) -> str:
    ink = "#f4f3f8" if theme == "dark" else "#1c1b22"
    coral = "#ff4d2e"
    total = sum(len(l) * TYPE_S + HOLD_S + GAP_S for l in LINES)
    parts, t = [], 0.0
    for i, line in enumerate(LINES):
        typing = len(line) * TYPE_S
        w = len(line) * CHAR_W + 6
        start, done, end = t, t + typing, t + typing + HOLD_S
        # the clip rectangle grows from 0 to the line's width while "typing", stays, then collapses
        parts.append(f'''<clipPath id="c{i}"><rect x="0" y="0" width="0" height="{H}">
  <animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0;0" keyTimes="0;{start/total:.4f};{done/total:.4f};{end/total:.4f};{(end+0.001)/total:.4f};1" dur="{total:.2f}s" repeatCount="indefinite" calcMode="linear"/>
</rect></clipPath>
<text x="0" y="{H*0.66:.0f}" clip-path="url(#c{i})" font-size="{FS}" font-weight="600" fill="{ink}" xml:space="preserve">{escape(line)}</text>''')
        # the cursor follows the clip edge for this line
        parts.append(f'''<rect y="{H*0.66-FS*0.8:.0f}" width="3" height="{FS*0.95:.0f}" rx="1" fill="{coral}" opacity="0">
  <animate attributeName="x" values="0;0;{w:.0f};{w:.0f};0;0" keyTimes="0;{start/total:.4f};{done/total:.4f};{end/total:.4f};{(end+0.001)/total:.4f};1" dur="{total:.2f}s" repeatCount="indefinite" calcMode="linear"/>
  <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{start/total:.4f};{(start+0.001)/total:.4f};{end/total:.4f};{(end+0.001)/total:.4f};1" dur="{total:.2f}s" repeatCount="indefinite"/>
</rect>''')
        t = end + GAP_S
    body = "\n".join(parts)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">
<title>Pranjul Rathour</title>
<style>rect.blink{{animation:b 1s steps(2,start) infinite}}@keyframes b{{to{{visibility:hidden}}}}</style>
<text x="0" y="{H*0.66:.0f}" font-size="{FS}" fill="{coral}" font-weight="600">&#8250;</text>
<g transform="translate(26 0)">
{body}
</g>
</svg>
'''


if __name__ == "__main__":
    for theme in ("dark", "light"):
        out = ROOT / "assets" / f"typing-{theme}.svg"
        out.write_text(build(theme), encoding="utf-8", newline="\n")
        print(out.relative_to(ROOT), out.stat().st_size // 1024, "KB")
