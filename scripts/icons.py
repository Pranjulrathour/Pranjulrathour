"""Theme-aware social icons for the README: assets/icons/<name>.svg (Simple Icons, CC0) -> assets/icons/dark/ and light/.

Dark variants are near-white, light variants carry the brand colour, so the README can swap them with
<picture media="(prefers-color-scheme: dark)">. Also writes the connect.html panel source.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
# name, label, url, brand colour (used on the light theme and on the connect panel tiles)
SOCIALS = [
    ("globe", "Portfolio", "https://pranjulrathour.scult.in", "#ff4d2e"),
    ("linkedin", "LinkedIn", "https://www.linkedin.com/in/pranjul-rathour/", "#0a66c2"),
    ("github", "GitHub", "https://github.com/Pranjulrathour", "#24292f"),
    ("x", "X", "https://x.com/PranjulRathourx", "#111111"),
    ("instagram", "Instagram", "https://www.instagram.com/pranjulrathour.in/", "#e4405f"),
    ("threads", "Threads", "https://www.threads.com/@pranjulrathour.in", "#111111"),
    ("facebook", "Facebook", "https://www.facebook.com/profile.php?id=1377591238763842", "#0866ff"),
    ("bluesky", "Bluesky", "https://bsky.app/profile/pranjulrathour.bsky.social", "#0285ff"),
    ("devdotto", "Dev.to", "https://dev.to/pranjulrathour", "#0a0a0a"),
    ("blogger", "Blogger", "https://pranjulrathourtechguru.blogspot.com/", "#ff5722"),
    ("hashnode", "Hashnode", "https://pranjulrathour.hashnode.dev", "#2962ff"),
    ("gmail", "Email", "mailto:pranjulrathour41@gmail.com", "#ea4335"),
]


def recolor(svg: str, fill: str) -> str:
    svg = re.sub(r'\sfill="[^"]*"', "", svg, count=1)
    return svg.replace("<svg ", f'<svg fill="{fill}" ', 1)


def path_of(svg: str) -> str:
    return re.search(r'<path d="([^"]+)"', svg).group(1)


if __name__ == "__main__":
    (ICONS / "dark").mkdir(exist_ok=True)
    (ICONS / "light").mkdir(exist_ok=True)
    tiles = []
    for name, label, url, color in SOCIALS:
        svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
        (ICONS / "dark" / f"{name}.svg").write_text(recolor(svg, "#f4f3f8"), encoding="utf-8", newline="\n")
        (ICONS / "light" / f"{name}.svg").write_text(recolor(svg, color if color not in ("#111111", "#0a0a0a", "#24292f") else "#1c1b22"),
                                                      encoding="utf-8", newline="\n")
        host = url.replace("https://", "").replace("mailto:", "").rstrip("/")
        tiles.append(f'<a class="t" style="--c:{color}"><span class="ic"><svg viewBox="0 0 24 24"><path d="{path_of(svg)}"/></svg></span>'
                     f'<b>{label}</b><span class="u">{host}</span></a>')
    html = f'''<!doctype html><html><head><meta charset="utf-8"><script src="theme.js"></script><link rel="stylesheet" href="art.css"><style>
.frame{{--h:880px;--gx:50%;--gy:120%}}
.hd h2{{max-width:1150px}}
.tiles{{position:absolute;left:72px;right:72px;top:300px;display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}
.t{{display:grid;grid-template-columns:52px 1fr;grid-template-rows:auto auto;column-gap:16px;align-items:center;padding:18px 20px;border-radius:20px;background:var(--p1);
  box-shadow:inset 0 0 0 1px var(--line);text-decoration:none;color:var(--ink)}}
.t .ic{{grid-row:span 2;width:52px;height:52px;border-radius:15px;display:grid;place-items:center;background:var(--c);box-shadow:0 14px 30px -14px var(--c)}}
.t .ic svg{{width:26px;height:26px;fill:#fff}}
.t b{{font-size:17px;letter-spacing:-.02em}}
.t .u{{font-family:Mono;font-size:11px;color:var(--muted);letter-spacing:.02em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.cta{{position:absolute;left:72px;right:72px;bottom:66px;display:grid;grid-template-columns:96px 1fr auto;gap:24px;align-items:center;padding:22px 26px;border-radius:24px;
  background:linear-gradient(90deg,rgba(255,77,46,.16),transparent 60%),var(--p1);box-shadow:inset 0 0 0 1px rgba(255,77,46,.35)}}
.cta img{{width:96px;height:96px;border-radius:50%;object-fit:cover;object-position:center 15%;box-shadow:0 0 0 4px var(--bg),0 0 0 6px var(--coral)}}
.cta h3{{font-size:30px;letter-spacing:-.035em;line-height:1.05;font-weight:760}}
.cta h3 .serif{{color:var(--coral);font-size:1.1em}}
.cta p{{margin-top:8px;font-size:15px;color:var(--muted)}}
.cta .btn{{display:inline-flex;align-items:center;gap:10px;padding:16px 24px;border-radius:999px;background:var(--coral);color:#fff;font-weight:700;font-size:16px;white-space:nowrap;box-shadow:0 18px 40px -16px var(--coral)}}
</style></head><body><div class="frame">
<span class="reg tl"></span><span class="reg tr"></span><span class="reg bl"></span><span class="reg br"></span>
<div class="rail mono"><span><b>07</b> &nbsp;everywhere</span><span>one person, one bio, one headshot, twelve doors</span><span>fig. 7</span></div>
<div class="hd"><div class="mono k">Find me</div><h2>Same name everywhere. <span class="serif">Say hello anywhere.</span></h2></div>
<div class="tiles">{"".join(tiles)}</div>
<div class="cta"><img src="../photos/headshot.webp"><div><h3>Judge your hackathon. <span class="serif">Speak at your college.</span></h3><p>Guest talks, workshops, mentorship sessions and hackathon judging, on-site across India or remote. Also open to GenAI roles.</p></div><span class="btn">pranjulrathour.scult.in/invite →</span></div>
<div class="foot mono"><span>pranjulrathour41@gmail.com</span><span>pranjul rathour · 2026</span></div>
</div></body></html>
'''
    (ROOT / "assets" / "src" / "connect.html").write_text(html, encoding="utf-8", newline="\n")
    print("icons:", len(SOCIALS), "x dark/light; connect.html written")
