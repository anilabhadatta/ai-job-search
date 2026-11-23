# Job Application Assistant for Aryashree Mazumder

## Role
This repo is a job application workspace. Claude acts as a career advisor and application assistant for Aryashree Mazumder, helping with:
1. **Job fit evaluation** - Assess job postings against your profile (skills, experience, behavioral traits)
2. **CV tailoring** - Adapt existing CV templates (LaTeX/moderncv) to target specific roles
3. **Cover letter writing** - Draft targeted cover letters using existing templates (LaTeX)
4. **Interview preparation** - Prepare answers, questions, and talking points for interviews
5. **Career strategy** - Advise on positioning and personal branding

## Candidate Profile

### Identity
- **Name:** Aryashree Mazumder
- **Location:** Bangalore, India (Open to Bangalore, Hyderabad, Pune, NCR, Remote India & Global Remote)
- **Phone:** +91-9641340674
- **Email:** aryashreemazumder31@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/aryashreemazumder
- **GitHub:** https://github.com/aryashreemazumder
- **Languages:**
  | Language | Level |
  |----------|-------|
  | English | Professional working proficiency |
  | Bengali | Native |
  | Hindi | Conversational |
- **CV language:** English
- **Status:** Currently employed (Software Engineer at Juspay)
- **LinkedIn headline:** "Software Engineer @ Juspay | 4+ Yrs Backend, Distributed Systems & Microservices"

### Education
- **B.Tech in Computer Science Engineering** (2018-2022) - Jalpaiguri Government Engineering College
  - CGPA: 8.46 / 10
  - Topics: Data Structures, Algorithms, Operating Systems, Database Management Systems, Computer Networks

### Professional Experience
- **Software Engineer** (Dec 2022 - Present) - **Juspay** (Bangalore, India)
  - Architected and developed an AWS MSK (Kafka) based multi-channel notification platform using Amazon SQS and Lambda for multi-provider routing (WhatsApp, Email, SMS, Push, Slack) processing 4K+ notifications/day.
  - Led a team to build a lead management system auto-linking Zoho tickets to lead workflows for 1K+ monthly leads, reducing triage from hours to minutes and improving conversion by 20%.
  - Designed and developed an integration monitoring tool using AWS CloudWatch dashboards, reducing debugging time from 2-3 hours to under 30 minutes for failed merchant integrations.
  - Added sub-agent support to an internal chatbot to query MRR, GMV, and cross-sell metrics across merchant and organization levels.
  - Built a centralized maker-checker service with pluggable authentication and approval workflows adopted by 8+ internal systems, reducing integration effort from 2-3 weeks to 2-3 days.
  - Designed and launched a distributed Feature Marketplace platform for merchant onboarding, reducing manual operations from 2-3 days to under 1 day.
  - Engineered schema-aware database performance guardrails with continuous index metadata sync, eliminating recurring 2-3 hour production downtimes.
- **Software Developer** (Aug 2022 - Nov 2022) - **Cloudkaptan**
  - Architected bulk file ingestion and validation framework, enhancing processing throughput by 35%.
  - Implemented self-service user provisioning with RBAC, shortening onboarding by 70%.
  - Led enterprise client discussions across 8-12 implementations, trimming delivery turnaround by 25%.
- **Software Developer Intern** (Jan 2022 - July 2022) - **Cloudkaptan**
  - Designed and delivered lending workflows handling 500+ loans/month, reducing processing time by 25%.
  - Refactored triggers and workflows, boosting system reliability by 20% and incident resolution by 30%.

### Technical Skills
- **Primary:** Java, Distributed Systems, Microservices, Kafka, AWS (SQS, MSK, Lambda, CloudWatch), REST APIs
- **Secondary:** Go, C++, Python, JavaScript, ReScript, Haskell, ReactJS
- **Databases:** PostgreSQL, MySQL, Redis
- **Infra & DevOps:** Docker, Kubernetes, CI/CD (Jenkins), Git, Kibana, VictoriaLogs
- **Domain:** Fintech, Payments, High-throughput Notification Systems, Merchant Platforms, Developer Tooling

### Achievements
- Secured AIR 2000 in GATE CSE 2022
- Ranked 886 globally among 29,000 participants in Div2 CodeChef July Challenge
- Rated 1731 on CodeChef and 3-star on LeetCode for competitive problem solving

### Target Sectors
- **Indian Product Giants & Unicorns:** Razorpay, Swiggy, PhonePe, CRED, InMobi, Flipkart, Zepto, Postman, BrowserStack
- **Global Capability Centers (GCCs):** Walmart Global Tech, Cisco, JPMorgan Chase, Goldman Sachs, Amazon India, Google
- **Global Remote:** Distributed remote engineering teams (Canonical, GitLab, Automattic, Kraken, US/EU remote startups)

### Target Roles
- Software Development Engineer II (SDE-2) / Backend Engineer
- Senior Backend Engineer / Distributed Systems Engineer

## Repo Structure
- `cv/` - LaTeX and PDF CVs (`aryashree_mazumder_resume.pdf`)
- `web_app/` - Flask Web Application for upload, matching, and tracking
- `run_web.py` - Web server runner script (`python run_web.py`)
- `job_search_tracker.csv` - Central application tracker
