"""
Job Matcher Service
Evaluates and scores job postings against the candidate's extracted CV profile.
Generates match scores, skill comparisons, fit rationale, and 1-click referral outreach links.
"""

import urllib.parse
from typing import List, Dict, Any


class JobMatcher:
    @staticmethod
    def calculate_match(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single job against the candidate profile."""
        cand_skills = set(s.lower() for s in candidate.get("skills", []))
        job_req_skills = [s.strip() for s in job.get("skills_required", [])]
        
        desc_text = f"{job.get('title', '')} {job.get('description', '')}".lower()

        # 1. Skill Overlap
        matched_skills = []
        missing_skills = []

        for req in job_req_skills:
            req_lower = req.lower()
            if req_lower in cand_skills or any(req_lower in s for s in cand_skills) or req_lower in candidate.get("raw_text", "").lower():
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        # Also find any candidate skills present in description
        for c_skill in candidate.get("skills", []):
            if c_skill.lower() in desc_text and c_skill not in matched_skills:
                matched_skills.append(c_skill)

        # Deduplicate while preserving order
        matched_skills = list(dict.fromkeys(matched_skills))
        missing_skills = [s for s in missing_skills if s not in matched_skills]

        # Skill score
        total_skills_to_evaluate = max(len(job_req_skills), 4)
        skill_score = min(100.0, (len(matched_skills) / float(total_skills_to_evaluate)) * 100)

        # 2. Experience / YoE score
        cand_yoe = candidate.get("estimated_yoe", 3.0)
        min_yoe = job.get("min_yoe", 2)
        max_yoe = job.get("max_yoe", 6)

        if min_yoe <= cand_yoe <= max_yoe:
            exp_score = 95.0
        elif cand_yoe < min_yoe:
            gap = min_yoe - cand_yoe
            exp_score = max(40.0, 90.0 - (gap * 25.0))
        else: # Overqualified
            exp_score = 85.0

        # Title alignment bonus
        title_lower = job.get("title", "").lower()
        title_bonus = 0
        if any(term in title_lower for term in ["backend", "distributed", "software engineer", "sde", "developer"]):
            title_bonus += 5

        # Final weighted composite score (0-100)
        final_score = int(min(100, max(10, round(0.65 * skill_score + 0.35 * exp_score + title_bonus))))

        # Tier classification
        if final_score >= 78:
            match_tier = "High Match"
            tier_class = "success"
            badge_color = "bg-emerald-500 text-white"
        elif final_score >= 55:
            match_tier = "Medium Match"
            tier_class = "warning"
            badge_color = "bg-amber-500 text-white"
        else:
            match_tier = "Exploratory"
            tier_class = "info"
            badge_color = "bg-slate-500 text-white"

        # Fit rationale bullets
        why_fits = []
        if any(s.lower() in ["kafka", "microservices", "distributed systems", "aws"] for s in matched_skills):
            why_fits.append("Strong event-driven & distributed systems alignment (Kafka, Microservices, Cloud).")
        if any(s.lower() in ["java", "go", "c++", "python"] for s in matched_skills):
            matched_langs = [s for s in matched_skills if s.lower() in ["java", "go", "c++", "python"]]
            why_fits.append(f"Matches core backend languages: {', '.join(matched_langs)}.")
        if cand_yoe >= min_yoe:
            why_fits.append(f"Candidate's {cand_yoe} YoE satisfies the required experience bar ({min_yoe}-{max_yoe} yrs).")
        else:
            why_fits.append(f"Direct match with modern backend service and API development patterns.")

        # Manual checkpoints before applying
        checkpoints = []
        if missing_skills:
            checkpoints.append(f"Review domain gaps in posting: {', '.join(missing_skills[:3])}.")
        if "india" in job.get("region", "").lower() or "india" in job.get("location", "").lower():
            checkpoints.append("Verify notice period expectation (30-60 days typical for Indian tech recruiters).")
        else:
            checkpoints.append("Check remote timezone overlap requirements (e.g. US/EU vs IST hours).")

        # LinkedIn Referral Search Links
        company_clean = job.get("company", "").strip()
        recruiter_query = urllib.parse.quote(f"{company_clean} tech recruiter")
        hiring_mgr_query = urllib.parse.quote(f"{company_clean} engineering manager")

        recruiter_link = f"https://www.linkedin.com/search/results/people/?keywords={recruiter_query}&origin=GLOBAL_SEARCH_HEADER"
        peer_link = f"https://www.linkedin.com/search/results/people/?keywords={hiring_mgr_query}&origin=GLOBAL_SEARCH_HEADER"

        return {
            **job,
            "match_score": final_score,
            "match_tier": match_tier,
            "tier_class": tier_class,
            "badge_color": badge_color,
            "matched_skills": matched_skills[:10],
            "missing_skills": missing_skills[:6],
            "why_fits": why_fits[:3],
            "checkpoints": checkpoints[:2],
            "recruiter_link": recruiter_link,
            "peer_link": peer_link
        }

    @classmethod
    def rank_all(cls, candidate: Dict[str, Any], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and sort all jobs by match score descending."""
        scored = [cls.calculate_match(candidate, j) for j in jobs]
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored
