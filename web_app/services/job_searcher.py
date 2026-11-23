"""
Job Searcher Service
Fetches software engineering job postings across Indian Tech Hubs (Bangalore, Hyderabad, Pune, NCR, Remote India)
and Global Remote companies using live API feeds, curated postings, and portal query generators.
"""

import os
import json
import urllib.parse
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Any, Optional

# Curated active openings at top Indian Product companies & GCCs
CURATED_INDIA_TECH_JOBS = [
    {
        "id": "ind-razorpay-sde2-be",
        "title": "Software Development Engineer II (Backend)",
        "company": "Razorpay",
        "location": "Bangalore, India / Hybrid",
        "region": "India",
        "salary_range": "28 - 40 LPA",
        "employment_type": "Full-time",
        "posted_date": "2 days ago",
        "description": "We are looking for an SDE-2 Backend Engineer to join our Payments Platform team. You will design and scale high-throughput payment microservices processing millions of daily transactions. Experience with Java or Go, Kafka, Distributed Systems, MySQL/PostgreSQL, Redis, and AWS is required. You will own end-to-end design, latency optimization, and reliability.",
        "skills_required": ["Java", "Go", "Kafka", "Microservices", "Distributed Systems", "AWS", "MySQL", "Redis", "REST APIs"],
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
        "salary_range": "32 - 45 LPA",
        "employment_type": "Full-time",
        "posted_date": "1 day ago",
        "description": "PhonePe is looking for a Backend Engineer to work on our core transactional engine and notifications backbone. The role involves designing fault-tolerant, horizontally scalable distributed systems handling billions of monthly UPI events. Requirements: Java/C++, Kafka/Pulsar, RocksDB, Aerospike, Docker, Kubernetes, Linux internals, and high concurrency.",
        "skills_required": ["Java", "C++", "Distributed Systems", "Kafka", "Docker", "Kubernetes", "Scalability", "Linux", "Microservices"],
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
        "salary_range": "30 - 42 LPA",
        "employment_type": "Full-time",
        "posted_date": "3 days ago",
        "description": "Swiggy is hiring SDE-2 for its core delivery allocation engine. You will build event-driven architectures with Kafka and AWS, optimizing routing algorithms, notification dispatch, and real-time state machines. Strong experience with Java, Spring Boot, AWS (SQS, Lambda), PostgreSQL, and Microservices required.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "AWS", "SQS", "Lambda", "PostgreSQL", "Microservices", "System Design"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://careers.swiggy.com/",
        "apply_url": "https://careers.swiggy.com/#/jobs",
        "source": "Swiggy Careers"
    },
    {
        "id": "ind-cred-be-eng",
        "title": "Backend Developer - Core Platforms",
        "company": "CRED",
        "location": "Bangalore, India",
        "region": "India",
        "salary_range": "35 - 50 LPA",
        "employment_type": "Full-time",
        "posted_date": "4 days ago",
        "description": "CRED is looking for high-ownership Backend Engineers. You will work on financial transaction ledgers, gamification engines, and internal microservices platforms. Tech stack: Go, Java, PostgreSQL, Kafka, AWS, Docker, Kubernetes, Event-Driven Architecture.",
        "skills_required": ["Go", "Java", "PostgreSQL", "Kafka", "AWS", "Docker", "Kubernetes", "Distributed Systems", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://cred.club/careers",
        "apply_url": "https://cred.club/careers",
        "source": "CRED Careers"
    },
    {
        "id": "ind-walmart-sde3-be",
        "title": "Senior Software Engineer / SDE-3 (Backend)",
        "company": "Walmart Global Tech India",
        "location": "Bangalore / Chennai, India",
        "region": "India",
        "salary_range": "32 - 48 LPA",
        "employment_type": "Full-time",
        "posted_date": "Just now",
        "description": "Walmart Global Tech is hiring Backend Engineers to build high-scale retail platform services. You will design, build, and deploy multi-cloud microservices handling peak millions of queries per second. Must have experience with Java, Spring Boot, Kafka, Kubernetes, Azure/GCP, and NoSQL databases.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Kubernetes", "Microservices", "Distributed Systems", "System Design", "Cloud"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://careers.walmart.com/global-tech",
        "apply_url": "https://careers.walmart.com/",
        "source": "Walmart Tech Careers"
    },
    {
        "id": "ind-cisco-se-cloud",
        "title": "Software Engineer - Cloud & Infrastructure Services",
        "company": "Cisco Systems",
        "location": "Bangalore, India",
        "region": "India",
        "salary_range": "24 - 36 LPA",
        "employment_type": "Full-time",
        "posted_date": "2 days ago",
        "description": "Join Cisco's Cloud Networking group. Work on cloud-native security, microservices orchestration, and telemetry monitoring pipelines. Strong background in Java, Python, Go, Docker, Kubernetes, Prometheus/Grafana, and AWS or GCP required.",
        "skills_required": ["Java", "Python", "Go", "Docker", "Kubernetes", "AWS", "CI/CD", "Prometheus", "Grafana", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://jobs.cisco.com/",
        "apply_url": "https://jobs.cisco.com/jobs/SearchJobs",
        "source": "Cisco Careers"
    },
    {
        "id": "ind-zepto-be-lead",
        "title": "SDE-2 / Senior Backend Engineer",
        "company": "Zepto",
        "location": "Bangalore / Mumbai, India",
        "region": "India",
        "salary_range": "30 - 45 LPA",
        "employment_type": "Full-time",
        "posted_date": "3 days ago",
        "description": "Zepto is expanding its 10-minute delivery dispatch and inventory backend. You will build scalable microservices, manage Kafka streams, and optimize high-throughput database queries. Java/Go, PostgreSQL, Redis, Kafka, AWS, Docker.",
        "skills_required": ["Java", "Go", "PostgreSQL", "Redis", "Kafka", "AWS", "Microservices", "System Design"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.zeptonow.com/careers",
        "apply_url": "https://www.zeptonow.com/careers",
        "source": "Zepto Careers"
    },
    {
        "id": "ind-inmobi-sde2-data",
        "title": "Software Development Engineer II (AdTech & Backend)",
        "company": "InMobi",
        "location": "Bangalore, India",
        "region": "India",
        "salary_range": "26 - 38 LPA",
        "employment_type": "Full-time",
        "posted_date": "5 days ago",
        "description": "InMobi powers ad-serving platforms at sub-millisecond latencies. Seeking SDE-2 with deep experience in Java/C++, distributed caching, event streaming with Kafka, and low-latency API architecture.",
        "skills_required": ["Java", "C++", "Kafka", "Distributed Systems", "MySQL", "Scalability", "Microservices", "AWS"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.inmobi.com/company/careers",
        "apply_url": "https://www.inmobi.com/company/careers",
        "source": "InMobi Careers"
    },
    {
        "id": "ind-postman-be-eng",
        "title": "Software Engineer II - Platform & Developer Tooling",
        "company": "Postman",
        "location": "Bangalore, India / Remote",
        "region": "India",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_date": "4 days ago",
        "description": "Postman is looking for a Backend / Systems Engineer to build developer tooling, API runtime engines, and collaborative cloud workspaces. Tech stack: Node.js/TypeScript, Go, React, AWS, Docker, Kubernetes, PostgreSQL.",
        "skills_required": ["Node.js", "TypeScript", "Go", "AWS", "Docker", "PostgreSQL", "REST APIs", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.postman.com/careers/",
        "apply_url": "https://www.postman.com/careers/",
        "source": "Postman Careers"
    },
    {
        "id": "ind-jpmorgan-swe-gcc",
        "title": "Software Engineer - Corporate Technology (Vice President / Associate)",
        "company": "JPMorgan Chase & Co.",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "salary_range": "26 - 40 LPA",
        "employment_type": "Full-time",
        "posted_date": "1 day ago",
        "description": "Join JPMorgan Chase Global Capability Center. You will build mission-critical banking platforms, automated clearing workflows, and microservices on AWS/Private Cloud. Core requirements: Core Java, Spring Boot, Microservices, Oracle/PostgreSQL, Kafka, CI/CD Jenkins.",
        "skills_required": ["Java", "Spring Boot", "Microservices", "Kafka", "PostgreSQL", "AWS", "CI/CD", "Jenkins", "System Design"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://careers.jpmorgan.com/",
        "apply_url": "https://careers.jpmorgan.com/",
        "source": "JPMorgan Careers"
    }
]

# Curated active global remote openings
CURATED_GLOBAL_REMOTE_JOBS = [
    {
        "id": "glob-canonical-be-eng",
        "title": "Software Engineer - Cloud & Distributed Systems",
        "company": "Canonical",
        "location": "Remote (Worldwide / India Eligible)",
        "region": "Global Remote",
        "salary_range": "$75,000 - $110,000 USD",
        "employment_type": "Full-time Remote",
        "posted_date": "2 days ago",
        "description": "Canonical is the publisher of Ubuntu. We are seeking a distributed systems backend engineer to work on open-source cloud infrastructure, Juju, and Kubernetes automation. Must be proficient in Go or Python/C++, with Linux system programming and cloud architecture experience.",
        "skills_required": ["Go", "Python", "C++", "Linux", "Kubernetes", "Docker", "Distributed Systems", "Git"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://canonical.com/careers",
        "apply_url": "https://canonical.com/careers",
        "source": "Canonical Remote"
    },
    {
        "id": "glob-gitlab-be-dev",
        "title": "Backend Engineer - CI/CD Platform",
        "company": "GitLab",
        "location": "Remote (Worldwide / All Timezones)",
        "region": "Global Remote",
        "salary_range": "$90,000 - $135,000 USD",
        "employment_type": "Full-time Remote",
        "posted_date": "3 days ago",
        "description": "GitLab is an all-remote organization. As a Backend Engineer on CI/CD, you will build scalable job scheduling, queue dispatchers, and pipeline execution engines. Tech: Ruby/Go, PostgreSQL, Redis, Kubernetes, Kafka/sidekiq, Distributed Systems.",
        "skills_required": ["Go", "Ruby", "PostgreSQL", "Redis", "Kubernetes", "CI/CD", "Git", "Distributed Systems"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://about.gitlab.com/jobs/",
        "apply_url": "https://about.gitlab.com/jobs/",
        "source": "GitLab Remote"
    },
    {
        "id": "glob-automattic-dev",
        "title": "Code Wrangler (Backend Systems Engineer)",
        "company": "Automattic (WordPress.com)",
        "location": "Remote (Global / Work from Anywhere)",
        "region": "Global Remote",
        "salary_range": "$80,000 - $120,000 USD",
        "employment_type": "Full-time Remote",
        "posted_date": "5 days ago",
        "description": "Automattic is a fully distributed company. You will work on web-scale backend infrastructure serving 1+ billion monthly users. We value self-driven engineers with solid experience in MySQL, PHP/Go/Java, message queues, and high availability systems.",
        "skills_required": ["Go", "Java", "MySQL", "Distributed Systems", "Docker", "REST APIs", "Scalability"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://automattic.com/work-with-us/",
        "apply_url": "https://automattic.com/work-with-us/",
        "source": "Automattic Careers"
    },
    {
        "id": "glob-kraken-swe-be",
        "title": "Backend Software Engineer - Payments & Ledgers",
        "company": "Kraken",
        "location": "Remote (Worldwide / Global)",
        "region": "Global Remote",
        "salary_range": "$95,000 - $140,000 USD",
        "employment_type": "Full-time Remote",
        "posted_date": "1 day ago",
        "description": "Kraken is looking for backend engineers to work on our high-performance trading engine and payment gateways. You will design fault-tolerant ledgers, handle high-volume event streams, and build microservices with C++, Rust, or Go.",
        "skills_required": ["Rust", "Go", "C++", "Distributed Systems", "Kafka", "PostgreSQL", "Docker", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.kraken.com/careers",
        "apply_url": "https://www.kraken.com/careers",
        "source": "Kraken Remote"
    }
]


class JobSearcher:
    @staticmethod
    def fetch_live_remote_jobs(query: str = "backend", limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch live remote developer jobs from open public APIs."""
        jobs = []

        # 1. Try Remotive API
        try:
            url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={urllib.parse.quote(query)}&limit={limit}"
            resp = requests.get(url, timeout=5, headers={"User-Agent": "AIJobSearch/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("jobs", [])[:limit]:
                    jobs.append({
                        "id": f"remotive-{item.get('id')}",
                        "title": item.get("title", "Software Engineer"),
                        "company": item.get("company_name", "Global Tech Company"),
                        "location": item.get("candidate_required_location", "Remote (Worldwide)"),
                        "region": "Global Remote",
                        "salary_range": item.get("salary", "Competitive"),
                        "employment_type": item.get("job_type", "Full-time Remote"),
                        "posted_date": item.get("publication_date", "")[:10] or "Recent",
                        "description": item.get("description", "")[:600],
                        "skills_required": item.get("tags", []),
                        "min_yoe": 3,
                        "max_yoe": 6,
                        "url": item.get("url", "https://remotive.com"),
                        "apply_url": item.get("url", "https://remotive.com"),
                        "source": "Remotive API"
                    })
        except Exception:
            pass

        # 2. Try Arbeitnow API if we need more
        if len(jobs) < limit:
            try:
                url = f"https://www.arbeitnow.com/api/job-board-api?search={urllib.parse.quote(query)}"
                resp = requests.get(url, timeout=5, headers={"User-Agent": "AIJobSearch/1.0"})
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("data", [])[:limit - len(jobs)]:
                        is_remote = item.get("remote", False)
                        jobs.append({
                            "id": f"arbeitnow-{item.get('slug', item.get('title'))}",
                            "title": item.get("title", "Backend Developer"),
                            "company": item.get("company_name", "Tech Startup"),
                            "location": "Remote" if is_remote else item.get("location", "Global"),
                            "region": "Global Remote",
                            "salary_range": "Market Rate",
                            "employment_type": "Full-time",
                            "posted_date": "Recent",
                            "description": item.get("description", "")[:600],
                            "skills_required": item.get("tags", []),
                            "min_yoe": 2,
                            "max_yoe": 5,
                            "url": item.get("url", ""),
                            "apply_url": item.get("url", ""),
                            "source": "Arbeitnow API"
                        })
            except Exception:
                pass

        return jobs

    @classmethod
    def search(cls,
               candidate_skills: Optional[List[str]] = None,
               region_filter: str = "All",  # "All", "India", "Global Remote"
               role_query: str = "Backend",
               limit: int = 25) -> List[Dict[str, Any]]:
        """
        Aggregate postings matching candidate profile and region preferences.
        """
        all_jobs = []

        # 1. Add Indian Tech Jobs
        if region_filter in ["All", "India"]:
            all_jobs.extend(CURATED_INDIA_TECH_JOBS)

        # 2. Add Curated Global Remote Jobs
        if region_filter in ["All", "Global Remote"]:
            all_jobs.extend(CURATED_GLOBAL_REMOTE_JOBS)

        # 3. Add live remote API jobs
        if region_filter in ["All", "Global Remote"]:
            live_jobs = cls.fetch_live_remote_jobs(query=role_query, limit=10)
            all_jobs.extend(live_jobs)

        # Filter by keyword if provided
        filtered = []
        q_lower = role_query.lower()
        for j in all_jobs:
            text_corpus = f"{j['title']} {j['company']} {j['description']} {' '.join(j.get('skills_required', []))}".lower()
            if not q_lower or q_lower in text_corpus or "engineer" in text_corpus or "developer" in text_corpus:
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
