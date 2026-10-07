"""Render assets/src/<name>.html -> assets/<name>-dark.webp and assets/<name>-light.webp (headless Chrome, 2x).

  python scripts/render.py            # every panel, both themes
  python scripts/render.py hero wins  # some panels

The light theme is selected by loading the same file with ?light (see assets/src/theme.js). Each panel sets its
own height with `--h` on .frame; the screenshot is cropped to it. WebP keeps the transparent rounded corners.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "src"
OUT = ROOT / "assets"
CHROME = next((p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe", shutil.which("google-chrome"), shutil.which("chromium"),
                           shutil.which("chrome")) if p and Path(p).exists()), None)


def render(name: str, theme: str) -> Path:
    html = SRC / f"{name}.html"
    h = int(re.search(r"--h:(\d+)px", html.read_text(encoding="utf-8")).group(1))
    url = html.as_uri() + ("?light" if theme == "light" else "")
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "shot.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--default-background-color=00000000", "--virtual-time-budget=5000", "--allow-file-access-from-files",
                        f"--window-size=1600,{h}", f"--screenshot={shot}", url], check=True, capture_output=True, timeout=180)
        im = Image.open(shot).convert("RGBA").crop((0, 0, 3200, h * 2))
    out = OUT / f"{name}-{theme}.webp"
    im.save(out, "WEBP", quality=88, method=6, alpha_quality=100)
    print(f"{out.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {out.stat().st_size // 1024} KB")
    return out


if __name__ == "__main__":
    if not CHROME:
        raise SystemExit("Chrome not found")
    names = sys.argv[1:] or [p.stem for p in sorted(SRC.glob("*.html"))]
    for n in names:
        for t in ("dark", "light"):
            render(n, t)
