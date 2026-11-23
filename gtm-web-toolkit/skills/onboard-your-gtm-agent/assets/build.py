#!/usr/bin/env python3
"""Build the onboarding assets from one data source.

Writes, next to this script:
  benchmark-chart.svg  the benchmark scatter as static SVG (no JS, light/dark aware)
  benchmark-chart-light.svg / -dark.svg  fixed-theme copies with a solid background, for the GitHub README
  onboarding.html      chart + use-case tiles + integrations tile, self-contained (no scripts, no CDN)
  onboarding-inline.html  the same chart + tiles as a bare fragment (no doctype, no page background)
                       to pass verbatim to an inline chat widget
  onboarding.png       a screenshot of onboarding.html (needs Google Chrome)

Run after any change to the benchmark numbers or tile copy:
  python3 skills/onboard-your-gtm-agent/assets/build.py
The numbers must match benchmark/README.md and the table in ../SKILL.md.
"""
import html
import pathlib
import shutil
import subprocess

HERE = pathlib.Path(__file__).resolve().parent

TITLE = "Deep research task comparison for GTM"
CAPTION = "GTM Use-Case Benchmark v2, 10 tasks, November 2026. Higher and further left is better."

# (provider, combined accuracy + coverage score, cost per run in USD). Nimble first = accent.
# Firecrawl's average is $0.096; it is plotted at $0.10 like the other price-matched APIs.
PROVIDERS = [
    ("Nimble", 0.497, 0.10),
    ("GPT-6.1 Sol", 0.448, 0.21),
    ("Exa", 0.405, 0.10),
    ("Parallel", 0.357, 0.10),
    ("Firecrawl", 0.316, 0.10),
]

# (title, API line, what it does, chip label, agents or sources it uses, example prompt)
TILES = [
    ("Meeting prep & buying signals", "Web Search Agents API",
     "Cited account briefs before a call, and what changed at an account or a whole watchlist since a date.",
     "Agents", ["Account brief", "Account signals", "Buying trigger monitor"],
     "Prepare me for a meeting with Gong (gong.io)."),
    ("People research", "Search + Web Search Agents APIs",
     "Who holds a role, verified as current, in seconds; deeper person briefs, buying committees and job-change checks.",
     "Agents", ["Decision makers", "Person brief", "Buying committee map", "Job change monitor", "People discovery"],
     "Who is Gong's CRO today, and since when?"),
    ("Competitive & brand intel", "Web Search Agents API",
     "Battlecards and pricing comparisons, plus what buyers, influencers and execs say about a brand online.",
     "Agents", ["Competitive intelligence", "Brand intelligence", "Social media monitor"],
     "Compare Slack, Teams and Google Chat on pricing."),
    ("Lists & CRM enrichment", "Web Search Agents + Search APIs",
     "ICP and local account lists with near-misses; CRM fields filled in batches, with sources and conflicts kept.",
     "Agents", ["ICP discovery", "Account discovery", "Local business discovery", "CRM enrichment"],
     "Find US legal AI companies, Series A to C, hiring AEs."),
    ("Fast search", "Search + Extract APIs",
     "Single facts in seconds, from first-party pages before aggregators, each with a dated citation.",
     "Sources", ["Company sites", "Newsrooms", "Careers & ATS boards", "Press"],
     "Did Clay raise a round this year?"),
    ("GTM data at scale", "Extract Templates + Jobs API",
     "Signals tracked over time from 800+ Extract Templates: batches of up to 1,000 inputs or scheduled jobs.",
     "Templates", ["LinkedIn & Indeed jobs", "G2 & Glassdoor reviews", "Google Maps", "ChatGPT & Perplexity answers"],
     "Track sales hiring at my top 200 accounts weekly."),
]
INTEGRATE_TITLE = "Try asking Nimble your most complex web research questions"
INTEGRATE_TEXT = "Once you're done testing, call the same APIs from your own apps and agents (MCP, SDK, CLI, & more):"
INTEGRATE_URL = "https://docs.nimbleway.com/integrations/overview"

# Plot geometry (viewBox units).
W, H = 640, 300
L, R, T, B = 64, 560, 16, 248
X_MAX = 0.25
Y_MIN, Y_MAX = 0.28, 0.52
Y_STEP, X_STEP = 0.04, 0.05


def px(cost):
    return L + cost / X_MAX * (R - L)


def py(score):
    return B - (score - Y_MIN) / (Y_MAX - Y_MIN) * (B - T)


def chart_svg(standalone):
    e = html.escape
    out = []
    style = """
  .grid{stroke:#e1e0d9;stroke-width:1}
  .axis{stroke:#c3c2b7;stroke-width:1}
  .tick{fill:#898781;font-size:11px}
  .ttl{fill:#52514e;font-size:12px}
  .lbl{fill:#52514e;font-size:12px}
  .lbl.n{fill:#2a78d6;font-weight:600}
  .pt{fill:#888780;stroke:#fcfcfb;stroke-width:2}
  .pt.n{fill:#2a78d6}
  @media (prefers-color-scheme: dark){
    .grid{stroke:#2c2c2a}.axis{stroke:#383835}
    .ttl,.lbl{fill:#c3c2b7}.lbl.n,.pt.n{fill:#3987e5}.pt{stroke:#1a1a19}
  }"""
    ns = ' xmlns="http://www.w3.org/2000/svg"' if standalone else ""
    out.append(f'<svg{ns} viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="bc-title bc-desc" '
               f'font-family="system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif">')
    out.append(f'<title id="bc-title">{e(TITLE)}</title>')
    desc = "; ".join(f"{n} {s:.3f} at ${c:.2f}" for n, s, c in PROVIDERS)
    out.append(f'<desc id="bc-desc">Accuracy + coverage score versus cost per run. {e(desc)}.</desc>')
    if standalone:
        out.append(f"<style>{style}\n</style>")
    for i in range(round((Y_MAX - Y_MIN) / Y_STEP) + 1):
        v = Y_MIN + i * Y_STEP
        y = py(v)
        out.append(f'<line class="{"axis" if i == 0 else "grid"}" x1="{L}" x2="{R}" y1="{y:.1f}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{L - 8}" y="{y + 4:.1f}" text-anchor="end">{v:.2f}</text>')
    for i in range(round(X_MAX / X_STEP) + 1):
        v = i * X_STEP
        x = px(v)
        out.append(f'<text class="tick" x="{x:.1f}" y="{B + 18}" text-anchor="middle">${v:.2f}</text>')
    out.append(f'<text class="ttl" x="{(L + R) / 2:.0f}" y="{H - 6}" text-anchor="middle">Cost per run (USD)</text>')
    out.append(f'<text class="ttl" transform="translate(14 {(T + B) / 2:.0f}) rotate(-90)" text-anchor="middle">Accuracy + coverage score</text>')
    for i, (name, score, cost) in enumerate(PROVIDERS):
        x, y = px(cost), py(score)
        n = " n" if i == 0 else ""
        r = 7 if i == 0 else 5.5
        out.append(f'<circle class="pt{n}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
        out.append(f'<text class="lbl{n}" x="{x + 11:.1f}" y="{y + 4:.1f}">{e(name)}</text>')
    out.append("</svg>")
    return "\n".join(out), style


LIGHT = dict(grid="#e1e0d9", axis="#c3c2b7", tick="#898781", ink="#52514e", accent="#2a78d6", pt="#888780", bg="#ffffff")
DARK = dict(grid="#2c2c2a", axis="#383835", tick="#898781", ink="#c3c2b7", accent="#3987e5", pt="#888780", bg="#0d1117")


def fixed_svg(svg, theme):
    """Standalone chart with one fixed theme and a solid background (GitHub <picture>)."""
    c = theme
    style = (f".grid{{stroke:{c['grid']};stroke-width:1}}.axis{{stroke:{c['axis']};stroke-width:1}}"
             f".tick{{fill:{c['tick']};font-size:11px}}.ttl,.lbl{{fill:{c['ink']};font-size:12px}}"
             f".hd{{fill:{c['ink']};font-size:15px;font-weight:600}}"
             f".lbl.n{{fill:{c['accent']};font-weight:600}}.pt{{fill:{c['pt']};stroke:{c['bg']};stroke-width:2}}.pt.n{{fill:{c['accent']}}}")
    head, body = svg.split(">", 1)
    head = head.replace(f'viewBox="0 0 {W} {H}"', f'viewBox="0 -34 {W} {H + 34}"')
    return (f"{head}>\n<style>{style}</style>\n<rect x=\"0\" y=\"-34\" width=\"{W}\" height=\"{H + 34}\" fill=\"{c['bg']}\"/>\n"
            f"<text class=\"hd\" x=\"{L}\" y=\"-10\">{html.escape(TITLE)}</text>\n"
            + body.split("</style>", 1)[-1] if "</style>" in body else body)


def inline_fragment(svg, svg_style):
    """Chart + tiles as a bare HTML fragment for inline chat widgets: no doctype, no body, transparent
    background, host CSS variables with fallbacks."""
    e = html.escape
    tiles = "\n".join(
        f'<div class="nb-tile"><p class="nb-t">{e(t)}</p><p class="nb-api">{e(api)}</p>'
        f'<p class="nb-d">{e(d)}</p><p class="nb-cl">{e(cl)}</p><p class="nb-cs">'
        + "".join(f'<span class="nb-c">{e(c)}</span>' for c in chips)
        + f'</p><p class="nb-ex">&ldquo;{e(ex)}&rdquo;</p></div>' for t, api, d, cl, chips, ex in TILES)
    return f'''<style>
.nb{{color:var(--text-primary,#0b0b0b);font-family:var(--font-sans,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif);padding:4px 0}}
.nb p{{margin:0}}
.nb-h{{font-size:16px;font-weight:500;margin:0 0 4px!important}}
.nb-cap{{font-size:12px;color:var(--text-muted,#898781);margin:2px 0 18px!important}}
.nb-h2{{font-size:15px;font-weight:500;margin:0 0 10px!important}}
.nb-sub{{font-size:13px;color:var(--text-secondary,#52514e);margin:-6px 0 12px!important}}
.nb-g{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}
@media (max-width:520px){{.nb-g{{grid-template-columns:1fr}}}}
.nb-tile:last-child:nth-child(odd){{grid-column:1/-1}}
.nb-tile{{background:var(--surface-2,transparent);border:0.5px solid var(--border,rgba(127,127,127,.35));border-radius:12px;padding:12px 14px}}
.nb-t{{font-weight:500;font-size:14px}}
.nb-api{{font-size:12px;color:var(--text-accent,#2a78d6);margin:2px 0 6px!important}}
.nb-d{{font-size:13px;line-height:1.5;color:var(--text-secondary,#52514e);margin-bottom:6px!important}}
.nb-cl{{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted,#898781);margin-bottom:4px!important}}
.nb-cs{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px!important}}
.nb-c{{font-size:11px;line-height:1.4;padding:2px 8px;border-radius:999px;background:var(--surface-1,rgba(42,120,214,.08));border:0.5px solid var(--border,rgba(42,120,214,.25));color:var(--text-secondary,#52514e)}}
.nb-tile{{display:flex;flex-direction:column}}
.nb-ex{{font-size:12px;color:var(--text-muted,#898781);font-style:italic;margin-top:auto!important}}
.nb-w{{background:var(--surface-1,rgba(127,127,127,.08));border-radius:12px;padding:12px 14px;margin-top:10px;font-size:13px;line-height:1.5}}
.nb-w a{{color:var(--text-accent,#2a78d6)}}
{svg_style}
</style>
<div class="nb">
<p class="nb-h">{e(TITLE)}</p>
{svg}
<p class="nb-cap">{e(CAPTION)}</p>
<p class="nb-h2">Test Nimble's APIs on these use cases, right here in your AI.</p>
<p class="nb-sub">16 GTM Web Search Agents plus Search, Extract and 800+ Extract Templates. Ask in plain language; your AI picks the right one.</p>
<div class="nb-g">
{tiles}
</div>
<div class="nb-w"><p style="font-weight:500">{e(INTEGRATE_TITLE)}</p>
<p style="color:var(--text-secondary,#52514e)">{e(INTEGRATE_TEXT)} <a href="{INTEGRATE_URL}">{INTEGRATE_URL.removeprefix("https://")}</a></p></div>
</div>
'''


def page_html(svg, svg_style):
    e = html.escape
    tiles = "\n".join(
        f'''    <div class="tile">
      <p class="t">{e(t)}</p>
      <p class="api">{e(api)}</p>
      <p class="d">{e(d)}</p>
      <p class="cl">{e(cl)}</p>
      <p class="cs">{"".join(f'<span class="c">{e(c)}</span>' for c in chips)}</p>
      <p class="ex">&ldquo;{e(ex)}&rdquo;</p>
    </div>''' for t, api, d, cl, chips, ex in TILES)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nimble for GTM research</title>
<style>
  :root{{--bg:#ffffff;--card:#ffffff;--soft:#f6f5f2;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--line:rgba(11,11,11,.12);--accent:#2a78d6;--chip:#eef4fc;--chipline:#cfe0f5}}
  @media (prefers-color-scheme: dark){{:root{{--bg:#1a1a19;--card:#232321;--soft:#2a2a28;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--line:rgba(255,255,255,.12);--accent:#3987e5;--chip:#1f2a38;--chipline:#2f4560}}}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
  main{{max-width:720px;margin:0 auto;padding:20px 16px 24px}}
  h1{{font-size:17px;font-weight:600;margin:0 0 4px}}
  .cap{{font-size:12px;color:var(--muted);margin:2px 0 20px}}
  h2{{font-size:15px;font-weight:600;margin:0 0 10px}}
  .grid4{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}
  @media (max-width:560px){{.grid4{{grid-template-columns:1fr}}}}
  .tile:last-child:nth-child(odd){{grid-column:1/-1}}
  .tile{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px}}
  .tile p{{margin:0}}
  .t{{font-weight:600;font-size:14px}}
  .api{{font-size:12px;color:var(--accent);margin:2px 0 6px!important}}
  .d{{font-size:13px;color:var(--ink2);margin-bottom:6px!important}}
  .tile{{display:flex;flex-direction:column}}
  .cl{{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin-bottom:4px!important}}
  .cs{{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px!important}}
  .c{{font-size:11px;line-height:1.4;padding:2px 8px;border-radius:999px;background:var(--chip);border:1px solid var(--chipline);color:var(--ink2)}}
  .ex{{font-size:12px;color:var(--muted);font-style:italic;margin-top:auto!important}}
  .sub{{font-size:13px;color:var(--ink2);margin:-6px 0 12px}}
  .wide{{background:var(--soft);border-radius:12px;padding:12px 14px;margin-top:10px;font-size:13px}}
  .wide p{{margin:0}}
  .wide a{{color:var(--accent)}}
  {svg_style}
</style>
</head>
<body>
<main>
  <h1>{e(TITLE)}</h1>
  {svg}
  <p class="cap">{e(CAPTION)}</p>
  <h2>Test Nimble's APIs on these use cases, right here in your AI.</h2>
  <p class="sub">16 GTM Web Search Agents plus Search, Extract and 800+ Extract Templates. Ask in plain language; your AI picks the right one.</p>
  <div class="grid4">
{tiles}
  </div>
  <div class="wide">
    <p><strong>{e(INTEGRATE_TITLE)}</strong></p>
    <p style="color:var(--ink2)">{e(INTEGRATE_TEXT)} <a href="{INTEGRATE_URL}">{INTEGRATE_URL.removeprefix("https://")}</a></p>
  </div>
</main>
</body>
</html>
'''


def main():
    svg, style = chart_svg(standalone=True)
    (HERE / "benchmark-chart.svg").write_text(svg + "\n")
    inline_svg, _ = chart_svg(standalone=False)
    (HERE / "onboarding.html").write_text(page_html(inline_svg, style))
    (HERE / "onboarding-inline.html").write_text(inline_fragment(inline_svg, style))
    (HERE / "benchmark-chart-light.svg").write_text(fixed_svg(svg, LIGHT) + "\n")
    (HERE / "benchmark-chart-dark.svg").write_text(fixed_svg(svg, DARK) + "\n")
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or \
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if pathlib.Path(chrome).exists():
        subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=2",
                        "--window-size=720,1380", f"--screenshot={HERE / 'onboarding.png'}",
                        (HERE / "onboarding.html").as_uri()], check=True, capture_output=True)
    else:
        print("Chrome not found; onboarding.png not rebuilt")
    print("built", ", ".join(p.name for p in sorted(HERE.glob("*")) if p.suffix in {".svg", ".html", ".png"}))


if __name__ == "__main__":
    main()
