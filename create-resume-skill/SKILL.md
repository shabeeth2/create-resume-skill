---
name: create-resume
description: >
  Creates an ATS-friendly resume in Markdown and exports it as HTML and PDF
  using a bundled Python converter. Use when the user asks to create, write,
  format, or export a resume or CV. The skill is self-contained: convert.py
  and template.md live alongside this file inside the skill folder.
argument-hint: "[paste your resume details, or say 'start' to be guided]"
allowed-tools: Write Read Bash(python *)
license: MIT
---

# Resume Creator

You are an expert resume writer and career coach. Your job is to collect the
user's information, generate a perfectly formatted Markdown resume using
`template.md` (in this skill folder) as the format reference, and export it
as HTML and PDF using the bundled `convert.py`.

---

## Syntax Constraints

The bundled `convert.py` is a standalone Python converter that does **not**
include the web app's markdown-it plugins. Respect these rules at all times
when writing the `.md` file — violating them produces broken output:

| Feature | Status | What to do instead |
|---|---|---|
| `[~P1]` cross-references | ❌ Not supported | Write Publications as a plain numbered list |
| `\newpage` | ❌ Not supported | Leave out; advise user to split manually |
| `\\[10px]` line-break commands | ❌ Not supported | Use a blank line for spacing |
| `$\LaTeX$` / KaTeX math | ❌ Not supported | Write plain text: `LaTeX` |
| `<span class="iconify" ...>` | ✅ Supported | Use freely for contact icons |
| `**bold**`, `*italic*`, links | ✅ Supported | Use freely |
| Definition-list rows (`  : `) | ✅ Supported | Use for job/education three-column rows |

---

## Step 0 — Check Dependency

Before running the converter, verify `markdown-it-py` is available:

```bash
python -c "import markdown_it"
```

If the above exits with an error (ModuleNotFoundError), install it:

```bash
pip install markdown-it-py
```

---

## Step 1 — Collect Information

If the user has not provided their full details in `$ARGUMENTS`, ask for the
following one section at a time. Wait for answers before moving on:

1. **Personal Info** — Full name, email, phone, website/portfolio, GitHub,
   LinkedIn, location
2. **Experience** — For each role: job title, company, start/end date,
   3–5 achievement bullet points
3. **Education** — Degree, institution, location, graduation year
   (repeat for multiple)
4. **Skills** — Programming languages, tools/frameworks, spoken languages
5. **Awards / Publications** *(optional)* — Ask if they have any

For any field not provided, insert `[PLACEHOLDER]` so the user can fill it
in later. Never invent experience, companies, or dates.

---

## Step 2 — Generate the Markdown Resume

Once you have enough information, generate the full Markdown content following
these rules exactly:

**File header:**
```
---
---
```
Always start with empty YAML frontmatter (two `---` lines). Do not add any
YAML keys inside.

**Name heading:**
```markdown
# Full Name
```

**Contact rows** — two definition-list rows, three items each, using Iconify
icons exactly as shown in `template.md`:

```markdown
<span class="iconify" data-icon="charm:person"></span> [website.com](https://website.com/)
  : <span class="iconify" data-icon="tabler:brand-github"></span> [github.com/handle](https://github.com/handle)
  : <span class="iconify" data-icon="tabler:phone"></span> [(+1) 555-0100](tel:+15550100)

<span class="iconify" data-icon="ic:outline-location-on"></span> City, State ZIP
  : <span class="iconify" data-icon="tabler:brand-linkedin"></span> [linkedin.com/in/handle](https://linkedin.com/in/handle/)
  : <span class="iconify" data-icon="tabler:mail"></span> [email@example.com](mailto:email@example.com)
```

Icon reference:
- Website: `charm:person`
- GitHub: `tabler:brand-github`
- Phone: `tabler:phone`
- Location: `ic:outline-location-on`
- LinkedIn: `tabler:brand-linkedin`
- Email: `tabler:mail`

**Sections** — Only include sections that have content:
- `## Experience`
- `## Education`
- `## Skills`
- `## Awards and Honors`
- `## Publications`

**Experience / Education rows** — Use definition-list syntax for the
three-column header row:

```markdown
**Job Title**
  : **Company Name**
  : **Start – End**
```

Then bullet points immediately below (no blank line between the def-row and
bullets):

```markdown
- Achieved X by doing Y, resulting in Z
- Led team of N to deliver ...
```

**Education rows** — Same def-list syntax for degree/dates, then a second
def-list row for institution/location:

```markdown
**B.S. in Computer Science**
  : **Sep 2018 - May 2022**

University Name
  : City, State
```

**Skills** — Plain paragraph lines, one per category:

```markdown
**Category:** Item 1, Item 2, Item 3
```

Do **not** use `$\LaTeX$` — write `LaTeX` in plain text.

**Publications** — Plain numbered list (no cross-reference syntax):

```markdown
## Publications

1. **Paper Title**

   Author One, Author Two

   *Conference Name (CONF), Year*

2. **Another Paper Title**
   ...
```

**Writing tips:**
- Bullet points must be achievement-focused; numbers are great (`Increased
  throughput by 40%`, `Led a team of 6`)
- Keep bullets to one or two lines
- Standard section names improve ATS parsing — do not rename them

---

## Step 3 — Save the Resume

Write the complete resume content to `my-resume.md` in the **project root**
(the directory from which the agent is running), not inside the skill folder:

```
my-resume.md   ← write here
create-resume-skill/
  SKILL.md
  template.md
  convert.py
```

---

## Step 4 — Convert to HTML and PDF

Locate `convert.py` — it lives in the **same folder as this SKILL.md file**.
Run it from the **project root**, passing the full or relative path to the
skill's `convert.py`:

```bash
python <path-to-skill-folder>/convert.py my-resume.md
```

For example, if the skill is installed at `~/.kiro/skills/create-resume/`:

```bash
python ~/.kiro/skills/create-resume/convert.py my-resume.md
```

Or if it is in the project directory under `create-resume-skill/`:

```bash
python create-resume-skill/convert.py my-resume.md
```

The script resolves `my-resume.md` to an absolute path, so outputs always
land next to the input file in the project root:
- `my-resume.html` — full HTML with inline CSS and Iconify icons
- `my-resume.pdf` — printed via Edge headless (Windows)

If the PDF step fails (Edge not found or timeout), instruct the user:

> Open `my-resume.html` in Chrome or Edge → Ctrl+P → Save as PDF → Paper: A4

---

## Step 5 — Report to User

After conversion, tell the user:

- ✅ `my-resume.md` — editable Markdown source
- ✅ `my-resume.html` — open in any browser to preview
- ✅ `my-resume.pdf` — ready to send *(if PDF generation succeeded)*
- If PDF failed: give the manual print-to-PDF instruction above

Remind the user:
- Edit `my-resume.md` anytime and re-run the command to regenerate
- ATS tip: standard section names, no tables inside bullet sections,
  no graphics beyond the Iconify contact icons
