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
author: shabeeth2
license: MIT
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
allowed-tools:
  - Bash(python:*)
  - Read
  - Write
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

## Step 0 — Determine Output Filename & Check for Existing Resume

Output files are named using the pattern:

```
{FullName}-{JobTitle}-{Company}.md
{FullName}-{JobTitle}-{Company}.docx
```

- Replace spaces with underscores (`_`) in each segment.
- Derive `{FullName}`, `{JobTitle}`, and `{Company}` from the user's input or the job description provided.
- Example: `Mohamed_Shabeeth_N-Python_GenAI_Engineer-Capgemini_Invent.md`

Store this as `RESUME_FILE` and use it consistently in all subsequent steps.

Before collecting any information, check whether a resume with this name already exists:

```bash
ls {RESUME_FILE} 2>/dev/null || echo "NOT_FOUND"
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

## Step 2 — Analyse the JD & Collect Information

### 2a — Parse the Job Description First

If the user has provided a job description (JD), extract and internally note before doing anything else:

- **Required skills / tools / languages** — things explicitly listed as required or expected
- **Preferred / nice-to-have skills** — listed as a plus but not mandatory
- **Core responsibilities** — what the role actually does day-to-day
- **ATS keywords** — exact terms and phrases the JD repeats or emphasises

Use this analysis as the **filter** for every decision in Step 3:
- Include an experience bullet only if it maps to a JD responsibility or keyword
- Include a skill only if the JD explicitly requires or prefers it **and** the user has genuine hands-on experience with it
- Never add a skill just because it sounds relevant — it must appear in the JD and in the user's actual work
- If no JD is provided, include all relevant content and ask the user what role they are targeting

### 2b — Collect Missing Information

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

### JD-Alignment Rules (apply before writing anything)

Before writing a single line of resume content, filter all user data against the JD analysis from Step 2a:

**Experience bullets:**
- Select only bullets that directly match a JD responsibility or required skill
- Rewrite using the exact terminology from the JD where the underlying work is the same
- Drop bullets that are impressive but not relevant to this specific role
- Maximum 4–5 bullets per role — pick the strongest JD matches, not everything

**Projects:**
- Select 2–3 projects maximum — only those that demonstrate skills the JD explicitly asks for
- Drop projects that showcase skills not mentioned in the JD, even if technically impressive
- Prefer projects that use the same tools/frameworks the JD names

**Skills section:**
- List ONLY skills that (a) appear in the JD as required or preferred AND (b) the user has genuine hands-on experience with
- Do NOT list a skill simply because the user knows it — it must be relevant to this JD
- Do NOT list skills the user only has theoretical or passing familiarity with
- Keep categories lean: 4–6 items per category, most signal-rich for this role only
- If the JD doesn't mention a tool, leave it out even if the user has used it

**Summary:**
- Write using keywords drawn directly from the JD
- Mirror the role's exact language (e.g. if JD says "scalable AI solutions", use that phrase)
- 2–3 sentences maximum

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

Write the complete Markdown content to `{RESUME_FILE}` in the **project root**.
Show the user a brief summary of what was written (name, number of sections).

```
{Name}-{JobTitle}-{Company}.md      ← write here
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
