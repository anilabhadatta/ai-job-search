"""
Claude CLI Synchronizer
Syncs uploaded CV profile to CLAUDE.md, 01-candidate-profile.md, and search-queries.md
so that Claude Code CLI commands (/scrape, /rank, /apply) work seamlessly with ANY candidate.
"""

import os
from typing import Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def sync_to_claude_cli(candidate: Dict[str, Any]):
    """Sync candidate details to CLAUDE.md and .claude/ canonical files."""
    name = candidate.get("name", "Candidate")
    email = candidate.get("email", "")
    phone = candidate.get("phone", "")
    linkedin = candidate.get("linkedin", "")
    github = candidate.get("github", "")
    domain = candidate.get("primary_domain", "Software Engineer")
    skills = candidate.get("skills", [])
    yoe = candidate.get("estimated_yoe", 3.0)
    current_company = candidate.get("current_company", "Tech Company")
    summary = candidate.get("summary", "")

    skills_str = ", ".join(skills[:12])

    # 1. Update CLAUDE.md
    claude_md_path = os.path.join(BASE_DIR, "CLAUDE.md")
    claude_content = f"""# Job Application Assistant for {name}

## Role
This repo is a job application workspace. Claude acts as a career advisor and application assistant for {name}, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using templates
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** {name}
- **Location:** India (Open to Bangalore, Hyderabad, Pune, NCR, Remote India & Global Remote)
- **Phone:** {phone}
- **Email:** {email}
- **LinkedIn:** {linkedin}
- **GitHub:** {github}
- **Domain:** {domain} ({yoe} YoE)
- **Status:** Employed @ {current_company}
- **Languages:**
  | Language | Level |
  |----------|-------|
  | English | Professional working proficiency |

### Summary
{summary}

### Technical Skills
- **Core Skills:** {skills_str}
- **Domain:** {domain}

## Workflow for New Job Applications
1. Search jobs using `/scrape` or the Flask Web App
2. Evaluate and triage jobs using `/rank`
3. Prepare targeted applications using `/apply <url>`
"""
    try:
        with open(claude_md_path, "w", encoding="utf-8") as f:
            f.write(claude_content)
    except Exception:
        pass

    # 2. Update search-queries.md for Claude CLI /scrape
    search_queries_path = os.path.join(BASE_DIR, ".claude", "skills", "job-scraper", "search-queries.md")
    search_content = f"""# Search Queries for Job Scraper - {name}

## Target Domain: {domain}
Primary Skills: {skills_str}

## Query Categories

### Priority 1: {domain} Roles
#### Plain terms (portal CLIs)
```
{domain}
{" ".join(skills[:2])}
```

#### WebSearch-only (`site:` fallback)
```
site:linkedin.com/jobs "{domain}" India
site:linkedin.com/jobs "{domain}" Remote
site:naukri.com "{domain}" "{" ".join(skills[:2])}"
```
"""
    try:
        with open(search_queries_path, "w", encoding="utf-8") as f:
            f.write(search_content)
    except Exception:
        pass
