---
name: create-resume
version: "1.1.0"
description: >
  Creates, writes, formats, or updates an ATS-friendly resume or CV in Markdown
  and exports it as a polished HTML file and PDF. Use this skill whenever the
  user asks to create a resume, write a CV, format their work history, update
  their resume, generate a resume from a LinkedIn profile, or export a resume
  to PDF. The skill is self-contained: scripts/convert.py and
  assets/template.md live inside the skill folder and require no extra setup
  beyond Python 3.10+ and the markdown-it-py package (auto-installed if
  missing).
tags:
  - resume
  - cv
  - career
  - document
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
the format reference, and export it as HTML and PDF using `scripts/convert.py`.

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
- "Export my resume to PDF"
- "Make me an ATS-friendly resume"

---

## Syntax Constraints

`scripts/convert.py` is a standalone Python converter that does **not** include
full markdown-it plugin suites. Respect these rules at all times when writing
the `.md` file — violating them produces broken HTML output:

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

Verify `markdown-it-py` is available before running the converter:

```bash
python -c "import markdown_it; print('OK')"
```

If that exits with `ModuleNotFoundError`, install it silently:

```bash
pip install --quiet markdown-it-py
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

**Icon reference:**
| Field | Icon |
|-------|------|
| Website | `charm:person` |
| GitHub | `tabler:brand-github` |
| Phone | `tabler:phone` |
| Location | `ic:outline-location-on` |
| LinkedIn | `tabler:brand-linkedin` |
| Email | `tabler:mail` |

### Sections
Only include sections that have content. Use **exactly** these section names
(they are ATS-optimised — do not rename them):

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
Then bullet points immediately below (no blank line between the def-row and
the bullets):
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
Do **not** use `$\LaTeX$` — write `LaTeX` in plain text.

### Publications — plain numbered list (no cross-reference syntax)
```markdown
## Publications

1. **Paper Title**

   Author One, Author Two

   *Conference Name (CONF), Year*
```

### Writing tips
- Bullet points must be achievement-focused; numbers are great
- Keep each bullet to one or two lines
- Standard section names improve ATS parsing — do not rename them
- Use active verbs: Led, Built, Designed, Reduced, Increased, Launched

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

## Step 5 — Convert to HTML and PDF

Locate `scripts/convert.py` in the `scripts/` subfolder of this SKILL.md file.
Run it from the **project root**:

```bash
python <path-to-skill-folder>/scripts/convert.py my-resume.md
```

**Common install locations:**

| Platform | Command |
|----------|---------|
| Claude Code (global) | `python ~/.claude/skills/create-resume/scripts/convert.py my-resume.md` |
| Claude Code (project) | `python .claude/skills/create-resume/scripts/convert.py my-resume.md` |
| OpenCode (global) | `python ~/.config/opencode/skills/create-resume/scripts/convert.py my-resume.md` |
| Project directory | `python create-resume/scripts/convert.py my-resume.md` |

The script outputs:
- `my-resume.html` — full HTML with inline CSS and Iconify icons
- `my-resume.pdf` — printed via Edge/Chrome headless

**If PDF generation fails** (browser not found or timeout), instruct the user:
> Open `my-resume.html` in Chrome or Edge → `Ctrl+P` (or `Cmd+P` on Mac) →
> **Save as PDF** → Paper size: **A4**

---

## Step 6 — Report to User

After successful conversion, clearly report the output files:

```
✅ Resume created successfully!

📄 my-resume.md   — Markdown source (edit anytime)
🌐 my-resume.html — Open in any browser to preview
📑 my-resume.pdf  — Ready to send to employers
```

If PDF failed, provide the manual print-to-PDF instruction instead.

Then remind the user:
- Edit `my-resume.md` and re-run the convert command to regenerate anytime
- **ATS tip**: Keep standard section names, avoid tables inside bullet
  sections, and avoid graphics beyond the Iconify contact icons
- **PDF tip**: Print-to-PDF from a browser always produces the cleanest output

---

## Error Handling

| Error | Agent Action |
|-------|-------------|
| `python` not found | Report: "Python 3.10+ is required. Download from python.org" |
| `pip install` fails | Report: "Could not install markdown-it-py. Try: `pip3 install markdown-it-py`" |
| `convert.py` not found | Check skill installation path; verify skill folder structure |
| Edge/Chrome not found | Skip PDF; provide manual print-to-PDF instruction |
| Timeout on PDF step | Skip PDF; provide manual print-to-PDF instruction |
| Output file already exists | Overwrite silently (the script handles this) |
