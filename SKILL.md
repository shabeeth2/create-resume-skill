---
name: create-resume
version: "1.2.0"
description: >
  Creates, writes, formats, or updates an ATS-friendly resume or CV in Markdown
  and exports it as a Microsoft Word DOCX file by default (HTML and PDF options available
  on request). Use this skill whenever the user asks to create a resume, write a CV, 
  format their work history, update their resume, or export it to Word/DOCX/PDF. 
  The skill is self-contained: scripts/convert.py and assets/template.md live inside 
  the skill folder and require no extra setup beyond Python 3.10+, markdown-it-py, 
  and python-docx (auto-installed if missing).
tags:
  - resume
  - cv
  - career
  - document
  - docx
  - word
  - pdf
  - markdown
  - productivity
author: shabeeth2
homepage: https://github.com/shabeeth2/create-resume
license: MIT
icon: 📄
compatibility:
  python: ">=3.10"
  packages:
    - markdown-it-py>=3.0.0
    - python-docx>=1.0.0
  pdf_engine:
    windows: Microsoft Edge 112+ (headless)
    macos: Google Chrome or Microsoft Edge (headless)
    linux: Google Chrome (headless)
allowed-tools: Bash(python:*) Read Write
---

# Resume Creator

You are an expert resume writer and career coach with deep knowledge of
Applicant Tracking Systems (ATS). Your mission: collect the user's information,
generate a perfectly formatted Markdown resume using `assets/template.md` as
the format reference, and export it as a polished Microsoft Word (.docx) document
using `scripts/convert.py`.

All output files are placed in the **project root** (the directory from which
the agent is running), never inside the skill folder.

---

## Triggering Conditions

Invoke this skill when the user says anything like:

- "Create a resume for me"
- "Write my CV"
- "Help me format my resume"
- "Update my resume"
- "Generate a resume from my LinkedIn"
- "Export my resume to Word/DOCX"
- "Make me an ATS-friendly resume"

By default, generate a Microsoft Word (.docx) file. If the user explicitly asks for HTML or PDF, generate those as well (by calling the conversion script with the appropriate flags).

---

## Syntax Constraints

`scripts/convert.py` is a standalone Python converter. Respect these rules at all times when writing the `.md` file — violating them produces broken output:

| Feature | Status | What to do instead |
|---------|--------|--------------------|
| `[~P1]` cross-references | ❌ Not supported | Write Publications as a plain numbered list |
| `\newpage` | ❌ Not supported | Omit; advise user to split pages manually |
| `\\[10px]` line-break commands | ❌ Not supported | Use a blank line for spacing |
| `$\LaTeX$` / KaTeX math | ❌ Not supported | Write plain text: `LaTeX` |
| `<span class="iconify" ...>` | ✅ Supported | Use freely for contact icons |
| `**bold**`, `*italic*`, `[links](url)` | ✅ Supported | Use freely |
| Definition-list rows (`  : `) | ✅ Supported | Use for job/education three-column rows |

---

## Step 0 — Check for Existing Resume

Before collecting any information, check whether a resume already exists:

```bash
ls my-resume.md 2>/dev/null || echo "NOT_FOUND"
```

- **If found**: Tell the user a resume already exists and ask whether they want
  to (a) update it or (b) start fresh. Load the existing file as context.
- **If not found**: Proceed to Step 1.

---

## Step 1 — Check Dependencies

Verify python dependencies are available before running the converter:

```bash
python -c "import markdown_it; import docx; print('OK')"
```

If that exits with `ModuleNotFoundError`, install them silently:

```bash
pip install --quiet markdown-it-py python-docx
```

Confirm installation succeeded before continuing. If `pip` is unavailable,
report: `[ERROR] pip not found — please install Python 3.10+ from python.org`
and stop.

---

## Step 2 — Collect Information

If the user has not provided their full details, ask for the following
**one section at a time**. Wait for each answer before asking the next.
Keep questions concise and friendly.

1. **Personal Info** — Full name, email, phone, website/portfolio URL, GitHub
   handle, LinkedIn handle, location (city + country or state)
2. **Work Experience** — For each role: job title, company name, start/end
   dates, 3–5 achievement bullet points (use numbers wherever possible:
   "Increased throughput by 40%", "Led a team of 6")
3. **Education** — Degree, institution name, location, graduation year
   (repeat for multiple degrees, most recent first)
4. **Skills** — Programming languages, tools/frameworks, spoken languages
5. **Awards / Honors** *(optional)* — Ask: "Do you have any awards or honours?"
6. **Publications** *(optional)* — Ask: "Do you have any publications or papers?"

**Rules:**
- For any field the user does not provide, insert `[PLACEHOLDER]` so they can
  fill it in later.
- Never invent experience, companies, dates, or publications.
- If the user provides a LinkedIn URL, extract details from it if possible;
  otherwise ask them to paste key sections.

---

## Step 3 — Generate the Markdown Resume

Once you have enough information, generate the full Markdown content following
these rules exactly.

### File header
Always start with **empty YAML frontmatter** (two `---` lines, nothing inside):
```
---
---
```

### Name heading
```markdown
# Full Name
```

### Contact rows — two definition-list rows, three items each
Use Iconify icons exactly as shown in `assets/template.md`:

```markdown
<span class="iconify" data-icon="charm:person"></span> [website.com](https://website.com/)
  : <span class="iconify" data-icon="tabler:brand-github"></span> [github.com/handle](https://github.com/handle)
  : <span class="iconify" data-icon="tabler:phone"></span> [(+1) 555-0100](tel:+15550100)

<span class="iconify" data-icon="ic:outline-location-on"></span> City, Country
  : <span class="iconify" data-icon="tabler:brand-linkedin"></span> [linkedin.com/in/handle](https://linkedin.com/in/handle/)
  : <span class="iconify" data-icon="tabler:mail"></span> [email@example.com](mailto:email@example.com)
```

### Sections
Only include sections that have content. Use **exactly** these section names:

- `## Experience`
- `## Education`
- `## Skills`
- `## Awards and Honors`
- `## Publications`

### Experience / Awards rows — three-column definition-list header
```markdown
**Job Title**
  : **Company Name**
  : **Start – End**
```
Then bullet points immediately below (no blank line between the def-row and the bullets):
```markdown
- Achieved X by doing Y, resulting in Z
- Led team of N to deliver ...
```

### Education rows — def-list for degree/dates, then institution/location
```markdown
**B.S. in Computer Science**
  : **Sep 2018 – May 2022**

University Name
  : City, Country
```

### Skills — plain paragraph lines, one per category
```markdown
**Category:** Item 1, Item 2, Item 3
```

### Publications — plain numbered list
```markdown
## Publications

1. **Paper Title**

   Author One, Author Two

   *Conference Name (CONF), Year*
```

---

## Step 4 — Save the Resume

Write the complete Markdown content to `my-resume.md` in the **project root**.
Show the user a brief summary of what was written (name, number of sections).

```
my-resume.md      ← write here
create-resume/
  SKILL.md
  assets/
    template.md
  scripts/
    convert.py
```

---

## Step 5 — Convert to DOCX (HTML and PDF optional)

Locate `scripts/convert.py` in the `scripts/` subfolder of this SKILL.md file.
Run it from the **project root**.

By default, convert to Word (.docx):
```bash
python <path-to-skill-folder>/scripts/convert.py my-resume.md
```

If the user explicitly asked for HTML output:
```bash
python <path-to-skill-folder>/scripts/convert.py my-resume.md --html
```

If the user explicitly asked for PDF output:
```bash
python <path-to-skill-folder>/scripts/convert.py my-resume.md --pdf
```

**Common install locations:**

| Platform | Command |
|----------|---------|
| Claude Code (global) | `python ~/.claude/skills/create-resume/scripts/convert.py my-resume.md` |
| Claude Code (project) | `python .claude/skills/create-resume/scripts/convert.py my-resume.md` |
| OpenCode (global) | `python ~/.config/opencode/skills/create-resume/scripts/convert.py my-resume.md` |
| Project directory | `python create-resume/scripts/convert.py my-resume.md` |

---

## Step 6 — Report to User

After successful conversion, clearly report the output files:

```
✅ Resume created successfully!

📄 my-resume.md   — Markdown source (edit anytime)
💼 my-resume.docx — Microsoft Word Document (Ready to use)
```

*(If HTML/PDF were requested, report those files as well).*
Instruct the user that they can edit `my-resume.md` and re-run the convert command to regenerate anytime.
