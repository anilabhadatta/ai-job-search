"""
Flask Web Application for AI Job Search
Provides a web interface for CV upload, job search across Indian & Global tech companies,
AI fit scoring, manual application verification, and application tracking.
Supports configurable URL context / base prefix (e.g. /ai-job-search).
Keeps profile synchronized with Claude Code CLI (/scrape, /rank, /apply) and
auto-executes Claude CLI upon upload.
"""

import os
import json
import csv
import io
from flask import (
    Flask, Blueprint, render_template, request, redirect, url_for,
    flash, session, jsonify, send_file, Response
)
from werkzeug.utils import secure_filename

from web_app.services.cv_parser import CVParser
from web_app.services.job_searcher import JobSearcher
from web_app.services.job_matcher import JobMatcher
from web_app.services.tracker_service import TrackerService
from web_app.services.claude_sync import sync_to_claude_cli
from web_app.services.claude_runner import ClaudeRunner
from web_app.services.task_manager import TaskManager

# Base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
CV_FOLDER = os.path.join(BASE_DIR, "cv")
ALLOWED_EXTENSIONS = {"pdf", "txt", "md"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CV_FOLDER, exist_ok=True)

# URL Context / Base Prefix (e.g. '/ai-job-search')
raw_prefix = os.environ.get("URL_PREFIX", "/ai-job-search").strip()
if raw_prefix and not raw_prefix.startswith("/"):
    raw_prefix = "/" + raw_prefix
URL_PREFIX = raw_prefix.rstrip("/") if raw_prefix != "/" else ""

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ai-job-search-dev-secret-key-2026")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max
app.config["URL_PREFIX"] = URL_PREFIX

# Create Blueprint with url_prefix
main_bp = Blueprint("main", __name__, url_prefix=URL_PREFIX or None)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_existing_cvs():
    """List any PDF or TXT resume files in cv/ directory."""
    files = []
    if os.path.exists(CV_FOLDER):
        for f in os.listdir(CV_FOLDER):
            if f.lower().endswith((".pdf", ".txt", ".md")) and not f.startswith("."):
                files.append(f)
    return files


@app.context_processor
def inject_context():
    """Make URL prefix and active candidate available to all templates."""
    return {
        "url_prefix": URL_PREFIX,
        "candidate": session.get("candidate")
    }


# Root redirect if URL_PREFIX is active and request arrives at /
if URL_PREFIX:
    @app.route("/")
    def root_redirect():
        return redirect(f"{URL_PREFIX}/")


@main_bp.route("/")
@main_bp.route("")
def index():
    existing_cvs = get_existing_cvs()
    has_active_profile = "candidate" in session
    return render_template(
        "index.html",
        existing_cvs=existing_cvs,
        has_active_profile=has_active_profile,
        candidate=session.get("candidate")
    )


@main_bp.route("/upload", methods=["POST"])
def upload_cv():
    region = request.form.get("region", "All")
    role_query = request.form.get("role_query", "auto")
    max_days = int(request.form.get("max_days", 7))
    existing_file = request.form.get("existing_file")
    review_skills = request.form.get("review_skills") == "true"

    target_path = None

    # Option 1: Existing file chosen
    if existing_file and os.path.exists(os.path.join(CV_FOLDER, existing_file)):
        target_path = os.path.join(CV_FOLDER, existing_file)
    # Option 2: Uploaded file
    elif "cv_file" in request.files:
        file = request.files["cv_file"]
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            target_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(target_path)
            try:
                import shutil
                shutil.copy(target_path, os.path.join(CV_FOLDER, filename))
            except Exception:
                pass

    if not target_path or not os.path.exists(target_path):
        flash("Please upload a valid CV (.pdf, .txt, .md) or choose an existing one.", "error")
        return redirect(url_for("main.index"))

    try:
        candidate_data = CVParser.parse(target_path)
        
        # Determine role focus dynamically from CV
        if not role_query or role_query == "auto":
            role_query = candidate_data.get("primary_domain", "Software Engineer")

        # Automatically synchronize profile with Claude Code CLI
        sync_to_claude_cli(candidate_data)

        session["candidate"] = {k: v for k, v in candidate_data.items() if k != "raw_text"}
        session["region"] = region
        session["role_query"] = role_query
        session["max_days"] = max_days
        session["cv_filename"] = os.path.basename(target_path)

        if review_skills:
            return redirect(url_for("main.review_skills_view"))

        # If review not requested, execute pipeline asynchronously in background
        task_id = TaskManager.start_pipeline_async(
            candidate_data=candidate_data,
            run_codex=True,
            min_lpa=0.0,
            region=region,
            role_query=role_query,
            max_days=max_days
        )
        return redirect(url_for("main.analyzing_view", task_id=task_id))
    except Exception as e:
        flash(f"Failed to parse CV: {str(e)}", "error")
        return redirect(url_for("main.index"))


@main_bp.route("/analyzing")
def analyzing_view():
    task_id = request.args.get("task_id")
    if not task_id:
        return redirect(url_for("main.index"))
    return render_template("analyzing.html", task_id=task_id)


@main_bp.route("/api/tasks/<task_id>/status")
def api_task_status(task_id: str):
    task = TaskManager.get_task(task_id)
    if not task:
        return jsonify({"status": "failed", "error": "Task not found", "progress": 0}), 404
    return jsonify({
        "task_id": task["task_id"],
        "status": task["status"],
        "progress": task.get("progress", 0),
        "stage": task.get("stage", ""),
        "error": task.get("error")
    })


@main_bp.route("/api/tasks/start", methods=["POST"])
def api_start_task():
    """Start an asynchronous job discovery task via JSON API."""
    data = request.get_json(silent=True) or request.form
    candidate = data.get("candidate") or session.get("candidate")
    if not candidate:
        return jsonify({"error": "No candidate profile provided"}), 400

    run_codex = str(data.get("run_codex", "true")).lower() in ("true", "1", "yes")
    try:
        min_lpa = float(data.get("min_lpa", 0))
    except Exception:
        min_lpa = 0.0
    region = data.get("region", "All")
    role_query = data.get("role_query") or candidate.get("primary_domain", "Backend")
    try:
        max_days = int(data.get("max_days", 7))
    except Exception:
        max_days = 7

    task_id = TaskManager.start_pipeline_async(
        candidate_data=candidate,
        run_codex=run_codex,
        min_lpa=min_lpa,
        region=region,
        role_query=role_query,
        max_days=max_days
    )
    return jsonify({"success": True, "task_id": task_id, "status": "running"})


@main_bp.route("/api/rematch-async", methods=["POST"])
def api_rematch_async():
    """Async endpoint for inline re-matching from results page drawer."""
    data = request.get_json(silent=True) or request.form
    candidate = session.get("candidate", {})

    raw_skills = data.get("custom_skills") or data.get("skills") or ""
    if raw_skills:
        skills = [s.strip() for s in raw_skills.split(",") if s.strip() and s.strip() != "C"]
        if skills:
            candidate["skills"] = skills

    primary_domain = data.get("primary_domain") or candidate.get("primary_domain", "Backend")
    candidate["primary_domain"] = primary_domain

    try:
        min_lpa = float(data.get("min_lpa", 0))
    except Exception:
        min_lpa = 0.0

    region = data.get("region") or session.get("region", "All")
    run_codex = str(data.get("run_codex", "false")).lower() in ("true", "1", "yes")

    session["candidate"] = candidate
    session["min_lpa"] = min_lpa
    session["region"] = region
    session["role_query"] = primary_domain

    task_id = TaskManager.start_pipeline_async(
        candidate_data=candidate,
        run_codex=run_codex,
        min_lpa=min_lpa,
        region=region,
        role_query=primary_domain,
        max_days=7
    )
    return jsonify({"success": True, "task_id": task_id, "status": "running"})


@main_bp.route("/review-skills")
def review_skills_view():
    candidate = session.get("candidate")
    if not candidate:
        flash("Please upload a CV or select a profile first.", "info")
        return redirect(url_for("main.index"))
    return render_template(
        "review_skills.html",
        candidate=candidate,
        region=session.get("region", "All"),
        max_days=session.get("max_days", 7)
    )


@main_bp.route("/direct-skills-input", methods=["POST"])
def direct_skills_input():
    name = request.form.get("name", "Candidate").strip()
    primary_domain = request.form.get("primary_domain", "Backend")
    try:
        estimated_yoe = float(request.form.get("estimated_yoe", 4.0))
    except Exception:
        estimated_yoe = 4.0
    raw_skills = request.form.get("skills", "")
    try:
        min_lpa = float(request.form.get("min_lpa", 0))
    except Exception:
        min_lpa = 0.0
    region = request.form.get("region", "All")

    skills = [s.strip() for s in raw_skills.split(",") if s.strip() and s.strip() != "C"]
    candidate_data = {
        "name": name,
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "current_company": "Tech Company",
        "primary_domain": primary_domain,
        "estimated_yoe": estimated_yoe,
        "skills": skills,
        "summary": f"{primary_domain} Engineer with {estimated_yoe} years of experience."
    }
    session["candidate"] = candidate_data
    session["region"] = region
    session["role_query"] = primary_domain
    session["min_lpa"] = min_lpa
    session["max_days"] = 7
    sync_to_claude_cli(candidate_data)
    return redirect(url_for("main.review_skills_view"))


@main_bp.route("/analyze-custom-skills", methods=["POST"])
def analyze_custom_skills():
    candidate = session.get("candidate", {})
    name = request.form.get("name", candidate.get("name", "Candidate")).strip()
    primary_domain = request.form.get("primary_domain", candidate.get("primary_domain", "Backend"))
    try:
        estimated_yoe = float(request.form.get("estimated_yoe", candidate.get("estimated_yoe", 4.0)))
    except Exception:
        estimated_yoe = 4.0

    raw_skills = request.form.get("custom_skills", "")
    skills = [s.strip() for s in raw_skills.split(",") if s.strip() and s.strip() != "C"]
    if not skills:
        skills = candidate.get("skills", ["Java", "Python", "SQL", "Cloud"])

    try:
        min_lpa = float(request.form.get("min_lpa", 0))
    except Exception:
        min_lpa = 0.0
    region = request.form.get("region", "All")
    run_codex = request.form.get("run_codex") == "true"

    # Update candidate in session
    candidate["name"] = name
    candidate["primary_domain"] = primary_domain
    candidate["estimated_yoe"] = estimated_yoe
    candidate["skills"] = skills
    session["candidate"] = candidate
    session["region"] = region
    session["role_query"] = primary_domain
    session["min_lpa"] = min_lpa

    # Sync profile with CLAUDE.md
    sync_to_claude_cli(candidate)

    # Launch asynchronous background pipeline (Codex AI + concurrent feeds + ranking)
    task_id = TaskManager.start_pipeline_async(
        candidate_data=candidate,
        run_codex=run_codex,
        min_lpa=min_lpa,
        region=region,
        role_query=primary_domain,
        max_days=7
    )

    return redirect(url_for("main.analyzing_view", task_id=task_id))


@main_bp.route("/results")
def results():
    task_id = request.args.get("task_id")
    task = TaskManager.get_task(task_id) if task_id else None

    # If coming from an async task, hydrate session from the completed task
    if task and task.get("status") == "completed":
        if task.get("candidate"):
            session["candidate"] = task["candidate"]
        session["codex_jobs"] = task.get("codex_jobs", [])
        session["claude_status"] = task.get("claude_status")
        session["min_lpa"] = task.get("min_lpa", 0.0)
        session["region"] = task.get("region", "All")
        session["role_query"] = task.get("role_query", "Backend")

    candidate = session.get("candidate")
    if not candidate:
        flash("Please upload your CV first.", "info")
        return redirect(url_for("main.index"))

    # Sanitize skills to ensure no legacy cached single-letter "C"
    if "skills" in candidate:
        candidate["skills"] = [s for s in candidate.get("skills", []) if s != "C"]
        session["candidate"] = candidate

    region = request.args.get("region") or session.get("region", "All")
    role_query = request.args.get("role_query") or session.get("role_query", candidate.get("primary_domain", "Backend"))
    max_days_raw = request.args.get("max_days")
    max_days = int(max_days_raw) if max_days_raw and max_days_raw.isdigit() else session.get("max_days", 7)
    
    min_lpa_raw = request.args.get("min_lpa")
    try:
        min_lpa = float(min_lpa_raw) if min_lpa_raw is not None else float(session.get("min_lpa", 0))
    except Exception:
        min_lpa = 0.0

    sort_by = request.args.get("sort_by", "match_desc")
    claude_status = session.get("claude_status")

    # If the async task already ranked jobs with matching filters, use them instantly!
    if task and task.get("ranked_jobs") and not request.args.get("min_lpa") and not request.args.get("sort_by"):
        ranked_jobs = task["ranked_jobs"]
    else:
        # Get cached Codex jobs from session
        codex_jobs = session.get("codex_jobs", [])

        # Fetch jobs across the expanded 70+ company catalog, live feeds & Codex discoveries
        jobs = JobSearcher.search(
            candidate_skills=candidate.get("skills", []),
            region_filter=region,
            role_query=role_query,
            max_days=max_days,
            min_lpa=min_lpa,
            codex_jobs=codex_jobs,
            limit=75
        )

        # Score and rank jobs
        ranked_jobs = JobMatcher.rank_all(candidate, jobs, sort_by=sort_by)

    # Calculate metrics
    unique_companies = sorted(list(set(j.get("company", "").strip() for j in ranked_jobs if j.get("company"))))
    company_count = len(unique_companies)
    high_count = sum(1 for j in ranked_jobs if j.get("match_tier") == "High Match")
    med_count = sum(1 for j in ranked_jobs if j.get("match_tier") == "Medium Match")
    expl_count = sum(1 for j in ranked_jobs if j.get("match_tier") == "Exploratory")
    codex_count = sum(1 for j in ranked_jobs if j.get("source_type") == "codex")
    live_scraped_count = sum(1 for j in ranked_jobs if j.get("source_type") == "live_feed")
    career_portal_count = sum(1 for j in ranked_jobs if j.get("source_type") == "career_portal")

    return render_template(
        "results.html",
        candidate=candidate,
        jobs=ranked_jobs,
        region=region,
        role_query=role_query,
        max_days=max_days,
        min_lpa=min_lpa,
        sort_by=sort_by,
        company_count=company_count,
        unique_companies=unique_companies,
        claude_status=claude_status,
        high_count=high_count,
        med_count=med_count,
        expl_count=expl_count,
        codex_count=codex_count,
        live_scraped_count=live_scraped_count,
        career_portal_count=career_portal_count,
        total_count=len(ranked_jobs)
    )


@main_bp.route("/api/search", methods=["POST"])
def api_search():
    candidate = session.get("candidate")
    if not candidate:
        return jsonify({"error": "No candidate profile found. Please upload a CV first."}), 400

    data = request.get_json() or {}
    region = data.get("region", session.get("region", "All"))
    role_query = data.get("role_query", session.get("role_query", "Backend"))
    max_days = int(data.get("max_days", session.get("max_days", 7)))
    sort_by = data.get("sort_by", "match_desc")

    jobs = JobSearcher.search(
        candidate_skills=candidate.get("skills", []),
        region_filter=region,
        role_query=role_query,
        max_days=max_days,
        limit=70
    )
    ranked_jobs = JobMatcher.rank_all(candidate, jobs, sort_by=sort_by)

    return jsonify({
        "success": True,
        "count": len(ranked_jobs),
        "company_count": len(set(j.get("company", "") for j in ranked_jobs)),
        "jobs": ranked_jobs
    })


@main_bp.route("/tracker")
def tracker():
    tracker_service = TrackerService()
    records = tracker_service.get_all()
    return render_template("tracker.html", records=records, count=len(records))


@main_bp.route("/api/tracker/update", methods=["POST"])
def api_tracker_update():
    data = request.get_json() or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()
    status = data.get("status", "applied")
    fit_rating = data.get("fit_rating", "High")
    notes = data.get("notes", "")
    job_url = data.get("job_url", "")
    source = data.get("source", "Web App")

    if not company or not role:
        return jsonify({"error": "Company and role are required."}), 400

    tracker_service = TrackerService()
    res = tracker_service.add_or_update(
        company=company,
        role=role,
        status=status,
        fit_rating=fit_rating,
        notes=notes,
        job_url=job_url,
        source=source
    )
    return jsonify(res)


@main_bp.route("/api/tracker/delete", methods=["POST"])
def api_tracker_delete():
    data = request.get_json() or {}
    company = data.get("company", "").strip()
    role = data.get("role", "").strip()

    if not company or not role:
        return jsonify({"error": "Company and role are required."}), 400

    tracker_service = TrackerService()
    tracker_service.delete(company, role)
    return jsonify({"success": True})


@main_bp.route("/export/tracker")
def export_tracker():
    tracker_service = TrackerService()
    records = tracker_service.get_all()

    output = io.StringIO()
    if records:
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    else:
        output.write("No records found.")

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=job_search_tracker.csv"}
    )


@main_bp.route("/export/results")
def export_results():
    candidate = session.get("candidate")
    if not candidate:
        flash("No active search results.", "warning")
        return redirect(url_for("main.index"))

    region = session.get("region", "All")
    role_query = session.get("role_query", "Backend")
    max_days = int(request.args.get("max_days", 7))
    sort_by = request.args.get("sort_by", "match_desc")

    jobs = JobSearcher.search(
        candidate_skills=candidate.get("skills", []),
        region_filter=region,
        role_query=role_query,
        max_days=max_days,
        limit=70
    )
    ranked = JobMatcher.rank_all(candidate, jobs, sort_by=sort_by)

    fmt = request.args.get("format", "json").lower()
    if fmt == "csv":
        output = io.StringIO()
        fieldnames = ["match_score", "match_tier", "company", "title", "location", "salary_range", "posted_date", "url", "matched_skills"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for j in ranked:
            row = dict(j)
            row["matched_skills"] = ", ".join(j.get("matched_skills", []))
            writer.writerow(row)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=matched_jobs.csv"}
        )

    return jsonify(ranked)


@main_bp.route("/reset")
def reset_session():
    session.clear()
    flash("Session reset.", "info")
    return redirect(url_for("main.index"))


# Register Blueprint
app.register_blueprint(main_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
