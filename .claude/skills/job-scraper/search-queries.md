# Search Queries for Job Scraper

## Installed portal CLIs (primary for `/scrape`)
Discovers portal skills under `.agents/skills/*/SKILL.md` or falls back to WebSearch.

## Target Locations
- **India:** Bangalore, Hyderabad, Pune, Gurgaon, Noida, Chennai, Remote India
- **Global:** Worldwide Remote (US, Europe, Global startups hiring in India timezone)

## Target Job Boards
- **LinkedIn Jobs:** linkedin.com/jobs (Filter: India / Remote)
- **Naukri.com:** naukri.com (India tech product & GCC search)
- **Instahyre:** instahyre.com (Indian tech startups & product companies)
- **Wellfound:** wellfound.com (AngelList Talent - remote & startups)

---

## Query Categories

### Priority 1: Backend & Distributed Systems (India Product & GCCs)

#### Plain terms (portal CLIs)
```
Software Development Engineer Backend
Backend Engineer Kafka
Distributed Systems Engineer
Java Backend Engineer
SDE 2 Backend
```

#### WebSearch-only (`site:` fallback)
```
site:linkedin.com/jobs "Backend Engineer" "Kafka" Bangalore
site:linkedin.com/jobs "SDE-2" "Distributed Systems" India
site:naukri.com "Backend Developer" "Java" "Kafka" "Microservices"
site:instahyre.com "Software Engineer" "Backend" "Bangalore"
```

### Priority 2: Global Remote Software Engineering

#### Plain terms (portal CLIs)
```
Remote Backend Engineer
Software Engineer Distributed Systems
Staff / Senior Backend Engineer Remote
```

#### WebSearch-only (`site:` fallback)
```
site:linkedin.com/jobs "Backend Engineer" "Remote" "Worldwide"
site:wellfound.com "Backend Engineer" "Remote" "India"
site:remotive.com "Software Engineer" "Backend"
```

### Priority 3: Cloud & Platform Engineering

#### Plain terms (portal CLIs)
```
Cloud Platform Engineer
DevOps Engineer AWS Kubernetes
Platform Software Engineer
```

#### WebSearch-only (`site:` fallback)
```
site:linkedin.com/jobs "Platform Engineer" "AWS" "Kubernetes" Bangalore
site:linkedin.com/jobs "Cloud Software Engineer" India Remote
```
