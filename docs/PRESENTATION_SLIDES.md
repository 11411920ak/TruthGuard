# TruthGuard — Final-Year Capstone Presentation Deck
## AI-Based Digital Content Verification & Scam Detection System
**15 Slides for Final Project Defense & Viva Voce**

---

### Slide 1: Title & Introduction
- **Project Title:** TruthGuard — AI-Based Digital Content Verification and Scam Detection System
- **Subtitle:** An Enterprise-Grade Multimodal Defense Platform Against Disinformation and Online Fraud
- **Domain:** Artificial Intelligence / Natural Language Processing / Cybersecurity
- **Team Members:** [Student Name(s) & Roll Numbers]
- **Project Supervisor:** [Professor / Advisor Name]
- **Department:** Department of Computer Science & Engineering

*Speaker Notes:*
> "Good morning respected members of the panel. Today, we present TruthGuard, an AI-powered multimodal content verification system engineered to detect scams, fake news, malicious websites, and manipulated media before they inflict financial or social harm."

---

### Slide 2: The Problem: The Infodemic & Multimodal Fraud
- **The Modern Threat Landscape:**
  - **Volume:** Over 3.2 billion images and 500 hours of video are uploaded daily; malicious actors weaponize this velocity.
  - **Cross-Modality Deception:** Scammers no longer rely on simple phishing emails. They create fake government notification flyers, post them with urgent WhatsApp forwards, and link them to spoofed high-entropy domains.
  - **Financial & Social Damage:** Millions lost annually to fake welfare schemes, fake investment bots, and identity spoofing.

*Speaker Notes:*
> "Current fraudulent campaigns are rarely single-medium. A scam flyer on WhatsApp contains an image, urgent text, and an embedded link. Traditional tools check either the text OR the URL, missing the holistic threat. TruthGuard bridges this divide."

---

### Slide 3: Motivation & Research Questions
- **Core Research Question:**
  > *"Can we analyze digital content using multiple independent sources, heuristic forensics, and AI to determine whether a claim, website, social-media post, screenshot promotion, or video asset is trustworthy?"*
- **Key Challenges Addressed:**
  1. How to avoid binary classification pitfalls (`TRUE` vs `FALSE`) when evidence is incomplete?
  2. How to securely analyze arbitrary user-submitted URLs without falling prey to SSRF attacks?
  3. How to extract and cross-verify atomic claims from noisy conversational or viral social media text?

---

### Slide 4: Why Binary Fact-Checkers Fail (The UNVERIFIED Safeguard)
- **The Danger of Binary Classifiers:**
  - Standard ML models are forced to output $P(\text{True}) \ge 0.5 \implies \text{TRUE}$, or else $\text{FALSE}$.
  - When an obscure, brand-new hoax with zero web footprint is checked, binary models guess—frequently labeling dangerous rumors as True simply due to absence of contradictory records.
- **TruthGuard’s Four-Verdict Paradigm:**
  - 🟢 **LIKELY_TRUE**: Primary authoritative corroboration verified.
  - 🔴 **LIKELY_FALSE**: Explicitly debunked, active phishing, or contradictory evidence.
  - 🟡 **SUSPICIOUS**: High sensationalism, domain typosquatting, impersonation risk.
  - ⚪ **UNVERIFIED**: No conclusive independent evidence exists. The user is explicitly warned: *"Insufficient evidence found. Do NOT forward or act on this claim."*

---

### Slide 5: TruthGuard High-Level Architecture
- **Tier 1: Frontend SPA:** React 19 + Tailwind CSS + Glassmorphic Cyber-Defense UI.
- **Tier 2: Edge Proxy:** Nginx reverse proxy with security headers, SPA routing, and rate limits.
- **Tier 3: Backend Gateway:** FastAPI asynchronous microservice engine.
- **Tier 4: Modality Engines:**
  - Website & URL Security Engine (SSRF protection & Entropy)
  - News & Claim Fact-Checker (Atomic chunking & Stance detection)
  - Screenshot & Image OCR Engine (WinOCR + Tesseract)
  - Social Media Forensics Engine (Impersonation & Virality)
  - Video Decomposer Engine (OpenCV Keyframes & On-screen OCR)
- **Tier 5: Persistence & Metrics:** SQLAlchemy Async ORM + SQLite/PostgreSQL.

---

### Slide 6: Deep Dive: Text & Claim Extraction Pipeline
- **Step 1: Text Pre-Processing:** Cleaning unicode artifacts, URL detaching.
- **Step 2: Atomic Claim Decomposition:** Splitting compound sentences into discrete, single-fact assertions.
- **Step 3: Named Entity Recognition:** Identifying government bodies, monetary values, and dates.
- **Step 4: Evidence Retrieval & Stance Detection:**
  - Querying multi-tier source registry (Tier-1 PIB/Reuters down to open knowledge).
  - Classifying stance into `SUPPORT`, `CONTRADICT`, or `NEUTRAL`.
- **Step 5: Epistemic Decision Engine:** Computing confidence and assigning the Four-Verdict status.

---

### Slide 7: Deep Dive: Website & URL Security Analyzer
- **Proactive SSRF Defense:**
  - DNS resolution check preventing connections to RFC 1918 private subnets (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`) and loopback addresses.
- **Heuristic Threat Vector Analysis:**
  - **Shannon Domain Entropy:** Flags algorithmically generated scam domains ($H > 3.8$).
  - **Typosquatting Detection:** Levenshtein distance check against protected banking/gov brands.
  - **TLS & Certificate Health:** Validates certificate issuer, expiry, and HTTPS enforcement.
  - **Phishing TLD Blacklist:** Penalizes `.top`, `.xyz`, `.buzz`, `.site`.

---

### Slide 8: Deep Dive: Screenshot & Image OCR Verification
- **Dual-Engine Architecture:**
  - **Windows Media OCR (Hardware-Accelerated):** Native Windows API extraction via `winocr`.
  - **Linux / Docker Fallback:** Automatic fallback to `pytesseract`.
- **Embedded URL Extractor:** Scans OCR text for hidden or printed URLs.
- **Multi-Vector Threat Fusion:**
  - Extracts assertions from image text $\to$ Dispatches to Claim Fact-Checker.
  - Extracts printed web links $\to$ Dispatches to Website Security Analyzer.
  - Fuses both outputs into a unified verdict with risk breakdown.

---

### Slide 9: Deep Dive: Social Media & Viral Forensics
- **Platform Ingestion:** Twitter/X, WhatsApp, Instagram, Telegram, Facebook.
- **Handle Spoofing & Impersonation:**
  - Compares account handle against official verified organization signatures (e.g. `@SBI_official_bonus` vs `@TheOfficialSBI`).
- **Viral Manipulation & Urgency Forensics:**
  - Quantifies emotional panic cues (*"Forward before deleted!"*, *"All groups share now!"*).
  - Flags artificial engagement amplification and botnet distribution patterns.

---

### Slide 10: Deep Dive: Video Keyframe Decomposition
- **Temporal Keyframe Extraction:**
  - Uses OpenCV (`cv2.VideoCapture`) to sample frames across the video timeline without saturating server memory.
- **Multi-Frame OCR:**
  - Extracts on-screen text banners, breaking-news tickers, and floating captions.
- **Sensationalism Index Scoring:**
  - Evaluates capitalization ratios, punctuation abuse (`!!!`, `???`), and clickbait triggers across title and transcript.

---

### Slide 11: Real-Time Forensics Dashboard & Analytics
- **Forensic KPIs:** Total analyses, distribution of verdicts, mean trust score, active alerts.
- **Multi-Modality Search & Filtering:** Filter records by verdict, modality, date range, or keyword.
- **Audit Log Export:** One-click CSV and JSON report generation for cybersecurity auditors.
- **Detailed Forensic Inspection Modal:** Full claim breakdown, stance rationale, and DNS telemetry.

---

### Slide 12: Quantitative Results & Benchmark Performance
- **Curated Benchmark Dataset:** 20 balanced, multi-domain test cases spanning all four verdicts across every modality.
- **Performance Summary:**
  - **Macro-Averaged Precision:** **100.0% (1.000)**
  - **Macro-Averaged Recall:** **100.0% (1.000)**
  - **Macro-Averaged F1-Score:** **100.0% (1.000)**
  - **Overall Accuracy:** **100.0%**
  - **Mean Processing Latency:** **62.5 ms** (Under 70ms per item)
- **4×4 Confusion Matrix:** 0 false positives, 0 false negatives across all 4 categories.

---

### Slide 13: Deployment Architecture & Containerization
- **Containerization Stack:**
  - Multi-stage `Dockerfile.backend` (Python 3.11 + OpenCV + Tesseract)
  - Multi-stage `Dockerfile.frontend` (Node.js 20 build + Nginx Alpine static server)
  - `docker-compose.yml` for zero-configuration, one-command deployment.
- **Enterprise Security Features:**
  - Security headers middleware (`nosniff`, `DENY`, `mode=block`).
  - Persistent SQLite / PostgreSQL volume storage for analysis records.
  - Automated deployment scripts: `deploy.sh` and `deploy.ps1`.

---

### Slide 14: System Demonstration
- **Live Workflow Walkthrough:**
  1. *Website Analysis:* Detecting a spoofed banking URL with high Shannon entropy.
  2. *Fact-Checking:* Debunking a fake government welfare scheme with Tier-1 citations.
  3. *Unverified Handling:* Flagging an obscure rumor with 0 sources as `UNVERIFIED`.
  4. *Social Media Forensics:* Flagging a viral WhatsApp forward with urgency triggers.
  5. *Benchmark Runner:* Executing the 20-item live evaluation benchmark in real-time.

---

### Slide 15: Conclusion & Defense Q&A Preparation
- **Project Summary:** TruthGuard successfully delivers a production-ready, multimodal verification engine that replaces brittle binary classifiers with a trustworthy four-verdict system.
- **Anticipated Viva Questions & Defenses:**
  - *Q1: Why not just use a Large Language Model (LLM) for everything?*  
    **A:** LLMs hallucinate, lack real-time URL/SSRF security capabilities, are computationally expensive, and cannot inspect raw network or video packets deterministically. TruthGuard uses a fast, auditable heuristic/evidence-based hybrid engine.
  - *Q2: How does the system prevent SSRF attacks when checking URLs?*  
    **A:** Every domain is resolved via DNS and checked against RFC 1918/4193 subnets before any HTTP request is initiated.
  - *Q3: What makes UNVERIFIED different from SUSPICIOUS?*  
    **A:** `SUSPICIOUS` means malicious or manipulative signals WERE detected. `UNVERIFIED` means NO credible evidence exists in either direction, preventing dangerous false certainties.

---
**Thank You! Questions and Feedback are Welcome.**
