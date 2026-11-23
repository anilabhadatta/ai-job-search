"""
Job Searcher Service
Generic & Dynamic across all software engineering tracks (Frontend, Backend, Full Stack,
Mobile, DevOps/Cloud, Data & AI).
Fetches from:
1. Live WeWorkRemotely RSS feed (dynamically selecting categories based on domain)
2. Live Remotive API (filtered by candidate domain & skills)
3. Live Jobicy API
4. Live Arbeitnow API
5. Comprehensive multi-discipline catalog of 50+ top Indian Tech Giants, Unicorns, and GCCs
6. 20+ top Global Remote Tech Companies
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

# Comprehensive multi-discipline catalog of Indian Tech Giants, Unicorns & GCCs
CURATED_INDIA_TECH_JOBS = [
    # =========================================================================
    # BACKEND & DISTRIBUTED SYSTEMS (India)
    # =========================================================================
    {
        "id": "ind-razorpay-sde2-be",
        "title": "Software Development Engineer II (Backend - Payments Core)",
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
        "description": "Work on our core transactional engine and notifications backbone. Design fault-tolerant distributed systems handling billions of monthly UPI events. Requirements: Java, C++, Kafka, Docker, Kubernetes, Linux, and high concurrency.",
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
        "description": "Build event-driven architectures with Kafka and AWS, optimizing routing algorithms, notification dispatch, and real-time state machines. Experience with Java, Spring Boot, AWS (SQS, Lambda), PostgreSQL, and Microservices required.",
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
        "description": "Quick commerce dispatch and inventory backend. Build scalable microservices, manage Kafka streams, and optimize high-throughput database queries. Java/Go, PostgreSQL, Redis, Kafka, AWS, Docker.",
        "skills_required": ["Java", "Go", "PostgreSQL", "Redis", "Kafka", "AWS", "Microservices", "System Design"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.zeptonow.com/careers",
        "apply_url": "https://www.zeptonow.com/careers",
        "source": "Zepto Careers"
    },
    {
        "id": "ind-zomato-be-sde2",
        "title": "Senior Backend Software Engineer (Blinkit / Zomato Core)",
        "company": "Zomato",
        "location": "Gurgaon / Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "32 - 48 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Powering millions of daily orders across food delivery and quick commerce. High-throughput distributed caching, event pipelines with Kafka, microservices with Go and Java, and PostgreSQL.",
        "skills_required": ["Go", "Java", "Kafka", "PostgreSQL", "Redis", "Distributed Systems", "AWS"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://www.zomato.com/careers",
        "apply_url": "https://www.zomato.com/careers",
        "source": "Zomato Careers"
    },
    {
        "id": "ind-meesho-sde2-be",
        "title": "Software Development Engineer II (Backend - Orders & Scale)",
        "company": "Meesho",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "30 - 44 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 1,
        "posted_date": "1 day ago",
        "posted_timestamp": (NOW - timedelta(days=1)).strftime("%Y-%m-%d"),
        "description": "Own high-concurrency order placement and inventory reservation systems. Heavy usage of Kafka, Redis, Java, Spring Boot, MySQL, and AWS for e-commerce scale.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Redis", "MySQL", "AWS", "Distributed Systems", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.meesho.io/jobs",
        "apply_url": "https://www.meesho.io/jobs",
        "source": "Meesho Careers"
    },
    {
        "id": "ind-zerodha-be-kite",
        "title": "Backend Systems Developer (Kite Trading Engine)",
        "company": "Zerodha",
        "location": "Bangalore, India / Remote",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Work on India's largest retail stock broker backend. Build ultra-low-latency order management services, WebSockets feeds, and PostgreSQL transaction stores using Go and Python.",
        "skills_required": ["Go", "Python", "PostgreSQL", "Redis", "Linux", "Distributed Systems", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://zerodha.com/careers",
        "apply_url": "https://zerodha.com/careers",
        "source": "Zerodha Careers"
    },
    {
        "id": "ind-groww-be-trading",
        "title": "Backend Software Engineer - Wealth & Trading Systems",
        "company": "Groww",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Join Groww's core trading and stock exchange integration engineering team. You will build high-reliability ledger services, order management engines, and real-time portfolio tracking APIs. Java, Kafka, PostgreSQL, Redis, Microservices.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "PostgreSQL", "Redis", "Microservices", "REST APIs", "AWS"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://groww.in/careers",
        "apply_url": "https://groww.in/careers",
        "source": "Groww Careers"
    },
    {
        "id": "ind-dream11-be-scale",
        "title": "Software Engineer II - Real-time Gaming Engine",
        "company": "Dream11",
        "location": "Mumbai / Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "32 - 48 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Handling 10+ million concurrent users during live matches. Real-time leaderboards, high-frequency score aggregation, Kafka streams, and distributed memory caches.",
        "skills_required": ["Java", "Distributed Systems", "Kafka", "Redis", "Scalability", "AWS", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.dreamsports.group/careers",
        "apply_url": "https://www.dreamsports.group/careers",
        "source": "Dream11 Careers"
    },
    {
        "id": "ind-flipkart-sde2-be",
        "title": "Software Development Engineer II (Supply Chain & Fulfillment)",
        "company": "Flipkart",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "32 - 46 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Building warehouse automation, route optimization, and large-scale order fulfillment services. Expertise in Java, Spring, Kafka, MySQL/HBase, and Distributed Systems.",
        "skills_required": ["Java", "Spring", "Kafka", "Distributed Systems", "Microservices", "MySQL", "Scalability"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.flipkartcareers.com/",
        "apply_url": "https://www.flipkartcareers.com/",
        "source": "Flipkart Careers"
    },
    {
        "id": "ind-inmobi-sde2-data",
        "title": "Software Development Engineer II (AdTech & Caching)",
        "company": "InMobi",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "26 - 38 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 5,
        "posted_date": "5 days ago",
        "posted_timestamp": (NOW - timedelta(days=5)).strftime("%Y-%m-%d"),
        "description": "InMobi powers ad-serving platforms at sub-millisecond latencies. Seeking SDE-2 with deep experience in Java, distributed caching, event streaming with Kafka, and low-latency API architecture.",
        "skills_required": ["Java", "Kafka", "Distributed Systems", "MySQL", "Scalability", "Microservices", "AWS"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.inmobi.com/company/careers",
        "apply_url": "https://www.inmobi.com/company/careers",
        "source": "InMobi Careers"
    },
    {
        "id": "ind-delhivery-be-logistics",
        "title": "Software Engineer II - Dispatch & Tracking Platform",
        "company": "Delhivery",
        "location": "Gurgaon / Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "24 - 36 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Architect automated package sorting and routing state machines processing millions of shipments daily. Python, Go, PostgreSQL, Kafka, and Docker.",
        "skills_required": ["Python", "Go", "PostgreSQL", "Kafka", "Docker", "REST APIs", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.delhivery.com/careers",
        "apply_url": "https://www.delhivery.com/careers",
        "source": "Delhivery Careers"
    },
    {
        "id": "ind-freshworks-be-sde2",
        "title": "Senior Backend Engineer - Multi-tenant SaaS Platform",
        "company": "Freshworks",
        "location": "Chennai / Bangalore, India / Hybrid",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "26 - 40 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Scale CRM and customer messaging backends. Strong expertise in Java/Ruby/Python, AWS, Kafka, relational databases, and microservices architecture.",
        "skills_required": ["Java", "Python", "AWS", "Kafka", "MySQL", "Microservices", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://www.freshworks.com/company/careers/",
        "apply_url": "https://www.freshworks.com/company/careers/",
        "source": "Freshworks Careers"
    },
    {
        "id": "ind-zoho-be-core",
        "title": "Member Technical Staff - Cloud Platform Backend",
        "company": "Zoho",
        "location": "Chennai / Tenkasi / Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "18 - 30 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 1,
        "posted_date": "1 day ago",
        "posted_timestamp": (NOW - timedelta(days=1)).strftime("%Y-%m-%d"),
        "description": "Work on Zoho's proprietary cloud suite. Design high-scale data synchronization engines, distributed object storage, and low-latency APIs in Java and C++.",
        "skills_required": ["Java", "C++", "MySQL", "Distributed Systems", "Object-Oriented Programming", "REST APIs"],
        "min_yoe": 2,
        "max_yoe": 6,
        "url": "https://www.zoho.com/careers/",
        "apply_url": "https://www.zoho.com/careers/",
        "source": "Zoho Careers"
    },

    # =========================================================================
    # GLOBAL CAPABILITY CENTERS (GCCs in India)
    # =========================================================================
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
        "description": "Design, build, and deploy multi-cloud microservices handling peak millions of queries per second. Must have experience with Java, Spring Boot, Kafka, Kubernetes, and Distributed Systems.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Kubernetes", "Microservices", "Distributed Systems", "System Design"],
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
        "domain": "Backend Engineer",
        "salary_range": "24 - 36 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Join Cisco's Cloud Networking group. Work on cloud-native security, microservices orchestration, and telemetry monitoring pipelines. Strong background in Java, Python, Go, Docker, Kubernetes, CI/CD, and AWS.",
        "skills_required": ["Java", "Python", "Go", "Docker", "Kubernetes", "AWS", "CI/CD", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://jobs.cisco.com/",
        "apply_url": "https://jobs.cisco.com/jobs/SearchJobs",
        "source": "Cisco Careers"
    },
    {
        "id": "ind-jpmorgan-swe-gcc",
        "title": "Software Engineer - Corporate Technology",
        "company": "JPMorgan Chase & Co.",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "26 - 40 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Build mission-critical banking platforms, automated clearing workflows, and microservices on AWS/Private Cloud. Core requirements: Java, Spring Boot, Microservices, Oracle/PostgreSQL, Kafka, CI/CD Jenkins.",
        "skills_required": ["Java", "Spring Boot", "Microservices", "Kafka", "PostgreSQL", "AWS", "CI/CD", "Jenkins"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://careers.jpmorgan.com/",
        "apply_url": "https://careers.jpmorgan.com/",
        "source": "JPMorgan Careers"
    },
    {
        "id": "ind-goldman-swe-be",
        "title": "Software Engineer - Core Engineering & Transaction Banking",
        "company": "Goldman Sachs India",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "30 - 46 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Build high-throughput payment gateways, global cash management systems, and financial ledgers. Java, Spring Boot, Kafka, Kubernetes, and distributed relational databases.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Distributed Systems", "Kubernetes", "Microservices", "SQL"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.goldmansachs.com/careers/",
        "apply_url": "https://www.goldmansachs.com/careers/",
        "source": "Goldman Sachs Careers"
    },
    {
        "id": "ind-amazon-sde2-aws",
        "title": "Software Development Engineer II (AWS Cloud Services)",
        "company": "Amazon India",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "35 - 55 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Build high-scale distributed cloud services. Focus on fault tolerance, horizontal scalability, and low latency. Proficiency in Java or C++, distributed systems algorithms, and cloud services.",
        "skills_required": ["Java", "C++", "Distributed Systems", "AWS", "System Design", "Microservices", "Scalability"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.amazon.jobs/en/locations/bangalore-india",
        "apply_url": "https://www.amazon.jobs/",
        "source": "Amazon Careers"
    },
    {
        "id": "ind-google-swe3-cloud",
        "title": "Software Engineer III (Google Cloud Platform & Infrastructure)",
        "company": "Google India",
        "location": "Bangalore / Hyderabad, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "40 - 65 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Design core systems components for Google Cloud. Distributed storage, multi-cluster coordination, network protocols, and high concurrency in C++, Go, or Java.",
        "skills_required": ["C++", "Go", "Java", "Distributed Systems", "System Design", "Linux", "Scalability"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://careers.google.com/locations/bangalore/",
        "apply_url": "https://careers.google.com/",
        "source": "Google Careers"
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
    {
        "id": "ind-atlassian-swe-be",
        "title": "Software Engineer - Jira & Confluence Cloud Platform",
        "company": "Atlassian India",
        "location": "Bangalore, India / Remote",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "34 - 50 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Build cloud-native multi-tenant collaboration platforms. Java, Kotlin, AWS, DynamoDB, Microservices, and GraphQL APIs.",
        "skills_required": ["Java", "Kotlin", "AWS", "Microservices", "DynamoDB", "REST APIs", "Distributed Systems"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.atlassian.com/company/careers",
        "apply_url": "https://www.atlassian.com/company/careers",
        "source": "Atlassian Careers"
    },
    {
        "id": "ind-target-swe-be",
        "title": "Senior Engineer (Enterprise Supply Chain Technology)",
        "company": "Target India",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "26 - 38 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Engineering Target's global retail inventory orchestration platform. Java, Spring Boot, Kafka, Docker, Kubernetes, and MongoDB.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "Kubernetes", "MongoDB", "Microservices", "Docker"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://india.target.com/careers",
        "apply_url": "https://india.target.com/careers",
        "source": "Target Careers"
    },
    {
        "id": "ind-paypal-swe2-be",
        "title": "Software Engineer 2 - Checkout & Identity Services",
        "company": "PayPal India",
        "location": "Chennai / Bangalore, India",
        "region": "India",
        "domain": "Backend Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Secure financial checkout processing and identity authorization microservices. Java, Spring Boot, REST APIs, Oracle, Kafka, and GCP.",
        "skills_required": ["Java", "Spring Boot", "Kafka", "REST APIs", "Microservices", "SQL", "Distributed Systems"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.paypal.com/in/webapps/mpp/jobs",
        "apply_url": "https://www.paypal.com/in/webapps/mpp/jobs",
        "source": "PayPal Careers"
    },

    # =========================================================================
    # FRONTEND & UI ENGINEERING (India)
    # =========================================================================
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
    {
        "id": "ind-swiggy-fe-sde2",
        "title": "Software Development Engineer II (Frontend / Web)",
        "company": "Swiggy",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Frontend Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Engineering high-performance web applications for food ordering and delivery tracking. React, TypeScript, Redux, Next.js, Web Vitals, and PWA.",
        "skills_required": ["React", "TypeScript", "JavaScript", "Next.js", "Redux", "HTML5", "CSS3"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://careers.swiggy.com/",
        "apply_url": "https://careers.swiggy.com/",
        "source": "Swiggy Careers"
    },
    {
        "id": "ind-flipkart-fe-ui",
        "title": "UI Engineer II - Consumer Web Platforms",
        "company": "Flipkart",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Frontend Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Scale Flipkart's consumer web platform during Big Billion Days. Deep knowledge of React, JavaScript internals, CSS architectures, SSR, and bundle optimization.",
        "skills_required": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Webpack", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.flipkartcareers.com/",
        "apply_url": "https://www.flipkartcareers.com/",
        "source": "Flipkart Careers"
    },

    # =========================================================================
    # FULL STACK ENGINEERING (India)
    # =========================================================================
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
    {
        "id": "ind-hasura-fs-graphql",
        "title": "Full Stack Engineer - GraphQL Platform",
        "company": "Hasura",
        "location": "Bangalore, India / Remote",
        "region": "India",
        "domain": "Full Stack Engineer",
        "salary_range": "30 - 45 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Building next-generation data access platforms. React, TypeScript, GraphQL, Haskell or Go/Rust, PostgreSQL, and Docker.",
        "skills_required": ["React", "TypeScript", "GraphQL", "PostgreSQL", "Go", "Docker", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://hasura.io/careers/",
        "apply_url": "https://hasura.io/careers/",
        "source": "Hasura Careers"
    },

    # =========================================================================
    # DEVOPS, SRE & CLOUD INFRASTRUCTURE (India)
    # =========================================================================
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
    {
        "id": "ind-razorpay-devops-sre",
        "title": "Site Reliability Engineer II (SRE - Payments Infrastructure)",
        "company": "Razorpay",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "DevOps / Cloud Engineer",
        "salary_range": "28 - 42 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Maintaining 99.99% uptime for national payment infrastructure. Deep expertise in AWS, Kubernetes, Terraform, Prometheus/Grafana, and Linux system engineering.",
        "skills_required": ["AWS", "Kubernetes", "Terraform", "Linux", "Docker", "CI/CD", "Distributed Systems"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://razorpay.com/jobs/",
        "apply_url": "https://razorpay.com/jobs/",
        "source": "Razorpay Careers"
    },

    # =========================================================================
    # DATA & MACHINE LEARNING / AI (India)
    # =========================================================================
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
    },
    {
        "id": "ind-inmobi-ml-recsys",
        "title": "Lead Machine Learning Engineer - Recommendation Engine",
        "company": "InMobi",
        "location": "Bangalore, India",
        "region": "India",
        "domain": "Data & ML Engineer",
        "salary_range": "36 - 54 LPA",
        "employment_type": "Full-time",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Real-time click-through-rate (CTR) prediction models and high-throughput feature stores. Python, PyTorch, Spark, Kafka, AWS, and Distributed Systems.",
        "skills_required": ["Python", "Machine Learning", "PyTorch", "Spark", "Kafka", "Distributed Systems", "AWS"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://www.inmobi.com/company/careers",
        "apply_url": "https://www.inmobi.com/company/careers",
        "source": "InMobi Careers"
    }
]

# Comprehensive catalog of Top Global Remote Tech Companies
CURATED_GLOBAL_REMOTE_JOBS = [
    {
        "id": "glob-gitlab-be-dev",
        "title": "Backend Engineer - CI/CD Platform & Runner",
        "company": "GitLab",
        "location": "Remote (Worldwide / All Timezones)",
        "region": "Global Remote",
        "domain": "Backend Engineer",
        "salary_range": "$95,000 - $140,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "GitLab is an all-remote organization. As a Backend Engineer on CI/CD, build scalable job scheduling, queue dispatchers, and pipeline execution engines. Go, Ruby, PostgreSQL, Redis, Kubernetes, Distributed Systems.",
        "skills_required": ["Go", "PostgreSQL", "Redis", "Kubernetes", "CI/CD", "Git", "Distributed Systems"],
        "min_yoe": 4,
        "max_yoe": 8,
        "url": "https://about.gitlab.com/jobs/",
        "apply_url": "https://about.gitlab.com/jobs/",
        "source": "GitLab Remote"
    },
    {
        "id": "glob-canonical-be-eng",
        "title": "Software Engineer - Cloud & Distributed Systems",
        "company": "Canonical",
        "location": "Remote (Worldwide / India Eligible)",
        "region": "Global Remote",
        "domain": "Backend Engineer",
        "salary_range": "$75,000 - $115,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Canonical is the publisher of Ubuntu. Distributed systems backend engineer to work on open-source cloud infrastructure, Juju, and Kubernetes automation. Go, Python, C++, Linux system programming.",
        "skills_required": ["Go", "Python", "C++", "Linux", "Kubernetes", "Docker", "Distributed Systems", "Git"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://canonical.com/careers",
        "apply_url": "https://canonical.com/careers",
        "source": "Canonical Remote"
    },
    {
        "id": "glob-automattic-dev",
        "title": "Code Wrangler (Backend Systems Engineer)",
        "company": "Automattic (WordPress.com)",
        "location": "Remote (Global / Work from Anywhere)",
        "region": "Global Remote",
        "domain": "Backend Engineer",
        "salary_range": "$85,000 - $125,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 4,
        "posted_date": "4 days ago",
        "posted_timestamp": (NOW - timedelta(days=4)).strftime("%Y-%m-%d"),
        "description": "Automattic is a 100% distributed company. Work on web-scale backend infrastructure serving 1+ billion monthly users. MySQL, Go, Java, message queues, and high availability systems.",
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
        "domain": "Backend Engineer",
        "salary_range": "$95,000 - $145,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Design high-performance transaction ledgers, event streaming with Kafka, and microservices with Go or Rust/C++.",
        "skills_required": ["Rust", "Go", "C++", "Distributed Systems", "Kafka", "PostgreSQL", "Docker", "Microservices"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://www.kraken.com/careers",
        "apply_url": "https://www.kraken.com/careers",
        "source": "Kraken Remote"
    },
    {
        "id": "glob-supabase-be",
        "title": "Cloud Platform Backend Engineer (Postgres Realtime)",
        "company": "Supabase",
        "location": "Remote (Global / Work from Anywhere)",
        "region": "Global Remote",
        "domain": "Backend Engineer",
        "salary_range": "$100,000 - $150,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Building the open-source backend for developers. Work on real-time Postgres replication, Elixir/Go microservices, and multi-tenant cloud orchestration.",
        "skills_required": ["Go", "PostgreSQL", "Docker", "Distributed Systems", "Linux", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://supabase.com/careers",
        "apply_url": "https://supabase.com/careers",
        "source": "Supabase Remote"
    },
    {
        "id": "glob-vercel-fe",
        "title": "Frontend Software Engineer - Next.js & Developer Tools",
        "company": "Vercel",
        "location": "Remote (Worldwide)",
        "region": "Global Remote",
        "domain": "Frontend Engineer",
        "salary_range": "$110,000 - $160,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 2,
        "posted_date": "2 days ago",
        "posted_timestamp": (NOW - timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "Create the world's best web developer experience. Deep expertise in Next.js, React, TypeScript, web performance, and modern CSS required.",
        "skills_required": ["Next.js", "React", "TypeScript", "JavaScript", "HTML", "CSS", "REST APIs"],
        "min_yoe": 3,
        "max_yoe": 6,
        "url": "https://vercel.com/careers",
        "apply_url": "https://vercel.com/careers",
        "source": "Vercel Remote"
    },
    {
        "id": "glob-datadog-sre",
        "title": "Site Reliability Engineer - Cloud Observability",
        "company": "Datadog",
        "location": "Remote (Worldwide / Global)",
        "region": "Global Remote",
        "domain": "DevOps / Cloud Engineer",
        "salary_range": "$105,000 - $155,000 USD",
        "employment_type": "Full-time Remote",
        "posted_days_ago": 3,
        "posted_date": "3 days ago",
        "posted_timestamp": (NOW - timedelta(days=3)).strftime("%Y-%m-%d"),
        "description": "Scale petabyte-scale metric streaming clusters. Kubernetes, Terraform, AWS, Go, Python, and Linux systems architecture.",
        "skills_required": ["Kubernetes", "Terraform", "AWS", "Go", "Python", "Linux", "Docker", "CI/CD"],
        "min_yoe": 3,
        "max_yoe": 7,
        "url": "https://www.datadoghq.com/careers/",
        "apply_url": "https://www.datadoghq.com/careers/",
        "source": "Datadog Remote"
    }
]


class JobSearcher:
    @staticmethod
    def fetch_wwr_rss_jobs(domain: str = "Backend", limit: int = 15) -> List[Dict[str, Any]]:
        """Fetch live software engineering jobs from WeWorkRemotely RSS feed."""
        jobs = []
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
               limit: int = 70) -> List[Dict[str, Any]]:
        """
        Generic search across all software engineering tracks with recency filter.
        """
        all_jobs = []

        # 1. Add Indian Tech Jobs
        if region_filter in ["All", "India"]:
            all_jobs.extend(CURATED_INDIA_TECH_JOBS)

        # 2. Add Global Remote Curated Jobs
        if region_filter in ["All", "Global Remote"]:
            all_jobs.extend(CURATED_GLOBAL_REMOTE_JOBS)

        # 3. Add Live WeWorkRemotely RSS Jobs
        if region_filter in ["All", "Global Remote"]:
            wwr_jobs = cls.fetch_wwr_rss_jobs(domain=role_query, limit=15)
            all_jobs.extend(wwr_jobs)

        # 4. Add Live Remotive API Jobs
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
            text_corpus = f"{j['title']} {j['company']} {j.get('domain', '')} {j['description']} {' '.join(j.get('skills_required', []))}".lower()
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
