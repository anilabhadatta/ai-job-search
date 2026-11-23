# AI Job Search - Flask Web Application

A web framework for AI-driven job search, resume fit analysis, and manual application workflow tailored for **Indian Software Companies (Bangalore, Hyderabad, Pune, NCR, Remote)** and **Global Remote** companies.

Configured with URL context prefix: **`/ai-job-search`** (e.g. `http://localhost:5000/ai-job-search`).

---

## Features

1. **URL Context Support (`/ai-job-search`)**:
   - Out of the box, all routes, assets, navigation, and API endpoints run under `/ai-job-search`.
   - Accessing root `/` automatically redirects to `/ai-job-search/`.
   - Custom prefix can be configured via `--url-context <prefix>` or `URL_PREFIX` environment variable.

2. **CV Upload & Ingestion**:
   - Upload any `.pdf`, `.txt`, or `.md` resume, or select existing files in `cv/` (e.g. `aryashree_mazumder_resume.pdf`) with 1 click.
   - Extracts candidate identity, skills, experience (YoE), seniority level, and contact links.

3. **Targeted Job Search**:
   - Curated & live openings across top Indian Tech Giants, Unicorns, and GCCs (Razorpay, Swiggy, PhonePe, CRED, InMobi, Zepto, Postman, Walmart Global Tech, Cisco, JPMorgan Chase).
   - Global Remote openings (Canonical, GitLab, Automattic, Kraken, and live API feeds via Remotive / Arbeitnow).

4. **Multi-Dimensional AI Fit Scoring**:
   - Calculates **Match Score (0–100%)** based on skill overlap, experience level (YoE), and domain alignment.
   - Highlights **Matched Skills** (green tags) and **Missing Skills / Gaps** (gray tags).
   - Generates bulleted **"Why it fits your background"** and **"Points to verify manually before applying"**.

5. **Manual Verification & 1-Click Outreach**:
   - Direct link to apply on the employer's career page.
   - 1-Click LinkedIn search links to connect with **Technical Recruiters** and **Engineering Managers** for referrals.

6. **Integrated Application Tracker**:
   - Save postings directly to `job_search_tracker.csv` with status updates (`Saved`, `Applied`, `Interview`, `Offer`, `Rejected`).
   - Export results and tracker to CSV or JSON.

---

## Quick Start

### Linux / macOS (Setup & Server in 1 Command)
```bash
chmod +x start_linux.sh
./start_linux.sh
```
*Note: `start_linux.sh` automatically checks dependencies, creates `.venv`, installs requirements, and skips setup on subsequent runs for instant launches.*

### Windows
```cmd
start_web.bat
```
or via PowerShell:
```powershell
.\start_web.ps1
```

### Manual Launch
```bash
python run_web.py
```
Open **[http://localhost:5000/ai-job-search](http://localhost:5000/ai-job-search)** in your browser.
*(Visiting `http://localhost:5000/` automatically redirects to `/ai-job-search/`)*

### Custom Port or Context
```bash
# Run on custom port 8080:
./start_linux.sh --port 8080
# or on Windows: python run_web.py --port 8080

# Run with custom URL context:
python run_web.py --url-context /my-portal

# Run with production Waitress WSGI server:
./start_linux.sh --prod --port 5000
```

---

## Reverse Proxy (Nginx) Example

If hosting behind Nginx with the `/ai-job-search` context:

```nginx
location /ai-job-search/ {
    proxy_pass http://127.0.0.1:5000/ai-job-search/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```
