"""
CV Parser Service
Generic & Dynamic: Extracts candidate identity, skills, experience, education,
YoE, and primary domain from ANY software engineering CV (Frontend, Backend,
Full Stack, DevOps/Cloud, Mobile, Data/ML/AI, QA, Security).
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pypdf
except ImportError:
    pypdf = None

# Comprehensive generic taxonomy across all software engineering tracks
GENERIC_SKILL_TAXONOMY = {
    "Languages": [
        "Java", "Python", "Go", "Golang", "C++", "C#", "Rust", "JavaScript", "TypeScript",
        "Haskell", "Scala", "Kotlin", "Swift", "Ruby", "PHP", "Dart", "SQL", "R", "C / C++"
    ],
    "Frontend": [
        "React", "ReactJS", "Next.js", "Vue", "Vue.js", "Angular", "Svelte", "Redux",
        "Tailwind", "TailwindCSS", "HTML", "HTML5", "CSS", "CSS3", "Webpack", "Vite"
    ],
    "Backend & APIs": [
        "Node.js", "Express", "Spring Boot", "Spring", "Django", "FastAPI", "Flask",
        "Ruby on Rails", "ASP.NET", ".NET", "GraphQL", "gRPC", "REST APIs", "Microservices"
    ],
    "Databases & Storage": [
        "PostgreSQL", "MySQL", "Redis", "MongoDB", "Cassandra", "DynamoDB",
        "Elasticsearch", "SQLite", "Kafka", "AWS MSK", "RabbitMQ", "Snowflake"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker",
        "Kubernetes", "K8s", "Terraform", "CI/CD", "Jenkins", "GitHub Actions",
        "Linux", "Git", "CloudWatch", "Lambda", "AWS SQS", "Prometheus", "Grafana"
    ],
    "Data & AI/ML": [
        "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-Learn",
        "Pandas", "NumPy", "Spark", "Airflow", "LLMs", "Generative AI", "NLP", "AI Agents"
    ],
    "Mobile": [
        "Android", "iOS", "Flutter", "React Native", "SwiftUI", "Jetpack Compose"
    ],
    "Architecture & Core": [
        "Distributed Systems", "System Design", "Scalability", "Data Modeling",
        "High Concurrency", "Low Latency", "Event-Driven Architecture",
        "Object-Oriented Programming", "Functional Programming"
    ]
}


class CVParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract plain text from PDF, TXT, or Markdown file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            if fitz is not None:
                try:
                    doc = fitz.open(file_path)
                    text = "\n".join([page.get_text() for page in doc])
                    if text.strip():
                        return text
                except Exception:
                    pass

            if pypdf is not None:
                reader = pypdf.PdfReader(file_path)
                return "\n".join([page.extract_text() or "" for page in reader.pages])

            raise RuntimeError("Neither PyMuPDF nor pypdf is available to read PDF.")

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    @staticmethod
    def extract_links(file_path: str) -> Dict[str, str]:
        """Extract embedded hyperlinks from a PDF file."""
        links = {"linkedin": "", "github": "", "portfolio": "", "email": ""}
        ext = os.path.splitext(file_path)[1].lower()
        if ext != ".pdf":
            return links

        try:
            if pypdf is not None:
                reader = pypdf.PdfReader(file_path)
                for page in reader.pages:
                    if "/Annots" in page:
                        for annot in page["/Annots"]:
                            obj = annot.get_object()
                            if "/A" in obj and "/URI" in obj["/A"]:
                                uri = obj["/A"]["/URI"]
                                if "linkedin.com" in uri and not links["linkedin"]:
                                    links["linkedin"] = uri
                                elif "github.com" in uri and not links["github"]:
                                    links["github"] = uri
                                elif uri.startswith("mailto:") and not links["email"]:
                                    links["email"] = uri.replace("mailto:", "")
        except Exception:
            pass

        return links

    @classmethod
    def detect_primary_domain(cls, skills_by_category: Dict[str, List[str]], raw_text: str) -> str:
        """Automatically detect the engineering domain from extracted skills and text."""
        raw_lower = raw_text.lower()
        counts = {
            "Frontend": len(skills_by_category.get("Frontend", [])),
            "Backend": len(skills_by_category.get("Backend & APIs", [])) + len(skills_by_category.get("Databases & Storage", [])),
            "Data & AI": len(skills_by_category.get("Data & AI/ML", [])),
            "Cloud & DevOps": len(skills_by_category.get("Cloud & DevOps", [])),
            "Mobile": len(skills_by_category.get("Mobile", []))
        }

        # Bonus keyword mentions in text
        if any(term in raw_lower for term in ["frontend", "ui developer", "react developer"]):
            counts["Frontend"] += 3
        if any(term in raw_lower for term in ["backend", "distributed systems", "api developer", "microservices"]):
            counts["Backend"] += 3
        if any(term in raw_lower for term in ["machine learning", "data scientist", "data engineer", "deep learning"]):
            counts["Data & AI"] += 3
        if any(term in raw_lower for term in ["devops", "sre", "site reliability", "cloud engineer", "infrastructure"]):
            counts["Cloud & DevOps"] += 3
        if any(term in raw_lower for term in ["mobile developer", "android developer", "ios developer"]):
            counts["Mobile"] += 3

        # Fullstack detection
        if counts["Frontend"] >= 2 and counts["Backend"] >= 3:
            return "Full Stack Engineer"

        max_domain = max(counts, key=counts.get)
        if counts[max_domain] == 0:
            return "Software Engineer"

        domain_map = {
            "Frontend": "Frontend Engineer",
            "Backend": "Backend Engineer",
            "Data & AI": "Data & ML Engineer",
            "Cloud & DevOps": "DevOps / Cloud Engineer",
            "Mobile": "Mobile Engineer"
        }
        return domain_map.get(max_domain, "Software Engineer")

    @classmethod
    def parse(cls, file_path: str) -> Dict[str, Any]:
        """Full parsing pipeline on ANY resume file."""
        raw_text = cls.extract_text(file_path)
        extracted_links = cls.extract_links(file_path)

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # 1. Candidate Name
        name = "Candidate"
        if lines:
            first_line = lines[0]
            cleaned = re.sub(r'[^a-zA-Z\s]', '', first_line).strip()
            if 2 <= len(cleaned.split()) <= 4 and len(cleaned) < 50:
                name = cleaned

        # 2. Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
        email = extracted_links.get("email") or (email_match.group(0) if email_match else "")

        # 3. Phone
        phone_match = re.search(r'(?:\+?91[-\s]?)?[6789]\d{9}|(?:\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}', raw_text)
        phone = phone_match.group(0).strip() if phone_match else ""

        # 4. Links
        linkedin = extracted_links.get("linkedin")
        if not linkedin:
            li_match = re.search(r'(https?://(?:www\.)?linkedin\.com/in/[\w-]+)', raw_text, re.IGNORECASE)
            linkedin = li_match.group(0) if li_match else ""

        github = extracted_links.get("github")
        if not github:
            gh_match = re.search(r'(https?://(?:www\.)?github\.com/[\w-]+)', raw_text, re.IGNORECASE)
            github = gh_match.group(0) if gh_match else ""

        # 5. Skills Extraction (Strict word-boundary matching)
        skills_detected = []
        skills_by_category = {}
        raw_lower = raw_text.lower()

        for category, skills in GENERIC_SKILL_TAXONOMY.items():
            matched_in_cat = []
            for skill in skills:
                if skill == "C / C++":
                    if re.search(r'\b(c\s*/\s*c\+\+|c\s+and\s+c\+\+|c,\s*c\+\+)\b', raw_lower):
                        matched_in_cat.append("C / C++")
                        if "C / C++" not in skills_detected:
                            skills_detected.append("C / C++")
                    continue

                pattern = r'(?<![a-zA-Z0-9_#+])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9_#+])'
                if re.search(pattern, raw_lower):
                    matched_in_cat.append(skill)
                    if skill not in skills_detected:
                        skills_detected.append(skill)

            if matched_in_cat:
                skills_by_category[category] = matched_in_cat

        # 6. Detect Engineering Domain dynamically
        primary_domain = cls.detect_primary_domain(skills_by_category, raw_text)

        # 7. Experience & YoE Estimation
        yoe_match = re.search(r'(\d+)\+?\s*(?:years|yrs)\s*(?:of\s*)?(?:experience|exp)?', raw_lower)
        estimated_yoe = float(yoe_match.group(1)) if yoe_match else 0.0

        if not estimated_yoe:
            date_ranges = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\s*[\u2013\u2014\-to]+\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4}))', raw_text, re.IGNORECASE)
            if date_ranges:
                current_year = datetime.now().year
                total_months = 0
                for start_yr, end_yr in date_ranges:
                    s = int(start_yr)
                    e = int(end_yr) if end_yr else current_year
                    if e >= s and (current_year - s) < 25:
                        total_months += (e - s) * 12
                if total_months > 0:
                    estimated_yoe = round(total_months / 12.0, 1)

        if estimated_yoe == 0:
            estimated_yoe = 3.0

        if estimated_yoe >= 5:
            seniority = f"Senior {primary_domain}"
        elif estimated_yoe >= 2:
            seniority = f"Mid-Level {primary_domain} (SDE-2)"
        else:
            seniority = f"Associate {primary_domain} (SDE-1)"

        # 8. Current Company Extraction
        companies = []
        for line in lines:
            line_clean = line.strip()
            if any(term in line_clean.lower() for term in ["present", "software engineer", "developer", "architect", "engineer"]) and "|" in line_clean:
                parts = line_clean.split("|")
                comp = parts[0].strip()
                if 2 <= len(comp) <= 40 and not any(h in comp.lower() for h in ["summary", "skills", "experience", "education"]):
                    companies.append(comp)

        current_company = companies[0] if companies else "Tech Company"

        # 9. Summary
        summary = ""
        summary_idx = -1
        for i, line in enumerate(lines):
            if line.lower() in ["summary", "professional summary", "about"]:
                summary_idx = i
                break
        if summary_idx != -1 and summary_idx + 1 < len(lines):
            summary = " ".join(lines[summary_idx + 1: summary_idx + 4])
        else:
            for line in lines[1:6]:
                if len(line.split()) > 10 and not line.startswith("http"):
                    summary = line
                    break

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin or (f"https://www.linkedin.com/in/{name.lower().replace(' ', '')}" if name != "Candidate" else ""),
            "github": github,
            "summary": summary,
            "skills": skills_detected,
            "skills_by_category": skills_by_category,
            "primary_domain": primary_domain,
            "top_skills": skills_detected[:6],
            "estimated_yoe": estimated_yoe,
            "seniority_level": seniority,
            "current_company": current_company,
            "raw_text": raw_text
        }
