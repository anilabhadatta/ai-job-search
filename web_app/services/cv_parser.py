"""
CV Parser Service
Extracts candidate identity, skills, experience, education, and YoE from resumes (PDF, TXT, MD).
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# Curated skill taxonomy for software engineering
SKILL_TAXONOMY = {
    "Languages": [
        "Java", "Python", "Go", "Golang", "C++", "C", "C#", "Rust", "JavaScript", "TypeScript",
        "Haskell", "ReScript", "Scala", "Kotlin", "Ruby", "PHP", "Swift", "Dart", "SQL", "HTML", "CSS"
    ],
    "Frameworks & Web": [
        "React", "ReactJS", "Node.js", "NodeJS", "Next.js", "Express", "Spring", "Spring Boot",
        "Django", "FastAPI", "Flask", "Angular", "Vue", "Vue.js", "GraphQL", "gRPC", "REST", "REST APIs"
    ],
    "Databases & Storage": [
        "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB",
        "Elasticsearch", "SQLite", "Oracle", "Kafka", "RabbitMQ", "ActiveMQ", "OpenSearch"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "K8s",
        "Terraform", "CI/CD", "Jenkins", "GitHub Actions", "GitLab CI", "Linux", "Git", "SQS", "MSK",
        "CloudWatch", "Lambda", "S3", "ECS", "EKS", "Prometheus", "Grafana", "Kibana", "VictoriaLogs"
    ],
    "Core Concepts & Architecture": [
        "Distributed Systems", "Microservices", "System Design", "Scalability", "Data Modeling",
        "Message Queues", "Object-Oriented Programming", "OOP", "Functional Programming", "FP",
        "Event-Driven Architecture", "Multi-threading", "Concurrency", "High Availability",
        "Fault Tolerance", "Performance Tuning", "AI Agents", "LLMs", "Generative AI", "RAG"
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
            # Try PyMuPDF first for cleanest layout
            if fitz is not None:
                try:
                    doc = fitz.open(file_path)
                    text = "\n".join([page.get_text() for page in doc])
                    if text.strip():
                        return text
                except Exception:
                    pass

            # Fallback to pypdf
            if pypdf is not None:
                reader = pypdf.PdfReader(file_path)
                return "\n".join([page.extract_text() or "" for page in reader.pages])

            raise RuntimeError("Neither PyMuPDF nor pypdf is available to read PDF.")

        # Text / Markdown files
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
    def parse(cls, file_path: str) -> Dict[str, Any]:
        """Full parsing pipeline on a resume file."""
        raw_text = cls.extract_text(file_path)
        extracted_links = cls.extract_links(file_path)

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        # 1. Candidate Name
        name = "Candidate"
        if lines:
            first_line = lines[0]
            # Check if first line looks like a name (2-4 words, alphabetic)
            cleaned = re.sub(r'[^a-zA-Z\s]', '', first_line).strip()
            if 2 <= len(cleaned.split()) <= 4 and len(cleaned) < 50:
                name = cleaned

        # 2. Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
        email = extracted_links.get("email") or (email_match.group(0) if email_match else "")

        # 3. Phone (India + international patterns)
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

        # 5. Skills Extraction
        skills_detected = []
        skills_by_category = {}

        raw_lower = raw_text.lower()
        for category, skills in SKILL_TAXONOMY.items():
            matched_in_cat = []
            for skill in skills:
                # Use word boundary search
                pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill.lower()) + r'(?![a-zA-Z0-9])'
                if re.search(pattern, raw_lower):
                    matched_in_cat.append(skill)
                    if skill not in skills_detected:
                        skills_detected.append(skill)
            if matched_in_cat:
                skills_by_category[category] = matched_in_cat

        # 6. Experience & YoE Estimation
        # Check explicit mentions: "4+ years", "4 years", "5 yrs"
        yoe_match = re.search(r'(\d+)\+?\s*(?:years|yrs)\s*(?:of\s*)?(?:experience|exp|backend|software)?', raw_lower)
        estimated_yoe = float(yoe_match.group(1)) if yoe_match else 0.0

        # Also search date ranges e.g. "Dec 2022 - Present", "Aug 2018 - May 2022"
        date_ranges = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})\s*[\u2013\u2014\-to]+\s*(?:Present|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4}))', raw_text, re.IGNORECASE)
        if not estimated_yoe and date_ranges:
            current_year = datetime.now().year
            total_months = 0
            for start_yr, end_yr in date_ranges:
                s = int(start_yr)
                e = int(end_yr) if end_yr else current_year
                if e >= s and (current_year - s) < 20: # Sanity check
                    total_months += (e - s) * 12
            if total_months > 0:
                estimated_yoe = round(total_months / 12.0, 1)

        # Default fallback if not found
        if estimated_yoe == 0:
            estimated_yoe = 3.0

        # Determine Seniority
        if estimated_yoe >= 5:
            seniority = "Senior Engineer / Tech Lead"
        elif estimated_yoe >= 2:
            seniority = "Mid-Level Engineer (SDE-2)"
        else:
            seniority = "Associate / Junior Engineer (SDE-1)"

        # 7. Current or Recent Company
        companies = []
        for line in lines:
            line_clean = line.strip()
            if any(term in line_clean.lower() for term in ["present", "software engineer", "developer", "architect"]) and "|" in line_clean:
                parts = line_clean.split("|")
                comp = parts[0].strip()
                if 2 <= len(comp) <= 40 and not any(h in comp.lower() for h in ["summary", "skills", "experience", "education"]):
                    companies.append(comp)

        current_company = companies[0] if companies else "Software Company"

        # 8. Summary snippet
        summary = ""
        summary_idx = -1
        for i, line in enumerate(lines):
            if line.lower() in ["summary", "professional summary", "about"]:
                summary_idx = i
                break
        if summary_idx != -1 and summary_idx + 1 < len(lines):
            summary = " ".join(lines[summary_idx + 1: summary_idx + 4])
        else:
            # Fallback to first descriptive paragraph
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
            "estimated_yoe": estimated_yoe,
            "seniority_level": seniority,
            "current_company": current_company,
            "raw_text": raw_text
        }
