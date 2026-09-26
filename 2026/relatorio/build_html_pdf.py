#!/usr/bin/env python3
"""Converte o relatório MD em HTML autocontido (imagens base64) e PDF."""
from __future__ import annotations

import base64
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "relatorio"
MD = ROOT / "auditoria_eleicoes_2022.md"
HTML = ROOT / "build" / "auditoria_eleicoes_2022.html"
PDF = ROOT / "build" / "auditoria_eleicoes_2022.pdf"
ROOT.joinpath("build").mkdir(exist_ok=True)

CSS = """
:root { --fg:#1a1a1a; --muted:#555; --line:#ddd; --bg:#fafafa; }
html { font-size: 16px; }
body {
  font-family: "Liberation Serif", "DejaVu Serif", Georgia, serif;
  color: var(--fg); background: #fff;
  max-width: 820px; margin: 2rem auto; padding: 0 1.25rem 3rem;
  line-height: 1.55;
}
h1 { font-size: 1.75rem; line-height: 1.25; margin-top: 0; border-bottom: 2px solid #333; padding-bottom: .4rem; }
h2 { font-size: 1.35rem; margin-top: 2.2rem; border-bottom: 1px solid var(--line); padding-bottom: .25rem; }
h3 { font-size: 1.1rem; margin-top: 1.5rem; }
p, li { font-size: 0.98rem; }
em { color: var(--muted); font-size: 0.92rem; }
img { max-width: 100%; height: auto; display: block; margin: 1rem auto;
      border: 1px solid var(--line); background: var(--bg); }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.88rem; }
th, td { border: 1px solid var(--line); padding: 0.35rem 0.5rem; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
code, pre { font-family: "DejaVu Sans Mono", monospace; font-size: 0.82rem; }
pre { background: #f4f4f4; padding: 0.75rem 1rem; overflow-x: auto; border: 1px solid var(--line); }
hr { border: none; border-top: 1px solid var(--line); margin: 2rem 0; }
strong { font-weight: 600; }
@media print {
  body { max-width: none; margin: 0; padding: 12mm; font-size: 10.5pt; }
  h2 { page-break-after: avoid; }
  img { page-break-inside: avoid; max-height: 88vh; }
  table { page-break-inside: avoid; }
}
"""


def md_to_html_body(md: str) -> str:
    """Pandoc MD → HTML fragment."""
    r = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--wrap=none"],
        input=md.encode("utf-8"),
        capture_output=True,
        check=True,
    )
    return r.stdout.decode("utf-8")


def embed_images(html: str, base: Path) -> str:
    def repl(m):
        src = m.group(1)
        alt = m.group(2) if m.lastindex >= 2 else ""
        path = (base / src).resolve()
        if not path.exists():
            return m.group(0)
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
        return f'<img src="data:{mime};base64,{data}" alt="{alt}"/>'

    # pandoc: <img src="figuras/..." ... />
    html = re.sub(
        r'<img src="([^"]+)"([^>]*)/>',
        lambda m: repl_img(m, base),
        html,
    )
    return html


def repl_img(m, base: Path) -> str:
    src = m.group(1)
    rest = m.group(2)
    path = (base / src).resolve()
    if not path.exists():
        return m.group(0)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f'<img src="data:{mime};base64,{data}"{rest}/>'


def main():
    md = MD.read_text(encoding="utf-8")
    body = md_to_html_body(md)
    body = embed_images(body, ROOT)
    doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Auditoria estatística das contagens — Eleições 2022</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""
    HTML.write_text(doc, encoding="utf-8")
    print("HTML:", HTML, f"({HTML.stat().st_size/1e6:.1f} MB)")

    # PDF via Chrome headless (melhor para HTML com data-URI)
    chrome = Path("/usr/bin/google-chrome")
    if chrome.exists():
        subprocess.run([
            str(chrome), "--headless", "--disable-gpu", "--no-pdf-header-footer",
            f"--print-to-pdf={PDF}",
            HTML.as_uri(),
        ], check=True, capture_output=True)
        print("PDF:", PDF, f"({PDF.stat().st_size/1e6:.1f} MB)")
    else:
        print("Chrome ausente; PDF não gerado.")


if __name__ == "__main__":
    main()
