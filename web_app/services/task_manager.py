"""
Background Task Manager for Asynchronous Job Matching and AI Search
Handles asynchronous background execution of:
1. OpenAI Codex live web job discovery (ChatGPT Plus)
2. Remote feed and portal scraping (concurrently)
3. ATS job matching & ranking
4. AI strategic advice generation
Provides thread-safe progress tracking and status polling endpoints.
"""

import time
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List

from web_app.services.job_searcher import JobSearcher
from web_app.services.job_matcher import JobMatcher
from web_app.services.claude_runner import ClaudeRunner
from web_app.services.claude_sync import sync_to_claude_cli


class TaskManager:
    """Thread-safe background task store and executor."""
    
    _lock = threading.Lock()
    _tasks: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _cleanup_old_tasks(cls, max_age_seconds: int = 3600):
        """Prune tasks older than max_age_seconds to prevent memory accumulation."""
        now = time.time()
        with cls._lock:
            to_delete = [
                tid for tid, task in cls._tasks.items()
                if now - task.get("created_timestamp", now) > max_age_seconds
            ]
            for tid in to_delete:
                cls._tasks.pop(tid, None)

    @classmethod
    def create_task(cls, initial_stage: str = "Initializing pipeline...") -> str:
        """Create a new task entry and return its unique task_id."""
        cls._cleanup_old_tasks()
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "status": "pending",           # pending | running | completed | failed
            "progress": 5,                 # 0 to 100
            "stage": initial_stage,
            "created_timestamp": time.time(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "candidate": None,
            "codex_jobs": [],
            "ranked_jobs": [],
            "claude_status": None,
            "metrics": {},
            "min_lpa": 0.0,
            "region": "All",
            "role_query": "Backend",
            "max_days": 7,
            "sort_by": "match_desc",
            "error": None
        }
        with cls._lock:
            cls._tasks[task_id] = task_data
        return task_id

    @classmethod
    def get_task(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve task data by ID in a thread-safe manner."""
        with cls._lock:
            task = cls._tasks.get(task_id)
            if task:
                return dict(task)
            return None

    @classmethod
    def update_task(cls, task_id: str, **kwargs):
        """Update fields on an existing task."""
        with cls._lock:
            if task_id in cls._tasks:
                cls._tasks[task_id].update(kwargs)

    @classmethod
    def start_pipeline_async(
        cls,
        candidate_data: Dict[str, Any],
        run_codex: bool = True,
        min_lpa: float = 0.0,
        region: str = "All",
        role_query: str = "Backend",
        max_days: int = 7,
        sort_by: str = "match_desc"
    ) -> str:
        """
        Spawns a background worker thread to execute the full job discovery & ranking pipeline
        asynchronously without blocking the HTTP request thread.
        """
        task_id = cls.create_task("Setting up candidate profile...")

        worker = threading.Thread(
            target=cls._run_pipeline_worker,
            args=(task_id, candidate_data, run_codex, min_lpa, region, role_query, max_days, sort_by),
            daemon=True
        )
        worker.start()
        return task_id

    @classmethod
    def _run_pipeline_worker(
        cls,
        task_id: str,
        candidate_data: Dict[str, Any],
        run_codex: bool,
        min_lpa: float,
        region: str,
        role_query: str,
        max_days: int,
        sort_by: str
    ):
        """Background worker thread function."""
        try:
            # Stage 1: Profile synchronization (15%)
            cls.update_task(
                task_id,
                status="running",
                progress=15,
                stage="Synchronizing candidate profile with AI engine...",
                candidate=candidate_data,
                min_lpa=min_lpa,
                region=region,
                role_query=role_query,
                max_days=max_days,
                sort_by=sort_by
            )
            try:
                sync_to_claude_cli(candidate_data)
            except Exception:
                pass

            # Stage 2: OpenAI Codex Live Discovery (35%)
            codex_jobs: List[Dict[str, Any]] = []
            if run_codex:
                cls.update_task(
                    task_id,
                    progress=35,
                    stage="🤖 OpenAI Codex (ChatGPT Plus): Searching live web for direct requisitions..."
                )
                try:
                    codex_jobs = ClaudeRunner.search_jobs_with_codex(
                        skills=candidate_data.get("skills", []),
                        role=candidate_data.get("primary_domain", role_query),
                        region=region,
                        limit=4,
                        timeout_sec=55
                    )
                except Exception as e:
                    codex_jobs = []

            cls.update_task(task_id, codex_jobs=codex_jobs)

            # Stage 3: Scanning Tech Giants & Remote Feeds (65%)
            cls.update_task(
                task_id,
                progress=65,
                stage="🌐 Concurrently scanning 70+ Tech Giants, Unicorns, and Live Remote feeds..."
            )
            jobs = JobSearcher.search(
                candidate_skills=candidate_data.get("skills", []),
                region_filter=region,
                role_query=role_query,
                max_days=max_days,
                min_lpa=min_lpa,
                codex_jobs=codex_jobs,
                limit=75
            )

            # Stage 4: AI Matching & Ranking (85%)
            cls.update_task(
                task_id,
                progress=85,
                stage="🎯 AI Fit Scoring & Pre-Apply Gap Checks against candidate skills..."
            )
            ranked_jobs = JobMatcher.rank_all(candidate_data, jobs, sort_by=sort_by)

            # Calculate metrics
            unique_companies = sorted(list(set(j.get("company", "").strip() for j in ranked_jobs if j.get("company"))))
            metrics = {
                "total_count": len(ranked_jobs),
                "company_count": len(unique_companies),
                "high_count": sum(1 for j in ranked_jobs if j.get("match_tier") == "High Match"),
                "med_count": sum(1 for j in ranked_jobs if j.get("match_tier") == "Medium Match"),
                "expl_count": sum(1 for j in ranked_jobs if j.get("match_tier") == "Exploratory"),
                "codex_count": sum(1 for j in ranked_jobs if j.get("source_type") == "codex"),
                "ats_count": sum(1 for j in ranked_jobs if j.get("source_type") == "ats_portal"),
                "live_scraped_count": sum(1 for j in ranked_jobs if j.get("source_type") == "live_feed"),
                "career_portal_count": sum(1 for j in ranked_jobs if j.get("source_type") == "career_portal")
            }

            # Stage 5: Strategic Application Advisory (95%)
            cls.update_task(
                task_id,
                progress=95,
                stage="⚡ Generating strategic career recommendations..."
            )
            claude_status = ClaudeRunner.execute_claude_pipeline(candidate_data, timeout_sec=12)

            # Stage 6: Completion (100%)
            cls.update_task(
                task_id,
                status="completed",
                progress=100,
                stage="✅ Matching complete! Rendering your tailored job opportunities...",
                ranked_jobs=ranked_jobs,
                claude_status=claude_status,
                metrics=metrics,
                completed_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

        except Exception as e:
            cls.update_task(
                task_id,
                status="failed",
                error=str(e),
                stage=f"Pipeline error: {str(e)}"
            )
