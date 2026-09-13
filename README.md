# TruthGuard — AI-Based Digital Content Verification & Scam Detection System

<p align="center">
  <strong>Verify Before You Trust</strong>
</p>

---

## 🎯 Objective

Analyze digital content using multiple independent sources and AI to estimate whether a claim, website, social-media post, promotion or other content is trustworthy.

## 📊 Output Verdicts

| Verdict | Meaning |
|---------|---------|
| 🟢 **LIKELY TRUE** | Multiple reliable sources confirm the claim |
| 🔴 **LIKELY FALSE** | Strong evidence contradicts the claim |
| 🟡 **UNVERIFIED** | Insufficient evidence to confirm or deny |
| 🟠 **SUSPICIOUS** | Multiple warning signals detected |

Each analysis includes: **Confidence Score**, **Risk Score**, **Evidence**, **Sources**, **Reasons**, and **Earliest Traceable Source**.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js, Tailwind CSS, Axios, React Router |
| Backend | Python, FastAPI, Pydantic, httpx |
| AI/ML | LLM API, Sentence Transformers, scikit-learn |
| Database | PostgreSQL / SQLite, SQLAlchemy |
| Tools | Git, VS Code, Postman |

## 📁 Project Structure

```
truthguard/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
├── docs/              # Documentation
├── tests/             # Test datasets & scripts
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js >= 18
- Python >= 3.11
- Git

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 🔍 What Can TruthGuard Verify?

- 🌐 **Websites** — Domain safety, scam detection, shopping risk
- 📰 **News** — Claim extraction and cross-source verification
- 📱 **Social Media** — Post verification and origin tracing
- 🖼️ **Screenshots** — OCR + claim + URL verification
- 🎥 **Videos** — Speech-to-text + claim verification
- 🛒 **Shopping** — E-commerce scam detection
- 🎓 **Courses/Jobs** — Placement claim verification

## 📄 License

This project is developed as a final-year academic project.
