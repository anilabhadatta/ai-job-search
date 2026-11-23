"""
Job Matcher Service
Evaluates and scores job postings against the candidate's extracted CV profile.
Generates accurate, differentiated match scores, skill comparisons, fit rationale,
and 1-click LinkedIn referral outreach links.
"""

import urllib.parse
from typing import List, Dict, Any


class JobMatcher:
    @staticmethod
    def calculate_match(candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Score a single job against the candidate profile with strict ATS accuracy."""
        cand_skills_raw = candidate.get("skills", [])
        cand_skills_lower = set(s.lower() for s in cand_skills_raw if s.lower() != "c")
        cand_raw_text = candidate.get("raw_text", "").lower()

        job_req_skills = [s.strip() for s in job.get("skills_required", []) if s.strip().lower() != "c"]
        desc_text = f"{job.get('title', '')} {job.get('description', '')}".lower()

        # 1. Compare Required Skills
        matched_required = []
        missing_required = []

        for req in job_req_skills:
            req_lower = req.lower()
            is_match = False
            # Direct match
            if req_lower in cand_skills_lower:
                is_match = True
            # Substring/alias match (e.g. "AWS" matches "AWS SQS", "Postgres" matches "PostgreSQL")
            elif any(req_lower in s or s in req_lower for s in cand_skills_lower):
                is_match = True
            elif req_lower in cand_raw_text and len(req_lower) > 2:
                is_match = True

            if is_match:
                matched_required.append(req)
            else:
                missing_required.append(req)

        # 2. Check for Bonus Candidate Skills mentioned in Job Description
        bonus_skills = []
        for c_skill in cand_skills_raw:
            c_lower = c_skill.lower()
            if c_lower == "c":
                continue
            if c_skill not in matched_required and c_lower in desc_text and len(c_lower) > 2:
                bonus_skills.append(c_skill)

        # Total matched skills to display (clean & deduplicated)
        all_matched_display = list(dict.fromkeys(matched_required + bonus_skills[:3]))
        # Clean up any bare single-letter "C"
        all_matched_display = [s for s in all_matched_display if s != "C"]

        # 3. Calculate Core Skill Score (0 to 100)
        total_required_count = len(job_req_skills) if job_req_skills else 5
        base_skill_ratio = len(matched_required) / float(total_required_count)
        
        # Skill score with small bonus for complementary candidate strengths
        bonus_points = min(10.0, len(bonus_skills) * 3.0)
        core_skill_score = min(100.0, (base_skill_ratio * 90.0) + bonus_points)

        # If key required skills are missing, apply realistic deduction
        if missing_required:
            core_skill_score = min(core_skill_score, 100.0 - (len(missing_required) * 6.5))

        # 4. Experience & YoE Score (0 to 100)
        cand_yoe = candidate.get("estimated_yoe", 3.0)
        min_yoe = job.get("min_yoe", 2)
        max_yoe = job.get("max_yoe", 6)

        if min_yoe <= cand_yoe <= max_yoe:
            exp_score = 95.0
        elif cand_yoe < min_yoe:
            gap = min_yoe - cand_yoe
            exp_score = max(35.0, 85.0 - (gap * 25.0))
        else: # Overqualified / above band
            exp_score = 88.0

        # 5. Role Alignment Score (0 to 100)
        title_lower = job.get("title", "").lower()
        role_score = 85.0
        if any(term in title_lower for term in ["backend", "distributed systems", "sde-2", "software engineer", "platform"]):
            role_score = 95.0

        # 6. Composite Score (Weighted: 60% Skills + 25% Experience + 15% Role Alignment)
        final_score = round(0.60 * core_skill_score + 0.25 * exp_score + 0.15 * role_score)
        # Cap at 95% for realistic ATS calibration
        final_score = int(min(95, max(30, final_score)))

        # 7. Tier Classification
        if final_score >= 82:
            match_tier = "High Match"
            tier_class = "success"
            badge_color = "bg-emerald-500 text-white"
        elif final_score >= 65:
            match_tier = "Medium Match"
            tier_class = "warning"
            badge_color = "bg-amber-500 text-white"
        else:
            match_tier = "Exploratory"
            tier_class = "info"
            badge_color = "bg-slate-500 text-white"

        # 8. Fit Rationale Bullets
        why_fits = []
        if any(s.lower() in ["kafka", "microservices", "distributed systems", "aws", "aws msk", "aws sqs"] for s in all_matched_display):
            why_fits.append("Direct alignment with your Kafka, microservices & distributed messaging experience.")
        if any(s.lower() in ["java", "go", "c++", "python"] for s in all_matched_display):
            matched_langs = [s for s in all_matched_display if s.lower() in ["java", "go", "c++", "python"]]
            why_fits.append(f"Strong language fit: {', '.join(matched_langs)}.")
        if cand_yoe >= min_yoe:
            why_fits.append(f"Candidate YoE ({cand_yoe} yrs) satisfies required band ({min_yoe}-{max_yoe} yrs).")
        else:
            why_fits.append("Solid core architecture and API engineering match.")

        # 9. Realistic Checkpoints Before Applying
        checkpoints = []
        if missing_required:
            checkpoints.append(f"Skill gap to check in posting: {', '.join(missing_required[:3])}.")
        if "india" in job.get("region", "").lower() or "india" in job.get("location", "").lower():
            checkpoints.append("Verify recruiter notice period bar (30-60 days typical for Indian tech recruiters).")
        else:
            checkpoints.append("Check timezone overlap requirements (e.g. US/EU vs IST hours).")

        # 10. LinkedIn Referral Search Links
        company_clean = job.get("company", "").strip()
        recruiter_query = urllib.parse.quote(f"{company_clean} technical recruiter")
        hiring_mgr_query = urllib.parse.quote(f"{company_clean} engineering manager")

        recruiter_link = f"https://www.linkedin.com/search/results/people/?keywords={recruiter_query}&origin=GLOBAL_SEARCH_HEADER"
        peer_link = f"https://www.linkedin.com/search/results/people/?keywords={hiring_mgr_query}&origin=GLOBAL_SEARCH_HEADER"

        # Skills match ratio string
        match_ratio_str = f"{len(matched_required)}/{total_required_count} required skills"

        return {
            **job,
            "match_score": final_score,
            "match_tier": match_tier,
            "match_ratio_str": match_ratio_str,
            "tier_class": tier_class,
            "badge_color": badge_color,
            "matched_skills": all_matched_display[:8],
            "missing_skills": missing_required[:4],
            "why_fits": why_fits[:3],
            "checkpoints": checkpoints[:2],
            "recruiter_link": recruiter_link,
            "peer_link": peer_link
        }

    @classmethod
    def rank_all(cls, candidate: Dict[str, Any], jobs: List[Dict[str, Any]], sort_by: str = "match_desc") -> List[Dict[str, Any]]:
        """Score and sort jobs according to user criteria."""
        scored = [cls.calculate_match(candidate, j) for j in jobs]

        if sort_by == "match_asc":
            scored.sort(key=lambda x: x["match_score"])
        elif sort_by == "recent":
            scored.sort(key=lambda x: x.get("posted_days_ago", 99))
        elif sort_by == "company":
            scored.sort(key=lambda x: x.get("company", "").lower())
        else: # match_desc (default)
            scored.sort(key=lambda x: (x["match_score"], -x.get("posted_days_ago", 99)), reverse=True)

        return scored
