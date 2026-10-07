"""Writes assets/src/stack.html: the tech-stack panel with a brand logo on every chip (Simple Icons, CC0, inlined as paths).
Skills and groups come from the resume's Technical Skills section. Chips without a logo are tools whose marks are not in Simple Icons."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "assets" / "icons" / "tech"

GROUPS = [
    ("ai", "AI / ML / GenAI", "Models to production", [
        ("OpenAI", None), ("Claude", "claude"), ("Gemini", "googlegemini"), ("Mistral", "mistralai"), ("Groq / Llama", "meta"),
        ("Hybrid RAG: dense + BM25", None), ("Re-ranking", None), ("LoRA / QLoRA", "huggingface"), ("Transformers · PEFT · TRL", "huggingface"),
        ("Vector search & embeddings", None), ("LangChain", "langchain"), ("MCP", "modelcontextprotocol"), ("OpenRouter", None),
        ("ONNX Runtime", "onnx"), ("Computer vision", "opencv"), ("PyTorch", "pytorch")]),
    ("be", "Backend", "APIs & data", [
        ("Python", "python"), ("FastAPI", "fastapi"), ("Node.js", "nodedotjs"), ("Express", "express"), ("REST APIs", None), ("WebSockets", "socketdotio"),
        ("PostgreSQL", "postgresql"), ("MongoDB", "mongodb"), ("Supabase", "supabase"), ("Firebase", "firebase"), ("Redis", "redis")]),
    ("fe", "Frontend & vector stores", "Interfaces & search", [
        ("TypeScript", "typescript"), ("JavaScript", "javascript"), ("React", "react"), ("Next.js", "nextdotjs"), ("Tailwind CSS", "tailwindcss"),
        ("shadcn/ui", "shadcnui"), ("Redux · Zustand", "redux"), ("HTML5", "html5"), ("CSS3", "css"), ("FAISS", None), ("Qdrant", "qdrant"), ("pgvector", "postgresql")]),
    ("ops", "Cloud & delivery", "Ship it", [
        ("Docker", "docker"), ("AWS", "aws"), ("Railway", "railway"), ("Vercel", "vercel"), ("Git", "git"), ("GitHub", "github"),
        ("GitHub Actions", "githubactions"), ("CI/CD", None), ("Structured logging & metrics", None)]),
]


def icon(name: str | None) -> str:
    if not name:
        return ""
    svg = (T / f"{name}.svg").read_text(encoding="utf-8")
    inner = re.sub(r"<title>.*?</title>", "", re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1), flags=re.S)
    inner = re.sub(r'\sfill="(?!none)[^"]*"', "", inner)          # monochrome: fill comes from CSS currentColor
    vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
    return f'<svg viewBox="{vb}" aria-hidden="true">{inner}</svg>'


chips = ""
for key, kicker, title, items in GROUPS:
    row = "".join(f'<span class="chip{" nologo" if not ic else ""}">{icon(ic)}{label}</span>' for label, ic in items)
    chips += f'<div class="g {key}"><span class="mono">{kicker}</span><h3>{title}</h3><div class="row">{row}</div></div>\n'

html = f'''<!doctype html><html><head><meta charset="utf-8"><script src="theme.js"></script><link rel="stylesheet" href="art.css"><style>
.frame{{--h:900px;--gx:95%;--gy:-20%}}
.cols{{position:absolute;left:72px;right:72px;top:276px;display:grid;grid-template-columns:1.5fr 1fr 1.15fr 1fr;gap:16px}}
.g{{padding:22px 22px 20px;border-radius:24px;background:var(--p1);box-shadow:inset 0 0 0 1px var(--line);min-height:440px}}
.g .mono{{color:var(--coral);font-size:11px}}
.g h3{{margin-top:10px;font-size:22px;letter-spacing:-.025em;font-weight:740}}
.g .row{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
.g .chip{{font-size:13px;padding:7px 12px 7px 9px;gap:8px;color:var(--ink)}}
.g .chip svg{{width:16px;height:16px;fill:currentColor;flex:none;opacity:.95}}
.g .chip.nologo{{padding-left:12px}}
.g.ai{{background:linear-gradient(180deg,rgba(255,77,46,.14),transparent 60%),var(--p1);box-shadow:inset 0 0 0 1px rgba(255,77,46,.4)}}
.g.ai .chip{{background:var(--coralsoft);box-shadow:inset 0 0 0 1px rgba(255,77,46,.35)}}
.g.ai .chip svg{{color:var(--coral)}}
.pr{{position:absolute;left:72px;right:72px;bottom:66px;display:flex;gap:14px;align-items:center;padding:18px 24px;border-radius:20px;background:var(--p1);box-shadow:inset 0 0 0 1px var(--line);color:var(--muted);font-size:15px}}
.pr .mono{{color:var(--coral);flex:none}}
.pr b{{color:var(--ink);font-weight:600}}
</style></head><body><div class="frame">
<span class="reg tl"></span><span class="reg tr"></span><span class="reg bl"></span><span class="reg br"></span>
<div class="rail mono"><span><b>04</b> &nbsp;stack</span><span>what the five production apps are actually made of</span><span>fig. 4</span></div>
<div class="hd"><div class="mono k">Tools I ship with</div><h2>Python for the models, <span class="serif">TypeScript for the people.</span></h2></div>
<div class="cols">
{chips}</div>
<div class="pr"><span class="mono">how I work</span><span>Every one of the five NextUpgrad apps shipped <b>end to end with Docker, CI/CD, structured logging and metrics</b>. RAG.NextUpgrad runs in about <b>220 MB on a free tier</b> because hosted embeddings replaced a 500 MB local torch stack.</span></div>
<div class="foot mono"><span>skills as listed on the resume · logos: simple icons (cc0)</span><span>pranjul rathour · 2026</span></div>
</div></body></html>
'''
(ROOT / "assets" / "src" / "stack.html").write_text(html, encoding="utf-8", newline="\n")
print("stack.html written")
