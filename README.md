<div align="center">

# 📄 create-resume

**An agent skill that builds ATS-friendly resumes in Markdown and exports them as HTML + PDF.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-D97757?logo=anthropic&logoColor=white)](https://claude.ai)
[![OpenCode](https://img.shields.io/badge/OpenCode-compatible-6C47FF)](https://opencode.ai)
[![Version](https://img.shields.io/badge/version-1.1.0-brightgreen)](SKILL.md)

</div>

---

## ✨ Features

- 🎯 **ATS-optimised output** — Standard section names, clean structure, no decorative tables
- 📝 **Guided interview** — Agent collects your info one section at a time
- 🌐 **Beautiful HTML** — Inline CSS, Iconify contact icons, print-ready layout
- 📑 **One-click PDF** — Exported via Edge or Chrome headless (no extra tools)
- 🔄 **Resumable** — Re-run anytime to update your existing resume
- 🪶 **Self-contained** — No external services, no API keys, fully offline
- 🖥️ **Cross-platform** — Windows, macOS, and Linux supported

---

## 📸 Sample Output

> The resume below was generated from a single agent conversation using this skill.

![Sample resume output showing Bruce Wayne's resume in clean two-column layout](assets/sample-output.png)

---

## 🚀 Install

### Claude Code

```bash
# Global install (available in all projects)
cp -r create-resume ~/.claude/skills/

# Project-level install
cp -r create-resume .claude/skills/
```

### OpenCode

```bash
# Global install
cp -r create-resume ~/.config/opencode/skills/

# Project-level install
cp -r create-resume .opencode/skills/
```

### All supported platforms

| Platform | Project-level path | Global path |
|----------|--------------------|-------------|
| Claude Code | `.claude/skills/create-resume/` | `~/.claude/skills/create-resume/` |
| OpenCode | `.opencode/skills/create-resume/` | `~/.config/opencode/skills/create-resume/` |
| Generic agents | `.agents/skills/create-resume/` | `~/.agents/skills/create-resume/` |

---

## 💬 Usage

Just ask your agent naturally. Any of these will trigger the skill:

```
"Create a resume for me"
"Help me write a CV"
"Format my work history into a resume"
"Update my existing resume"
"Generate a resume from my LinkedIn profile"
"Make me an ATS-friendly resume and export it to PDF"
```

The agent will:
1. Check if a resume already exists and offer to update it
2. Collect your info one section at a time (name, experience, education, skills, etc.)
3. Generate `my-resume.md` in your project root
4. Convert it to `my-resume.html` + `my-resume.pdf` automatically

---

## 📂 Output Files

| File | Description |
|------|-------------|
| `my-resume.md` | Editable Markdown source — the single source of truth |
| `my-resume.html` | Full HTML with inline CSS and Iconify icons; open in any browser |
| `my-resume.pdf` | Print-ready PDF exported via Edge/Chrome headless |

All files are written to the **project root** (the directory where your agent is running).

---

## 📋 Requirements

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | `python --version` to check |
| markdown-it-py | 3.0+ | Auto-installed if missing |
| Edge or Chrome | Any recent | For PDF export — optional |

Install Python dependencies manually if needed:

```bash
pip install markdown-it-py
```

---

## 🗂️ Project Structure

```
create-resume/
├── SKILL.md              # Agent instructions + skill metadata
├── AGENTS.md             # Agent-system documentation
├── skill.json            # Machine-readable metadata
├── scripts/
│   └── convert.py        # Markdown → HTML + PDF converter
├── assets/
│   ├── template.md       # Resume format reference (sample resume)
│   └── sample-output.png # Screenshot of rendered output
└── README.md             # This file
```

---

## 🔧 Manual Conversion

You can run the converter directly without an agent:

```bash
# Convert to HTML + PDF
python create-resume/scripts/convert.py my-resume.md

# Convert to HTML only (no PDF)
python create-resume/scripts/convert.py my-resume.md --html-only

# Show version
python create-resume/scripts/convert.py --version

# Show help
python create-resume/scripts/convert.py --help
```

---

## 🛠️ Troubleshooting

### PDF not generated
The PDF step requires Microsoft Edge (Windows) or Google Chrome (macOS/Linux).

**Manual fallback:**
1. Open `my-resume.html` in Chrome or Edge
2. Press `Ctrl+P` (or `Cmd+P` on Mac)
3. Select **Save as PDF**
4. Set paper size to **A4**
5. Click **Save**

### `markdown-it-py` not found
```bash
pip install markdown-it-py
# or
pip3 install markdown-it-py
```

### `python` command not found
On some systems Python 3 is available as `python3`:
```bash
python3 create-resume/scripts/convert.py my-resume.md
```

### Icons not showing in PDF
The Iconify CDN requires internet access when the HTML file is first opened.
Open `my-resume.html` in a browser with internet access, then print to PDF.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Commit your changes with clear messages
4. Open a Pull Request describing what you changed and why

**Ideas for contributions:**
- Additional resume templates (`assets/template-*.md`)
- More PDF engine support (WeasyPrint, wkhtmltopdf)
- Cover letter generation step
- LinkedIn profile parser integration

---

## 📄 License

MIT © [shabeeth2](https://github.com/shabeeth2)

See [LICENSE](LICENSE) for full text.

---

<div align="center">

Made with ❤️ for job seekers everywhere.
[⭐ Star this repo](https://github.com/shabeeth2/create-resume) if it helped you land your next role!

</div>
