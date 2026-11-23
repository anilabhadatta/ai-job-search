"""
Tracker Service
Manages application tracking entries in job_search_tracker.csv, compatible with the framework.
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_TRACKER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "job_search_tracker.csv"))

CSV_HEADERS = [
    "date", "company", "sector", "role", "role_type", "channel",
    "status", "contact_person", "fit_rating", "notes", "cv_file",
    "cover_letter_file", "source", "deadline", "job_url"
]


class TrackerService:
    def __init__(self, file_path: str = DEFAULT_TRACKER_PATH):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)

    def get_all(self) -> List[Dict[str, Any]]:
        self._ensure_file()
        records = []
        with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(dict(row))
        return records

    def add_or_update(self,
                      company: str,
                      role: str,
                      status: str = "applied",
                      fit_rating: str = "High",
                      notes: str = "",
                      job_url: str = "",
                      source: str = "Web App",
                      deadline: str = "") -> Dict[str, Any]:
        records = self.get_all()
        found = False
        today = datetime.now().strftime("%Y-%m-%d")

        for r in records:
            if r.get("company", "").strip().lower() == company.strip().lower() and \
               r.get("role", "").strip().lower() == role.strip().lower():
                r["status"] = status
                if notes:
                    r["notes"] = notes
                if fit_rating:
                    r["fit_rating"] = fit_rating
                if job_url:
                    r["job_url"] = job_url
                found = True
                break

        if not found:
            records.insert(0, {
                "date": today,
                "company": company,
                "sector": "Technology",
                "role": role,
                "role_type": "Backend / Software Engineering",
                "channel": "Online / Career Portal",
                "status": status,
                "contact_person": "",
                "fit_rating": fit_rating,
                "notes": notes,
                "cv_file": "cv/aryashree_mazumder_resume.pdf",
                "cover_letter_file": "",
                "source": source,
                "deadline": deadline,
                "job_url": job_url
            })

        # Save back to CSV
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)

        return {"success": True, "count": len(records)}

    def delete(self, company: str, role: str) -> bool:
        records = self.get_all()
        new_records = [
            r for r in records
            if not (r.get("company", "").strip().lower() == company.strip().lower() and
                    r.get("role", "").strip().lower() == role.strip().lower())
        ]
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(new_records)
        return True
