# create-resume

An [Agent Skills](https://agentskills.io)-compatible skill that creates ATS-friendly resumes in Markdown, then exports HTML + PDF.

## Install

### Claude Code / OpenCode

```bash
# Claude Code
cp -r create-resume ~/.claude/skills/

# OpenCode
cp -r create-resume ~/.opencode/skills/
```

### Manual

Copy the `create-resume/` folder into any of these locations:

| Platform | Path |
|----------|------|
| OpenCode (project) | `.opencode/skills/` |
| OpenCode (global) | `~/.config/opencode/skills/` |
| Claude Code (project) | `.claude/skills/` |
| Claude Code (global) | `~/.claude/skills/` |
| Agent-compatible (project) | `.agents/skills/` |
| Agent-compatible (global) | `~/.agents/skills/` |

## Usage

Ask your agent to create a resume:

> "Create a resume for me"
> "Help me write a CV"
> "Generate a resume from my LinkedIn profile"

The agent will collect your information, generate a Markdown resume, and export it as HTML + PDF.

## Requirements

- Python 3.10+
- `markdown-it-py` (auto-installed if missing)
- Microsoft Edge (for PDF generation, optional — fallback to browser print-to-PDF)

## Structure

```
create-resume/
├── SKILL.md          # Skill instructions + metadata
├── scripts/
│   └── convert.py    # Markdown → HTML + PDF converter
├── assets/
│   └── template.md   # Resume format reference
└── README.md         # This file
```

## License

MIT
