#!/usr/bin/env python3
"""
convert.py - Convert a markdown resume to HTML + PDF.

Usage:
  python convert.py <resume.md>              # → resume.html + resume.pdf
  python convert.py <resume.md> --html-only  # → resume.html only

Requirements (already installed):
  markdown-it-py  - Markdown parsing
  Edge headless   - HTML → PDF (built into Windows)
"""

import sys
import re
import subprocess
from pathlib import Path

# ─── Resume CSS ───────────────────────────────────────────────────────────────
# Matches the project's default template (site/src/utils/constants/default.ts)

RESUME_CSS = """
@page {
  size: A4;
  margin: 14.5mm 11.9mm;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  background: white;
  color: black;
  font-family: Verdana, Arial, sans-serif;
  font-size: 12px;
  line-height: 1.3;
  text-align: left;
  -webkit-hyphens: auto;
  hyphens: auto;
}

#resume {
  max-width: 794px;
  margin: 0 auto;
}

/* Headings */
h1, h2, h3 {
  font-weight: bold;
}

h1 {
  font-size: 2.5em;
  letter-spacing: 0.1em;
  text-align: center;
  margin-bottom: 0.25em;
  border-bottom: 1px solid darkgrey;
}

h2 {
  font-size: 1.2em;
  margin-bottom: 0.25em;
  margin-top: 1em;
  border-bottom: 1px solid darkgrey;
}

h3 {
  font-size: 1.1em;
  margin-bottom: 0.25em;
  margin-top: 0.8em;
}

/* Base elements */
p, li, dl {
  margin: 0;
  margin-bottom: 5px;
}

/* Lists */
ul, ol {
  padding-left: 1.5em;
  margin: 0.2em 0 1em 0;
}

ul { list-style-type: disc; }
ol { list-style-type: decimal; }

/* Definition lists — three-column row layout */
dl {
  display: flex;
  margin: 0;
  margin-bottom: 2px;
}

dl dt,
dl dd:not(:last-child) {
  flex: 1;
}

dl dd {
  margin: 0;
}

/* Links */
a {
  color: black;
  text-decoration: none;
}

/* Images */
img {
  max-width: 100%;
}

/* Print */
@media print {
  body { background: white !important; color: black !important; }
  a    { color: black !important; }
}
"""

# ─── Markdown pre-processor ───────────────────────────────────────────────────

def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- ... ---)."""
    text = text.strip()
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


def md_inline(text: str) -> str:
    """Convert inline markdown to HTML (bold, italic, links, code, underline)."""
    # Bold+Italic: ***text***
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic: *text* or _text_
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"_(.+?)_", r"<em>\1</em>", text)
    # Inline code: `text`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links: [label](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Pass-through HTML tags (iconify spans, <u>, etc.)
    return text


def preprocess_deflists(text: str) -> str:
    """
    Convert resume deflist syntax to HTML <dl> elements.

    Pattern in the template:
        **Job Title**
          : **Company Name**
          : **Date Range**

    Becomes:
        <dl><dt><strong>Job Title</strong></dt>
            <dd><strong>Company Name</strong></dd>
            <dd><strong>Date Range</strong></dd></dl>
    """
    lines = text.split("\n")
    output = []
    i = 0

    while i < len(lines):
        line = lines[i]
        # Peek ahead: is the next non-empty line a definition item?
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j < len(lines) and re.match(r"^  : |^: ", lines[j]):
            # Current line is the <dt>
            term = line.strip()
            defs = []
            i = j  # skip any blank lines between term and first def
            while i < len(lines) and re.match(r"^  : |^: ", lines[i]):
                d = re.sub(r"^  : |^: ", "", lines[i]).strip()
                defs.append(d)
                i += 1
            dd_parts = "".join(f"<dd>{md_inline(d)}</dd>" for d in defs)
            output.append(f"<dl><dt>{md_inline(term)}</dt>{dd_parts}</dl>")
        else:
            output.append(line)
            i += 1

    return "\n".join(output)


# ─── Main conversion ──────────────────────────────────────────────────────────

def md_to_html_body(md_text: str) -> str:
    """Convert full markdown resume text to an HTML body fragment."""
    from markdown_it import MarkdownIt

    # 1. Strip frontmatter
    md_text = strip_frontmatter(md_text)

    # 2. Pre-process definition lists (before markdown-it sees the text)
    md_text = preprocess_deflists(md_text)

    # 3. Run markdown-it for headings, paragraphs, bullet lists, etc.
    #    html=True lets us pass through the <dl>…</dl> blocks we injected.
    md = MarkdownIt("commonmark", {"html": True})
    html = md.render(md_text)
    return html


def build_full_html(body: str, title: str = "Resume") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <script src="https://code.iconify.design/2/2.2.1/iconify.min.js"></script>
  <style>{RESUME_CSS}</style>
</head>
<body>
<div id="resume">
{body}
</div>
</body>
</html>"""


def html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    """Render HTML to PDF using Edge headless. Returns True on success."""
    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge = next((p for p in edge_candidates if Path(p).exists()), None)

    if not edge:
        print("  [WARN] Microsoft Edge not found on this system.")
        print(f"  [INFO] Open '{html_path.name}' in your browser -> Ctrl+P -> Save as PDF.")
        return False

    file_url = html_path.as_uri()  # e.g. file:///D:/path/to/my-resume.html

    cmd = [
        edge,
        "--headless=new",          # new headless mode (Edge 112+)
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",   # wait up to 5 s for JS (iconify icons)
        f"--print-to-pdf={pdf_path}",
        file_url,
    ]

    print(f"  Running Edge headless -> {pdf_path.name} ...")
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        print("  [WARN] Edge timed out after 30 s.")
        return False
    except Exception as e:
        print(f"  [WARN] Edge error: {e}")
        return False

    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        return True

    # Edge sometimes outputs to the CWD — check there too
    cwd_pdf = Path.cwd() / pdf_path.name
    if cwd_pdf.exists() and cwd_pdf != pdf_path:
        cwd_pdf.rename(pdf_path)
        return True

    return False


def convert(md_file: str, html_only: bool = False) -> None:
    md_path = Path(md_file).resolve()
    if not md_path.exists():
        print(f"[ERROR] File not found: {md_path}")
        sys.exit(1)

    html_path = md_path.with_suffix(".html")
    pdf_path  = md_path.with_suffix(".pdf")

    print(f"\n[*] Input  : {md_path.name}")

    # Step 1 - Markdown to HTML
    print("[1] Markdown -> HTML ...")
    md_text   = md_path.read_text(encoding="utf-8")
    body_html = md_to_html_body(md_text)
    full_html = build_full_html(body_html, title=md_path.stem.replace("-", " ").title())
    html_path.write_text(full_html, encoding="utf-8")
    print(f"    OK: HTML saved -> {html_path}")

    if html_only:
        return

    # Step 2 - HTML to PDF
    print("[2] HTML -> PDF (Edge headless) ...")
    ok = html_to_pdf(html_path, pdf_path)
    if ok:
        size_kb = pdf_path.stat().st_size // 1024
        print(f"    OK: PDF saved  -> {pdf_path}  ({size_kb} KB)")
    else:
        print(f"    WARN: PDF not generated. Open '{html_path.name}' in browser -> Ctrl+P -> Save as PDF")

    print()


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    html_only = "--html-only" in args
    md_files  = [a for a in args if not a.startswith("--")]

    if not md_files:
        print("❌ Please provide a .md file path.")
        sys.exit(1)

    convert(md_files[0], html_only=html_only)
