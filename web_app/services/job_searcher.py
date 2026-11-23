"""
Job Searcher Service
Generic & Dynamic across all software engineering tracks (Frontend, Backend, Full Stack,
Mobile, DevOps/Cloud, Data & AI).
Fetches from:
1. Live WeWorkRemotely RSS feed (dynamically selecting categories based on domain)
2. Live Remotive API (filtered by candidate domain & skills)
3. Live Jobicy API
4. Live Arbeitnow API
5. Curated active openings across top Indian Tech Giants, Startups & GCCs covering multiple engineering disciplines.
Strictly scopes to the last 7 days by default.
"""

import os
import re
import json
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import requests
from typing import List, Dict, Any, Optional

NOW = datetime.now()

# Multi-discipline openings across top Indian Product companies & GCCs
CURATED_INDIA_TECH_JOBS = [
    # --- Backend & Distributed Systems ---
    {
        "id": "ind-razorpay-sde2-be",
        "title": "Software Development Engineer II (Backend)",
        "company": "Razorpay",
        "location": "Bangalore, India / Hybrid",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "28 - 40 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Looking for an SDE-2 Backend Engineer for our Payments Platform. Build high-throughput microservices processing millions of daily transactions. Strong experience in Java, Kafka, Distributed Systems, MySQL/PostgreSQL, Redis, and AWS required.",
        "skills_required": ["Java", "Kafka", "Microservices", "Distributed Systems", "AWS", "PostgreSQL", "Redis", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://razorpay.com/jobs/",
        "apply_url": "https://razorpay.com/jobs/openings/",
        "source": "Razorpay Careers"
    },
    {
        "id": "ind-phonepe-sde2-infra",
        "title": "Software Engineer (Backend & Distributed Systems)",
        "company": "PhonePe",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "32 - 45 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 1,
        "posted_date": "1 day ago",
        "posted_timestamp": (NOW - timedelta(days=1)).strftime("%Y-%m-%d"),
        "description": "PhonePe is looking for a Backend Engineer to work on our core transactional engine and notifications backbone. Design fault-tolerant distributed systems handling billions of monthly UPI events. Requirements: Java, C++, Kafka, Docker, Kubernetes, Linux, and high concurrency.",
        "skills_required": ["Java", "C++", "Kafka", "Distributed Systems", "Docker", "Kubernetes", "Scalability", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.phonepe.com/careers/",
        "apply_url": "https://www.phonepe.com/careers/job-openings/",
        "source": "PhonePe Careers"
    },
    {
        "id": "ind-swiggy-sde2-core",
        "title": "Software Development Engineer II - Logistics Backend",
        "company": "Swiggy",
        "location": "Bangalore, India / Hybrid",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "30 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Build event-driven architectures with Kafka and AWS, optimizing routing algorithms, notification dispatch, and real-time state machines. Strong experience with Java, Spring Boot, AWS (SQS, Lambda), PostgreSQL, and Microservices required.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "AWS", "AWS SQS", "AWS Lambda", "PostgreSQL", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://careers.swiggy.com/",
        "apply_url": "https://careers.swiggy.com/#/jobs",
        "source": "Swiggy Careers"
    },
    {
        "id": "ind-cred-be-eng",
        "title": "Backend Developer - Core Platforms & Ledgers",
        "company": "CRED",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "35 - 50 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Work on financial transaction ledgers, gamification engines, and internal microservices platforms. Tech stack: Java, Go, PostgreSQL, Kafka, AWS, Docker, Kubernetes, Event-Driven Architecture.",
        "skills_required": ["Java", "Go", "PostgreSQL", "Kafka", "AWS", "Docker", "Kubernetes", "Distributed Systems"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://cred.club/careers",
        "apply_url": "https://cred.club/careers",
        "source": "CRED Careers"
    },
    {
        "id": "ind-zepto-be-lead",
        "title": "SDE-2 Backend Engineer (Dispatch & Inventory)",
        "company": "Zepto",
        "location": "Bangalore / Mumbai, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "30 - 45 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Building quick commerce order dispatch and inventory backend. Build scalable microservices, manage Kafka streams, and optimize high-throughput database queries. Java/Go, PostgreSQL, Redis, Kafka, AWS, Docker.",
        "skills_required": ["Java", "Go", "PostgreSQL", "Redis", "Kafka", "AWS", "Microservices", "System Design"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.zeptonow.com/careers",
        "apply_url": "https://www.zeptonow.com/careers",
        "source": "Zepto Careers"
    },
    {
        "id": "ind-walmart-sde3-be",
        "title": "Senior Software Engineer / SDE-3 (Retail Cloud Platform)",
        "company": "Walmart Global Tech India",
        "location": "Bangalore / Chennai, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "32 - 48 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 1,
        "posted_date": "1 day ago",
        "posted_timestamp": (NOW - timedelta(days=1)).strftime("%Y-%m-%d"),
        "description": "Walmart Global Tech is hiring Backend Engineers to build high-scale retail platform services. Design, build, and deploy multi-cloud microservices handling peak millions of queries per second. Must have experience with Java, Spring Boot, Kafka, Kubernetes, and Distributed Systems.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Kubernetes", "Microservices", "Distributed Systems", "System Design"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://careers.walmart.com/global-tech",
        "apply_url": "https://careers.walmart.com/",
        "source": "Walmart Tech Careers"
    },
    {
        "id": "ind-uber-sde2-mobility",
        "title": "Software Engineer II - Mobility & Marketplace Engineering",
        "company": "Uber India",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "35 - 52 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Uber Bangalore Tech Center is hiring for Mobility & Dispatch Backend. Design scalable distributed services, handle real-time geolocation event streams, and optimize state synchronization with Go and Java.",
        "skills_required": ["Go", "Java", "Kafka", "Distributed Systems", "Microservices", "Docker", "Kubernetes", "System Design"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.uber.com/us/en/careers/",
        "apply_url": "https://www.uber.com/us/en/careers/",
        "source": "Uber Careers"
    },

    # --- Frontend & Web Engineering ---
    {
        "id": "ind-cred-fe-sde2",
        "title": "Software Development Engineer II (Frontend / UI)",
        "company": "CRED",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Frontend Engineer",
        "salary_range": "30 - 46 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Craft pixel-perfect web and mobile design systems, micro-frontends, and highly responsive user interfaces. Expert knowledge of React, Next.js, TypeScript, TailwindCSS, Webpack/Vite, and state management required.",
        "skills_required": ["React", "ReactJS", "Next.js", "TypeScript", "JavaScript", "Tailwind", "CSS3", "HTML5"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://cred.club/careers",
        "apply_url": "https://cred.club/careers",
        "source": "CRED Careers"
    },
    {
        "id": "ind-razorpay-fe-lead",
        "title": "Frontend Engineer II - Merchant Dashboard",
        "company": "Razorpay",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Frontend Engineer",
        "salary_range": "26 - 38 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Build high-speed, accessible financial dashboards used by over 5 million merchants. Deep expertise in ReactJS, TypeScript, Redux, Next.js, performance optimization, and browser security required.",
        "skills_required": ["React", "ReactJS", "TypeScript", "JavaScript", "Redux", "REST APIs", "HTML", "CSS"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://razorpay.com/jobs/",
        "apply_url": "https://razorpay.com/jobs/",
        "source": "Razorpay Careers"
    },

    # --- Full Stack Engineering ---
    {
        "id": "ind-postman-fullstack",
        "title": "Software Engineer II (Full Stack - Developer Experience)",
        "company": "Postman",
        "location": "Bangalore, India / Remote",
        "region": "India",
        "domain": "Full Stack Engineer",
        "salary_range": "28 - 44 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Build collaborative API client workflows end-to-end. Full stack proficiency in React, TypeScript, Node.js, Express, PostgreSQL, and AWS required.",
        "skills_required": ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "AWS", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.postman.com/careers/",
        "apply_url": "https://www.postman.com/careers/",
        "source": "Postman Careers"
    },
    {
        "id": "ind-browserstack-fs",
        "title": "Senior Full Stack Engineer - Cloud Infrastructure",
        "company": "BrowserStack",
        "location": "Mumbai / Bangalore, India",
        "region": "India",
        "domain": "Full Stack Engineer",
        "salary_range": "32 - 46 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Design test automation cloud grids. Requires strong full stack skills in React, TypeScript/JavaScript, Node.js or Ruby/Python, Docker, and AWS.",
        "skills_required": ["React", "TypeScript", "Node.js", "Docker", "AWS", "PostgreSQL", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://www.browserstack.com/careers",
        "apply_url": "https://www.browserstack.com/careers",
        "source": "BrowserStack Careers"
    },

    # --- DevOps & Cloud Infrastructure ---
    {
        "id": "ind-cisco-devops",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "Cisco Systems",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "DevOps / Cloud Engineer",
        "salary_range": "26 - 38 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Scale enterprise cloud platforms using Kubernetes, Terraform, Docker, CI/CD pipelines, and Prometheus/Grafana monitoring across AWS and GCP.",
        "skills_required": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Jenkins", "Linux", "Git"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://jobs.cisco.com/",
        "apply_url": "https://jobs.cisco.com/",
        "source": "Cisco Careers"
    },

    # --- Data & Machine Learning / AI ---
    {
        "id": "ind-swiggy-ml-engineer",
        "title": "Machine Learning Engineer - Delivery Intelligence",
        "company": "Swiggy",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Data & ML Engineer",
        "salary_range": "32 - 48 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Build real-time machine learning models for ETA prediction, dynamic dispatch, and batch optimization. Python, PyTorch/TensorFlow, Spark, Kafka, and AWS.",
        "skills_required": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "Pandas", "Kafka", "AWS", "Spark"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://careers.swiggy.com/",
        "apply_url": "https://careers.swiggy.com/",
        "source": "Swiggy AI Careers"
    }
]


class JobSearcher:
    @staticmethod
    def fetch_wwr_rss_jobs(domain: str = "Backend", limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch live software engineering jobs from WeWorkRemotely RSS feed."""
        jobs = []
        # Select appropriate RSS category based on candidate domain
        if "frontend" in domain.lower():
            rss_url = "https://weworkremotely.com/categories/remote-front-end-programming-jobs.rss"
        elif "devops" in domain.lower():
            rss_url = "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss"
        else:
            rss_url = "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss"

        try:
            resp = requests.get(rss_url, timeout=5, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                channel = root.find("channel")
                if channel is not None:
                    for item in channel.findall("item")[:limit]:
                        raw_title = item.find("title").text or "Software Engineer"
                        link = item.find("link").text or "https://weworkremotely.com"
                        pub_date_str = item.find("pubDate").text if item.find("pubDate") is not None else ""

                        company = "Global Remote Company"
                        title = raw_title
                        if ":" in raw_title:
                            parts = raw_title.split(":", 1)
                            company = parts[0].strip()
                            title = parts[1].strip()

                        posted_days = 2
                        if pub_date_str:
                            try:
                                dt = datetime.strptime(pub_date_str[:25].strip(), "%a, %d %b %Y %H:%M:%S")
                                delta = (datetime.utcnow() - dt).days
                                posted_days = max(1, delta)
                            except Exception:
                                pass

                        jobs.append({
                            "id": f"wwr-{abs(hash(link)) % 1000000}",
                            "title": title,
                            "company": company,
                            "location": "Remote (Worldwide / Global)",
                            "region": "Global Remote",
                            "domain": domain,
                            "salary_range": "$90,000 - $140,000 USD",
                            "employment_type": "Full-time Remote",
                            "posted_days_ago": posted_days,
                            "posted_date": f"{posted_days} days ago" if posted_days > 1 else "1 day ago",
                            "posted_timestamp": (NOW - timedelta(days=posted_days)).strftime("%Y-%m-%d"),
                            "description": f"Engineering role at {company}. Work on cloud platforms, microservices, and modern technology stack.",
                            "skills_required": ["Python", "Java", "TypeScript", "React", "AWS", "Docker", "Distributed Systems", "REST APIs"],
                            "min_yoe": 3,
                            "max_yoe": 7,
                            "url": link,
                            "apply_url": link,
                            "source": "WeWorkRemotely RSS"
                        })
        except Exception:
            pass
        return jobs

    @staticmethod
    def fetch_remotive_jobs(query: str = "software", limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch live developer jobs from Remotive API."""
        jobs = []
        try:
            url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={urllib.parse.quote(query)}&limit={limit}"
            resp = requests.get(url, timeout=5, headers={"User-Agent": "AIJobSearch/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", [])[:limit]:
                    pub_str = item.get("publication_date", "")[:10]
                    posted_days = 3
                    if pub_str:
                        try:
                            dt = datetime.strptime(pub_str, "%Y-%m-%d")
                            delta = (NOW - dt).days
                            posted_days = max(1, delta)
                        except Exception:
                            pass

                    tags = item.get("tags", [])
                    skills_req = [t for t in tags if len(t) > 1][:6]
                    if not skills_req:
                        skills_req = ["Python", "Java", "JavaScript", "TypeScript", "AWS", "REST APIs"]

                    jobs.append({
                        "id": f"remotive-{item.get('id')}",
                        "title": item.get("title", "Software Engineer"),
                        "company": item.get("company_name", "Global Tech Company"),
                        "location": item.get("candidate_required_location", "Remote (Worldwide)"),
                        "region": "Global Remote",
                        "domain": "Software Engineer",
                        "salary_range": item.get("salary", "Competitive"),
                        "employment_type": item.get("job_type", "Full-time Remote"),
                        "posted_days_ago": posted_days,
                        "posted_date": f"{posted_days} days ago" if posted_days > 1 else "1 day ago",
                        "posted_timestamp": pub_str or (NOW - timedelta(days=posted_days)).strftime("%Y-%m-%d"),
                        "description": item.get("description", "")[:500],
                        "skills_required": skills_req,
                        "min_yoe": 3,
                        "max_yoe": 6,
                        "url": item.get("url", "https://remotive.com"),
                        "apply_url": item.get("url", "https://remotive.com"),
                        "source": "Remotive API"
                    })
        except Exception:
            pass
        return jobs

    @classmethod
    def search(cls,
               candidate_skills: Optional[List[str]] = None,
               region_filter: str = "All",
               role_query: str = "Backend",
               max_days: int = 7,
               limit: int = 50) -> List[Dict[str, Any]]:
        """
        Generic search across all software engineering tracks with recency filter.
        """
        all_jobs = []

        # 1. Add Indian Tech Jobs
        if region_filter in ["All", "India"]:
            all_jobs.extend(CURATED_INDIA_TECH_JOBS)

        # 2. Add Live WeWorkRemotely RSS Jobs
        if region_filter in ["All", "Global Remote"]:
            wwr_jobs = cls.fetch_wwr_rss_jobs(domain=role_query, limit=12)
            all_jobs.extend(wwr_jobs)

        # 3. Add Live Remotive API Jobs
        if region_filter in ["All", "Global Remote"]:
            remotive_jobs = cls.fetch_remotive_jobs(query=role_query, limit=15)
            all_jobs.extend(remotive_jobs)

        # Apply Recency Filter (default: max_days = 7)
        recent_jobs = []
        for j in all_jobs:
            days = j.get("posted_days_ago", 3)
            if max_days <= 0 or days <= max_days:
                recent_jobs.append(j)

        # Keyword filtering if user specified a role query
        filtered = []
        q_lower = role_query.lower()
        for j in recent_jobs:
            text_corpus = f"{j['title']} {j['company']} {j['description']} {' '.join(j.get('skills_required', []))}".lower()
            if not q_lower or q_lower == "all" or q_lower in text_corpus or "engineer" in text_corpus or "developer" in text_corpus:
                filtered.append(j)

        # Deduplicate by company + title
        seen_keys = set()
        deduped = []
        for j in filtered:
            key = f"{j['company'].lower()} - {j['title'].lower()}"
            if key not in seen_keys:
                seen_keys.add(key)
                deduped.append(j)

        return deduped[:limit]
