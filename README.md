# create-resume

An agent skill that creates ATS-friendly resumes in Markdown and exports them as Word DOCX files by default, with HTML and PDF options available on request.

## Install

```bash
# Via npx skills (recommended)
npx skills add shabeeth2/create-resume-skill

# Or copy manually
cp -r create-resume ~/.claude/skills/        # Claude Code (global)
cp -r create-resume .claude/skills/          # Claude Code (project)
cp -r create-resume ~/.config/opencode/skills/  # OpenCode (global)
cp -r create-resume .opencode/skills/        # OpenCode (project)
```

## Usage

Just ask your agent naturally:

```
"Create a resume for me"
"Help me write a CV"
"Format my work history into a resume"
"Export my resume to DOCX"
```

The agent will:
1. Check if a resume already exists and offer to update it
2. Collect your info one section at a time
3. Generate `my-resume.md` in your project root
4. Convert it to `my-resume.docx` automatically

## Output

| File | Description |
|------|-------------|
| `my-resume.md` | Editable Markdown source |
| `my-resume.docx` | Microsoft Word Document (default) |
| `my-resume.html` | HTML (on request via `--html`) |
| `my-resume.pdf` | PDF (on request via `--pdf`) |

## Requirements

- Python 3.10+
- `markdown-it-py` (auto-installed)
- `python-docx` (auto-installed)
- Edge or Chrome (for PDF export only)

## License

MIT
