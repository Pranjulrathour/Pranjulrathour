"""GitHub stats, drawn by hand from the GraphQL API (no third-party card service): assets/stats-dark.svg and -light.svg.

Runs in .github/workflows/refresh.yml every day with the default GITHUB_TOKEN (public data only), and locally with
`gh auth token`. Also rewrites the numbers between <!-- stats:start --> and <!-- stats:end --> in README.md.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGIN = "Pranjulrathour"
Q = """
query($login:String!){ user(login:$login){
  followers{totalCount} createdAt
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){ totalCount nodes{ isPrivate stargazerCount pushedAt
    languages(first:8, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } } }
  contributionsCollection{ totalCommitContributions restrictedContributionsCount totalPullRequestContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount date } } } }
}}"""


def token() -> str:
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not t:
        t = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    return t


def fetch() -> dict:
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": Q, "variables": {"login": LOGIN}}).encode(),
                                 headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json", "User-Agent": LOGIN})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def summarise(u: dict) -> dict:
    repos = u["repositories"]["nodes"]
    langs: Counter = Counter()
    colors: dict[str, str] = {}
    for r in repos:
        if r["isPrivate"]:
            continue   # language bytes of private repos are not public information; keep the bar public-only
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
            colors[e["node"]["name"]] = e["node"]["color"] or "#8ea8ff"
    total = sum(langs.values()) or 1
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    streak = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            streak += 1
        elif d["date"] != dt.date.today().isoformat():   # today may simply not have happened yet
            break
    best = cur = 0
    for d in days:
        cur = cur + 1 if d["contributionCount"] > 0 else 0
        best = max(best, cur)
    active_days = sum(1 for d in days if d["contributionCount"] > 0)
    return {
        "contributions": cal["totalContributions"], "commits": u["contributionsCollection"]["totalCommitContributions"],
        "private": u["contributionsCollection"]["restrictedContributionsCount"], "prs": u["contributionsCollection"]["totalPullRequestContributions"],
        "repos": u["repositories"]["totalCount"], "public_repos": sum(1 for r in repos if not r["isPrivate"]),
        "stars": sum(r["stargazerCount"] for r in repos), "followers": u["followers"]["totalCount"],
        "streak": streak, "best_streak": best, "active_days": active_days, "days": days[-371:],
        "langs": [(n, s / total * 100, colors[n]) for n, s in langs.most_common(6)],
        "since": u["createdAt"][:4], "updated": dt.date.today().isoformat(),
    }


def svg(s: dict, theme: str) -> str:
    dark = theme == "dark"
    bg, p1, ink, muted, dim, line = ("#09090d", "#101016", "#f4f3f8", "#a09fb0", "#64637a", "rgba(255,255,255,.14)") if dark else \
                                    ("#f6f4ef", "#fdfcf9", "#1c1b22", "#5b5a66", "#8a8896", "rgba(28,27,34,.16)")
    coral, grid = "#ff4d2e", ("rgba(255,255,255,.075)" if dark else "rgba(28,27,34,.14)")
    W, H = 1600, 600
    mono = "font-family=\"'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace\""
    sans = "font-family=\"Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif\""
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs><pattern id="g" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{grid}"/></pattern>'
         f'<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity=".35"/></linearGradient>'
         f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>'
         f'<radialGradient id="glow" cx=".9" cy="1.1" r=".8"><stop offset="0" stop-color="{coral}" stop-opacity=".22"/><stop offset=".6" stop-color="{coral}" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="30" fill="{bg}"/><rect width="{W}" height="{H}" rx="30" fill="url(#glow)"/>',
         f'<rect width="{W}" height="{H}" rx="30" fill="url(#g)" mask="url(#m)"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="29.5" fill="none" stroke="{line}"/>']
    # rail
    o.append(f'<g {mono} font-size="12" letter-spacing="1.9" fill="{dim}"><text x="56" y="44">06 &#160; GITHUB</text>'
             f'<text x="{W/2:.0f}" y="44" text-anchor="middle">LIVE FROM THE GRAPHQL API · REFRESHED DAILY</text>'
             f'<text x="{W-56}" y="44" text-anchor="end">UPDATED {s["updated"]}</text></g>')
    o.append(f'<text x="72" y="104" {mono} font-size="12" letter-spacing="1.9" fill="{coral}">THE LAST 12 MONTHS ON GITHUB</text>')
    # headline numbers
    nums = [(f"{s['contributions']:,}", "contributions"), (f"{s['repos']}", "repositories"), (f"{s['active_days']}", "active days"),
            (f"{s['best_streak']}", "longest streak, days"), (f"{s['followers']}", "followers")]
    for i, (n, l) in enumerate(nums):
        x = 72 + i * 300
        o.append(f'<text x="{x}" y="186" {sans} font-size="64" font-weight="800" letter-spacing="-3" fill="{ink}">{n}</text>'
                 f'<text x="{x}" y="214" {mono} font-size="11" letter-spacing="1.7" fill="{dim}">{l.upper()}</text>')
        if i:
            o.append(f'<line x1="{x-30}" y1="138" x2="{x-30}" y2="214" stroke="{line}"/>')
    # contribution heatmap: 53 weeks x 7 days
    days = s["days"]
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    x0, y0 = 72, 262
    cell = (W - 2 * x0 - 52 * 4) / 53   # 53 week columns fill the frame width
    gap = 4
    mx = max((d["contributionCount"] for d in days), default=1) or 1
    o.append(f'<text x="{x0}" y="{y0-14}" {mono} font-size="11" letter-spacing="1.7" fill="{dim}">CONTRIBUTIONS, ONE SQUARE PER DAY · {s["commits"]:,} PUBLIC COMMITS · {s["private"]:,} PRIVATE</text>')
    for wi, wk in enumerate(weeks):
        for di, d in enumerate(wk):
            c = d["contributionCount"]
            a = 0.08 if c == 0 else min(1.0, 0.25 + 0.75 * (c / mx) ** 0.5)
            fill = (f'rgba(255,255,255,{a:.2f})' if dark else f'rgba(28,27,34,{a:.2f})') if c == 0 else f'rgba(255,77,46,{a:.2f})'
            o.append(f'<rect x="{x0 + wi*(cell+gap):.1f}" y="{y0 + di*(cell+gap):.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="5" fill="{fill}"/>')
    # month labels
    seen = set()
    for wi, wk in enumerate(weeks):
        m = wk[0]["date"][:7]
        if m not in seen and wk[0]["date"][8:10] <= "07":
            seen.add(m)
            o.append(f'<text x="{x0 + wi*(cell+gap):.1f}" y="{y0 + 7*(cell+gap) + 18:.1f}" {mono} font-size="10.5" letter-spacing="1.4" fill="{dim}">'
                     f'{dt.date.fromisoformat(wk[0]["date"]).strftime("%b").upper()}</text>')
    # language bar
    ly = 492
    o.append(f'<text x="72" y="{ly-16}" {mono} font-size="11" letter-spacing="1.7" fill="{dim}">LANGUAGES ACROSS {s["public_repos"]} PUBLIC REPOSITORIES, BY BYTES</text>')
    x = 72
    for n, pct, col in s["langs"]:
        w = max(4, (W - 144) * pct / 100)
        o.append(f'<rect x="{x:.1f}" y="{ly}" width="{w-3:.1f}" height="12" rx="4" fill="{col}"/>')
        x += w
    x = 72
    for n, pct, col in s["langs"]:
        o.append(f'<circle cx="{x+6}" cy="{ly+44}" r="5" fill="{col}"/>'
                 f'<text x="{x+18}" y="{ly+48}" {sans} font-size="14" font-weight="600" fill="{ink}">{n} <tspan fill="{muted}" font-weight="500">{pct:.1f}%</tspan></text>')
        x += 190
    o.append(f'<text x="{W-56}" y="{H-28}" text-anchor="end" {mono} font-size="12" letter-spacing="1.9" fill="{dim}">PRANJUL RATHOUR · SINCE {s["since"]}</text>')
    o.append("</svg>")
    return "\n".join(o)


def update_readme(s: dict) -> None:
    p = ROOT / "README.md"
    if not p.exists():
        return
    t = p.read_text(encoding="utf-8")
    line = (f"**{s['contributions']:,}** contributions in the last year across **{s['repos']}** repositories, "
            f"**{s['active_days']}** active days, longest streak **{s['best_streak']}** days. Updated {s['updated']}.")
    # the line sits on its own row between the markers, so GitHub parses the bold
    new = re.sub(r"(<!-- stats:start -->).*?(<!-- stats:end -->)", lambda m: m.group(1) + "\n" + line + "\n" + m.group(2), t, flags=re.S)
    if new != t:
        p.write_text(new, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    s = summarise(fetch())
    for theme in ("dark", "light"):
        out = ROOT / "assets" / f"stats-{theme}.svg"
        out.write_text(svg(s, theme), encoding="utf-8", newline="\n")
        print(out.relative_to(ROOT), out.stat().st_size // 1024, "KB")
    update_readme(s)
    print({k: v for k, v in s.items() if k not in ("days", "langs")}, [(n, round(p, 1)) for n, p, _ in s["langs"]])
