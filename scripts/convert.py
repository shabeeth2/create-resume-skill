#!/usr/bin/env python3
"""
convert.py - Convert a Markdown resume to HTML + PDF.

Part of the create-resume agent skill.
https://github.com/shabeeth2/create-resume

Usage:
  python convert.py <resume.md>              # → resume.html + resume.pdf
  python convert.py <resume.md> --html-only  # → resume.html only
  python convert.py --version                # → print version and exit
  python convert.py --help                   # → print this help

Requirements:
  markdown-it-py  (pip install markdown-it-py)

PDF engine (one of, in priority order):
  Windows : Microsoft Edge 112+  (msedge.exe — built into Windows)
  macOS   : Google Chrome        (homebrew: brew install --cask google-chrome)
  Linux   : Google Chrome / Chromium (apt: chromium-browser)
"""

__version__ = "1.1.0"

import sys
import re
import subprocess
from pathlib import Path

# ─── Resume CSS ───────────────────────────────────────────────────────────────
# Matches the project's default template styling

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
    """Convert inline markdown to HTML (bold, italic, links, code)."""
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


# ─── PDF engine detection ─────────────────────────────────────────────────────

def _find_browser() -> tuple[str | None, str]:
    """
    Find a headless-capable browser for PDF export.
    Returns (path_or_None, platform_name).

    Priority:
      1. Microsoft Edge (Windows primary, also available on macOS/Linux)
      2. Google Chrome (macOS / Linux)
      3. Chromium (Linux)
    """
    import platform
    os_name = platform.system()

    candidates: list[tuple[str, str]] = []

    if os_name == "Windows":
        candidates = [
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
        ]
    elif os_name == "Darwin":  # macOS
        candidates = [
            ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "Chrome"),
            ("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "Edge"),
            ("/Applications/Chromium.app/Contents/MacOS/Chromium", "Chromium"),
        ]
    else:  # Linux and others
        # Try PATH-based lookup for common executables
        for name in ("google-chrome", "google-chrome-stable", "chromium-browser",
                      "chromium", "microsoft-edge", "microsoft-edge-stable"):
            try:
                result = subprocess.run(
                    ["which", name], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    label = "Chrome" if "chrome" in name else (
                        "Chromium" if "chromium" in name else "Edge"
                    )
                    candidates.append((result.stdout.strip(), label))
            except Exception:
                pass

    for path, label in candidates:
        if Path(path).exists():
            return path, label

    return None, ""


def html_to_pdf(html_path: Path, pdf_path: Path) -> bool:
    """
    Render HTML to PDF using Edge or Chrome headless.
    Returns True on success, False on failure.
    """
    browser, label = _find_browser()

    if not browser:
        print("  [WARN] No supported browser found for PDF export.")
        print("         Supported: Microsoft Edge (Windows), Google Chrome, Chromium")
        print(f"  [INFO] Manual fallback: open '{html_path.name}' in your browser")
        print("         → Ctrl+P (or Cmd+P) → Save as PDF → Paper: A4")
        return False

    file_url = html_path.as_uri()  # e.g. file:///D:/path/to/my-resume.html

    cmd = [
        browser,
        "--headless=new",                          # new headless mode (Chrome/Edge 112+)
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=5000",              # wait up to 5 s for Iconify JS
        f"--print-to-pdf={pdf_path}",
        file_url,
    ]

    print(f"  [*] Using {label} headless -> {pdf_path.name} ...")
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
    except subprocess.TimeoutExpired:
        print("  [WARN] Browser timed out after 30 s.")
        print(f"  [INFO] Manual fallback: open '{html_path.name}' → Ctrl+P → Save as PDF")
        return False
    except FileNotFoundError:
        print(f"  [WARN] Browser executable not found: {browser}")
        return False
    except Exception as e:
        print(f"  [WARN] Browser error: {e}")
        return False

    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        return True

    # Some browsers output to CWD — check there too
    cwd_pdf = Path.cwd() / pdf_path.name
    if cwd_pdf.exists() and cwd_pdf != pdf_path:
        cwd_pdf.rename(pdf_path)
        return True

    return False


# ─── Main convert function ────────────────────────────────────────────────────

def convert(md_file: str, html_only: bool = False) -> None:
    md_path = Path(md_file).resolve()
    if not md_path.exists():
        print(f"[ERROR] File not found: {md_path}")
        sys.exit(1)

    html_path = md_path.with_suffix(".html")
    pdf_path  = md_path.with_suffix(".pdf")

    print(f"\n[*] Input  : {md_path}")

    # Step 1 - Markdown to HTML
    print("[1] Markdown -> HTML ...")
    md_text   = md_path.read_text(encoding="utf-8")
    body_html = md_to_html_body(md_text)
    full_html = build_full_html(body_html, title=md_path.stem.replace("-", " ").title())
    html_path.write_text(full_html, encoding="utf-8")
    print(f"    [OK] HTML saved -> {html_path}")

    if html_only:
        print()
        return

    # Step 2 - HTML to PDF
    print("[2] HTML -> PDF (headless browser) ...")
    ok = html_to_pdf(html_path, pdf_path)
    if ok:
        size_kb = pdf_path.stat().st_size // 1024
        print(f"    [OK] PDF saved  -> {pdf_path}  ({size_kb} KB)")
    else:
        print(f"    [WARN] PDF not generated.")
        print(f"    [INFO] Open '{html_path.name}' in Chrome/Edge -> Ctrl+P -> Save as PDF (A4)")

    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        sys.exit(0)

    if "--version" in args or "-v" in args:
        print(f"convert.py {__version__} (create-resume skill)")
        sys.exit(0)

    html_only = "--html-only" in args
    md_files  = [a for a in args if not a.startswith("--")]

    if not md_files:
        print("[ERROR] Please provide a .md file path.")
        print("        Usage: python convert.py <resume.md>")
        sys.exit(1)

    convert(md_files[0], html_only=html_only)
