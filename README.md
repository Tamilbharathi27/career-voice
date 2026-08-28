# Career Voice 🎙️🤖
> **Next-Generation AI Voice Interview & Career Readiness Platform**

Career Voice is a full-stack, AI-powered mock voice interview simulator that conducts adaptive interviews, analyzes spoken candidate answers in real-time (acoustics, speech pace, filler words, technical NLP accuracy, STAR methodology alignment, and sentiment), and produces composite scorecards with actionable coaching feedback and downloadable PDF reports.

---

## 🌟 Key Features

- **Agentic AI Interviewer**: Adaptive state-machine orchestrator that asks contextual follow-up questions or pivots competencies dynamically based on candidate performance.
- **Real-Time Voice Studio**: In-browser microphone capture with live frequency and waveform canvas visualization, audio level meter, and playback.
- **Multi-Modal AI Evaluation Pipeline**:
  - **Speech-to-Text (STT)**: Transcribes candidate speech with high fidelity.
  - **Voice & Acoustic Analysis**: Quantifies words per minute (WPM), speech duration, pause/silence ratio, pitch variance, and filler-word detection (`um`, `uh`, `like`, `you know`, `actually`, `basically`).
  - **NLP & Technical Relevance**: Evaluates semantic relevance, technical keyword coverage, and STAR (Situation, Task, Action, Result) structure.
  - **Sentiment & Confidence**: Assesses speaker tone, emotional poise, and delivery conviction.
  - **Composite ML Scoring**: Generates a weighted multi-metric score (0–100) per question and overall session.
- **Personalized Coaching & Feedback**: Actionable recommendations highlighting concrete strengths, improvement areas, and model STAR answers.
- **Interactive Dashboards**:
  - **Student Portal**: Interview history, score trends over time, radar chart competency breakdown, readiness score.
  - **Recruiter Portal**: Candidate directory, comparative analytics, response transcript inspection, audio playback, and score filters.
- **PDF Report Generation**: Comprehensive, downloadable PDF report cards built with ReportLab.

---

## 🛠️ Tech Stack

- **Frontend**: React 18, Vite, React Router v6, TailwindCSS, Lucide Icons, Web Audio API / MediaRecorder, Axios
- **Backend**: Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic
- **Database**: Supabase (PostgreSQL)
- **Audio & Signal Processing**: Web Audio API, NumPy, SciPy, Wave
- **Reporting**: ReportLab PDF generator
- **Auth**: JWT (Access + Refresh tokens), bcrypt password hashing
- **Deployment**: Docker & Docker Compose

---

## 🚀 Quick Start Guide

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.10+)
- (Optional) [Docker Desktop](https://www.docker.com/)

---

### Option 1: Run with Docker Compose (Recommended)

```bash
# 1. Clone the repository and enter directory
cd "Career Voice -Mini project"

# 2. Copy environment file
cp .env.example .env

# 3. Build and launch all services (MySQL, Redis, Backend, Frontend)
docker-compose up --build
```

- **Frontend**: `http://localhost:5173`
- **Backend API Docs (Swagger)**: `http://localhost:8000/docs`

---

### Option 2: Run Locally (Development Mode)

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database setup & seed initial templates
python -m app.db.init_db

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Visit `http://localhost:5173` to access Career Voice!

---

## 📂 Project Structure

```
career-voice/
├── frontend/                  # React.js SPA
│   ├── src/
│   │   ├── api/               # Axios client & endpoints
│   │   ├── components/        # Waveforms, Avatar, Radar, Nav, Cards
│   │   ├── context/           # AuthContext & Session state
│   │   ├── hooks/             # useAudioRecorder hook
│   │   ├── pages/
│   │   │   ├── auth/          # Login, Register
│   │   │   ├── student/       # Dashboard, Setup, Voice Interview, Report, Profile
│   │   │   └── recruiter/     # Candidate Directory, Candidate Detail
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint
│   │   ├── core/              # Config, Security, JWT, Deps
│   │   ├── db/                # SQLAlchemy session & Base
│   │   ├── models/            # User, Profile, InterviewSession, Question, Answer, AnswerEvaluation, SessionReport
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── services/          # STT, NLP, Voice Acoustics, Scoring, Feedback, Agent Interviewer, PDF Reports
│   │   └── api/v1/            # Auth, Users, Interviews, Voice, STT, NLP, Scoring, Feedback, Reports routes
│   ├── storage/               # Audio uploads & generated PDF reports
│   ├── tests/                 # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🧪 Testing

To run the backend automated test suite:
```bash
cd backend
pytest -v
```

---

## 🔒 Security & Architecture Decisions

- **Stateless Authentication**: Access tokens expire in 60 minutes; refresh tokens provide secure session continuation without storing credentials in memory.
- **Data Isolation**: All interview recordings and reports are scoped strictly to the authenticated user ID with role-based access controls protecting recruiter endpoints.
- **Fail-Safe Processing**: All AI services include offline signal processing heuristics and speech fallback logic to guarantee 100% testability and reliability even without third-party external API keys.
