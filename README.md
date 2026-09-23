<<<<<<< HEAD
# AI Content Generation Chatbot Using LLM and Prompt Engineering

A production-style academic mini-project designed for a **Generative AI / AI curriculum**. Built from scratch using **Python FastAPI**, **Vanilla HTML5/CSS3/JavaScript**, **SQLite with SQLAlchemy**, and **Groq (gpt-oss-120b)**.

---

## 1. Project Overview

The **AI Content Generation Chatbot** is a full-stack generative AI system that produces customized, high-quality, and domain-specific content across multiple formats:
- **Professional Emails**: Complete with subject line, greeting, context, body, call to action, and signature placeholders.
- **Structured Reports**: Markdown reports formatted with executive summaries, objectives, findings, analytical discussions, and recommendations.
- **Technical Explanations**: Audience-adaptive educational explanations that dynamically shift between intuitive beginner analogies and advanced architectural deep-dives.
- **General Content**: Versatile content generation governed by strict stylistic and length boundaries.

The core innovation of this project lies in its **dedicated Prompt Engineering Layer**: raw user input is never sent directly to the Large Language Model. Instead, it is systematically enriched with persona roles, audience calibration, tone parameters, structural boundaries, and negative safety constraints.

---

## 2. Problem Statement & Objectives

### Problem Statement
Standard interactions with Large Language Models often suffer from:
1. **Unpredictable Output Layouts**: The model returns unformatted walls of text without structural hierarchy.
2. **Audience Misalignment**: Technical topics are either overly complex for beginners or trivial for experts.
3. **Hallucination of Personal Data**: When generating correspondence (e.g., emails), naive LLMs often fabricate personal names, phone numbers, and company titles.
4. **Lack of In-Place Transformation**: Users often need to expand, shorten, improve, or regenerate content without manual prompt retyping.

### Project Objectives
- Demonstrate practical **Prompt Engineering techniques** in a production-style architecture.
- Integrate a local, privacy-preserving LLM runtime (**Groq with gpt-oss-120b**) running on local consumer hardware.
- Deliver an intuitive, responsive Single Page Web Application (**HTML5/CSS3/JavaScript**) without heavy frontend frameworks.
- Implement robust persistence for conversation history using **SQLite** and **SQLAlchemy ORM**.
- Provide complete REST API endpoints with Pydantic validation and comprehensive test suites.

---

## 3. Technology Stack

| Layer | Technology | Rationale / Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Lightweight, zero-build-step, fast-loading, pure web standards |
| **Backend** | Python 3.10+, FastAPI, Uvicorn | High-performance asynchronous REST API framework with automatic OpenAPI documentation |
| **Data Validation** | Pydantic v2 | Type safety, request body parsing, and field validation |
| **AI Runtime** | Groq (Local Daemon) | Zero-cost, privacy-first local LLM inference without paid API keys |
| **LLM Model** | Meta gpt-oss-120b (3.2B parameters) | State-of-the-art lightweight open-weights instruction model |
| **Database** | SQLite + SQLAlchemy ORM | Lightweight, zero-configuration local database with ORM mapping |
| **Testing** | Pytest, FastAPI TestClient | Automated test suite verifying health, schemas, and prompt builders |
| **Deployment** | Render-compatible (`run.py`, `render.yaml`) | Production-ready port binding and modular cloud provider adapter |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Browser Client (Vanilla HTML5 / CSS3 / JS)     │
│  - Dashboard View   - Chatbot View   - History View   - About│
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Web Application                  │
│                     (app/main.py, run.py)                   │
├──────────────────────────────┬──────────────────────────────┤
│  Routes Layer (/api)         │  Controllers                 │
│   ├── health.py              │   ├── GET /api/health        │
│   │                          │   └── GET /api/Groq-status │
│   ├── chat.py                │   ├── POST /api/generate     │
│   │                          │   ├── POST /api/regenerate   │
│   │                          │   ├── POST /api/improve      │
│   │                          │   ├── POST /api/shorten      │
│   │                          │   └── POST /api/expand       │
│   └── history.py             │   ├── GET /api/history       │
│                              │   └── DELETE /api/history    │
├──────────────────────────────┴──────────────────────────────┤
│  Services Layer                                             │
│   ├── PromptService (app/services/prompt_service.py)        │
│   │    Enforces: Role, Task, Context, Audience, Tone,       │
│   │              Length, Requirements, Output Format        │
│   │                                                         │
│   └── GroqService (app/services/Groq_service.py)        │
│        Async HTTP Client connecting to https://api.groq.com│
├──────────────────────────────┬──────────────────────────────┤
│  Database Layer              │  Local LLM Runtime           │
│   ├── SQLite (chatbot.db)    │   └── Groq Daemon          │
│   └── SQLAlchemy ORM         │        └── gpt-oss-120b (3.2B)  │
└──────────────────────────────┴──────────────────────────────┘
```

---

## 5. Prompt Engineering System (College Viva Focus)

The project implements an 8-component prompt engineering framework:

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. ROLE:          System persona (e.g. Senior Analyst / Educator)│
│ 2. TASK:          Precise instruction of what to produce        │
│ 3. CONTEXT:       Original query and background circumstances   │
│ 4. AUDIENCE:      Beginner, Student, Professional, Expert       │
│ 5. TONE:          Professional, Friendly, Academic, Simple      │
│ 6. LENGTH:        Short, Medium, Detailed (structural depth)    │
│ 7. REQUIREMENTS:  Strict factual boundaries & no invented data  │
│ 8. OUTPUT FORMAT: Explicit Markdown scaffolding and headers     │
└─────────────────────────────────────────────────────────────────┘
```

### Prompt Engineering Techniques Explained

1. **Role Prompting**: Directs the LLM to adopt an expert persona (e.g., *"You are an executive communication specialist..."*).
2. **Instruction Prompting**: Uses clear, imperative verbs defining step-by-step goals.
3. **Audience Conditioning**:
   - For **Beginner / Student**: Employs real-world analogies, defines foundational concepts gently, and avoids jargon.
   - For **Technical Expert**: Uses domain-specific terms, discusses trade-offs, and provides implementation concepts.
4. **Tone & Register Control**: Enforces consistent voice (e.g., *Formal*, *Academic*, *Friendly*).
5. **Length Control**: Dictates paragraph and section depth (Short, Medium, Detailed).
6. **Negative Constraints / Anti-Hallucination**: Prohibits inventing real user credentials or false data, enforcing placeholders such as `[Your Name]`, `[Company Name]`.
7. **Output Formatting Scaffolding**: Enforces Markdown templates (`# Title`, `## Executive Summary`, `## Findings`), guaranteeing predictable structural layout.
8. **Transformation Prompting**: Powers contextual transformations (*Regenerate*, *Improve*, *Shorten*, *Expand*) without simple string truncation.

### Viva Demonstration: Naive vs. Engineered Prompt

| Dimension | Naive Prompt | Engineered Prompt (Our System) |
| :--- | :--- | :--- |
| **Input** | *"Explain REST API."* | Structured prompt with Role, Audience: Beginner, Tone: Simple, Format: Analogy + Workflow + Pros/Cons. |
| **Audience** | Undefined; model guesses randomly | Explicitly tuned for a first-year student with an intuitive restaurant waiter analogy |
| **Layout** | Random paragraphs or single block | 6 distinct Markdown sections with bullet points |
| **Reliability** | Unpredictable length & tone | Guaranteed consistency suitable for grading |

---

## 6. Project Structure

```
AI_Content_Generation_Chatbot/
│
├── app/
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # FastAPI application & lifespan startup
│   ├── database.py                 # SQLAlchemy SQLite setup & session dependency
│   ├── models.py                   # ChatHistory database model
│   ├── schemas.py                  # Pydantic request/response schemas & enums
│   │
│   ├── routes/
│   │   ├── __init__.py             # Route package exports
│   │   ├── chat.py                 # Generation & transformation endpoints
│   │   ├── history.py              # CRUD history endpoints
│   │   └── health.py               # Health & Groq diagnostic checks
│   │
│   ├── services/
│   │   ├── __init__.py             # Services package exports
│   │   ├── Groq_service.py       # Async HTTP client for Groq API
│   │   └── prompt_service.py       # Prompt orchestration & transformers
│   │
│   └── prompts/
│       ├── __init__.py             # Prompts exports
│       ├── email.py                # Professional email template
│       ├── report.py               # Sectioned business/academic report
│       ├── technical.py            # Adaptive technical explanation template
│       └── general.py              # General content generation template
│
├── static/
│   ├── css/
│   │   └── style.css               # Modern slate responsive stylesheet
│   └── js/
│       └── app.js                  # Vanilla JS frontend logic & state management
│
├── templates/
│   └── index.html                  # Main SPA interface (Dashboard, Chat, History, About)
│
├── tests/
│   ├── __init__.py                 # Tests package init
│   ├── test_health.py              # Health, validation, and history tests
│   └── test_prompt_service.py      # Unit tests for prompt engineering builders
│
├── .env.example                    # Template environment variables
├── .gitignore                      # Git ignore patterns (venv, db, cache)
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render cloud deployment specification
├── README.md                       # Comprehensive project documentation
└── run.py                          # Application entry point (host & port binding)
```

---

## 7. Prerequisites & Installation (Windows)

### Step 1: Install Groq and Pull gpt-oss-120b
1. Download Groq for Windows from [https://Groq.com](https://Groq.com).
2. Open PowerShell and verify installation:
   ```powershell
   Groq --version
   ```
3. Pull the Meta gpt-oss-120b model:
   ```powershell
   Groq pull openai/gpt-oss-120b
   ```
4. Verify the installed model:
   ```powershell
   Groq list
   ```
5. Ensure Groq is running (it runs in the background automatically or can be started via):
   ```powershell
   Groq run openai/gpt-oss-120b
   ```

### Step 2: Clone / Open the Project Folder
```powershell
cd c:\Users\pushp\AI_Content_Generation_Chatbot
```

### Step 3: Set Up Python Virtual Environment
1. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   *(If script execution is disabled in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

3. Install required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` settings:
```ini
Groq_BASE_URL=https://api.groq.com
Groq_MODEL=openai/gpt-oss-120b
HOST=0.0.0.0
PORT=8000
```

---

## 8. Running the Application

### Local Development

**Option 1: Using run.py (Recommended)**
```powershell
python run.py
```

**Option 2: Using Uvicorn directly**
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: Production-style local test**
```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open your web browser and navigate to:
- **Application UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

### Option 1: Using run.py (Recommended)
```powershell
python run.py
```

### Option 2: Using Uvicorn directly
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your web browser and navigate to:
- **Application UI:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 9. Application Walkthrough & User Guide

### 1. Dashboard View
- Displays real-time **Groq Runtime Diagnostics** (Connected / Disconnected).
- Displays model status (`openai/gpt-oss-120b`), URL (`https://api.groq.com`), and feature summaries.

### 2. AI Chatbot View
1. **Configure Parameters**:
   - **Content Type**: `Email`, `Report`, `Technical Explanation`, `General Content`
   - **Tone**: `Professional`, `Friendly`, `Academic`, `Simple`, `Formal`
   - **Audience**: `Beginner`, `Student`, `Professional`, `Technical Expert`, `General Audience`
   - **Length**: `Short`, `Medium`, `Detailed`
2. **Submit Query**: Type instructions in the prompt box and hit **Enter** (or click **Generate**). Use **Shift+Enter** for new lines.
3. **Inspect Output**: Response is formatted with metadata badges.
4. **Trigger Actions**:
   - **Copy**: Copies response text to clipboard with instant visual feedback (*Copied!*).
   - **Download (.txt)**: Generates and downloads a `.txt` file using client-side JavaScript Blob.
   - **Regenerate**: Asks gpt-oss-120b for an alternative variation with the same constraints.
   - **Improve**: Polishes vocabulary and flow while preserving structure.
   - **Shorten**: Condenses output to high-impact brevity.
   - **Expand**: Elaborates with deeper details, examples, and analysis.

### 3. History View
- View previous generations stored in SQLite (`chatbot.db`).
- Click **Open** to inspect the full prompt and response in a modal.
- Click **Load into Chatbot** to bring past generations back into the active workspace.
- Click **Delete** to remove individual records or **Clear All History** to reset.

### 4. About & Prompt Engineering View
- Complete academic viva preparation guide.
- Detailed explanation of all 8 prompt engineering mechanisms.
- Interactive side-by-side comparison of **Naive vs. Engineered Prompts**.

---

## 10. API Documentation

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves frontend Single Page Application | None |
| `GET` | `/api/health` | Backend status and uptime timestamp | None |
| `GET` | `/api/Groq-status` | Checks Groq connectivity & model presence | None |
| `POST` | `/api/generate` | Generates content using prompt engineering | `GenerateRequest` |
| `POST` | `/api/regenerate` | Generates alternative response variation | `RegenerateRequest` |
| `POST` | `/api/improve` | Polishes and enhances existing response | `TransformRequest` |
| `POST` | `/api/shorten` | Condenses response into concise summary | `TransformRequest` |
| `POST` | `/api/expand` | Expands response with comprehensive details | `TransformRequest` |
| `GET` | `/api/history` | Lists conversation history with pagination | Query params (`limit`, `session_id`) |
| `GET` | `/api/history/{id}` | Fetches individual history record by ID | None |
| `DELETE` | `/api/history/{id}` | Deletes individual history record by ID | None |
| `DELETE` | `/api/history` | Clears all history or session-specific history | Query params (`session_id`) |

---

## 11. Database Schema

The SQLite database (`chatbot.db`) is automatically initialized on application startup via SQLAlchemy:

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(64) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    user_prompt TEXT NOT NULL,
    generated_response TEXT NOT NULL,
    tone VARCHAR(50) NOT NULL,
    audience VARCHAR(50) NOT NULL,
    length VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL
);
```

---

## 12. Automated Testing

Run the automated test suite using `pytest`:

```powershell
pytest tests/ -v
```

### Test Coverage:
- `test_health_endpoint`: Backend health and timestamp verification.
- `test_Groq_status_endpoint`: Checks diagnostic response structure.
- `test_home_page_serves_html`: Ensures SPA template loads correctly.
- `test_empty_prompt_validation`: Verifies HTTP 422 for blank prompts.
- `test_invalid_content_type_validation`: Verifies rejection of unsupported types.
- `test_history_crud_flow`: Tests history retrieval, count, and 404 behavior.
- `test_build_email_prompt_structure`: Verifies email placeholders & layout.
- `test_build_report_prompt_structure`: Verifies sectioned markdown reporting.
- `test_build_technical_prompt_beginner`: Verifies analogies & simple definition.
- `test_build_technical_prompt_expert`: Verifies architectural trade-offs.
- `test_build_general_prompt`: Verifies general content boundary injection.
- `test_prompt_service_routing`: Verifies central builder routing.
- `test_transformation_prompts`: Verifies improve, shorten, and expand builders.

*All unit tests run independently of whether Groq is active.*

---

## 13. Render Cloud Deployment

### Deployment Architecture and Limitations

This project is configured with `render.yaml` and binds to `0.0.0.0` and the `PORT` environment variable.

> [!IMPORTANT]
> **Critical Groq Deployment Limitation:**
> The primary working mode for this mini-project is **Local Mode** (FastAPI communicating with your local Groq instance running Meta gpt-oss-120b).
> A cloud instance deployed on Render **cannot** automatically connect to `the local machine` on your personal laptop because localhost on Render refers to the Render server itself, not your local machine.

### Current Deployment Status

The application will deploy successfully to Render, but **AI generation will not work** with the default configuration because:
- Render cannot access your local Groq server at `the local machine`
- The `render.yaml` is configured for local development by default
- No cloud LLM provider is currently configured

### Deployment Steps

1. **Initialize Git Repository** (if not already done):
   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub and create a new repository
   - Push your local repository to GitHub:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy to Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Deploy Web Service"

4. **Post-Deployment Configuration**:
   After deployment, you have two options to enable AI generation:

   **Option A: Use a Remote Groq Server**
   - Deploy Groq to a server with a public IP
   - Update the `Groq_BASE_URL` environment variable in Render to point to your remote Groq server
   - Ensure the remote server is accessible and has the `openai/gpt-oss-120b` model installed

   **Option B: Switch to a Cloud LLM Provider**
   - The modular `app/services/ai_provider.py` layer is designed to support cloud providers
   - To add cloud support, you would need to:
     1. Create a new service file (e.g., `app/services/openai_service.py`)
     2. Update `app/services/ai_provider.py` to include the new provider
     3. Add the necessary API keys to Render environment variables
     4. Update `AI_PROVIDER` environment variable in Render

### Repository Status

The repository is now **fully prepared for GitHub and Render deployment**:

✅ **Git Repository Initialized**
- Clean Git repository with proper commit history
- No sensitive files committed (.env, database files, etc.)
- Proper .gitignore configuration

✅ **Render Configuration**
- `render.yaml` configured with proper build and start commands
- Health check endpoint configured at `/api/health`
- Python version specified as 3.13
- Environment variables documented

✅ **Production Compatibility**
- Application binds to `0.0.0.0` and uses `PORT` environment variable
- Static files and templates configured for production serving
- Database auto-creation on startup
- Health endpoint works independently of AI service

✅ **Code Quality**
- All tests passing (13/13 tests)
- Proper error handling and validation
- Modular architecture for easy provider switching
- No hardcoded secrets or API keys

### Next Steps for Deployment

1. **Push to GitHub** (if not already done):
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git branch -M main
   git push -u origin main
   ```

2. **Connect to Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`
   - Deploy

3. **Post-Deployment**:
   - Monitor deployment logs
   - Test health endpoint: `https://your-app.onrender.com/api/health`
   - Configure remote Groq or cloud LLM provider for AI generation

### Expected Deployment Behavior

**What WILL work on Render:**
- Application starts successfully
- Health check endpoint `/api/health` returns 200
- Frontend loads correctly at `/`
- Static files (CSS, JavaScript) are served
- API endpoints are accessible
- Database operations work (SQLite)
- History functionality works

**What WILL NOT work on Render (with default config):**
- AI content generation (Groq connection will fail)
- `/api/Groq-status` will show "Groq is not running"
- Generate, Regenerate, Improve, Shorten, Expand operations will fail

### Environment Variables for Render

Update these environment variables in your Render dashboard after deployment:

```ini
# AI Provider Configuration
AI_PROVIDER=Groq

# Groq Configuration (only works with remote Groq server)
Groq_BASE_URL=https://your-remote-Groq-server.com
Groq_MODEL=openai/gpt-oss-120b

# Database Configuration (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./chatbot.db
```

### Health Check

The application uses `/api/health` as the health check endpoint, which:
- Returns HTTP 200 when the application is running
- Does not depend on Groq being available
- Returns a simple JSON response with status and timestamp

This ensures Render can monitor the application health even when AI generation is unavailable.

---

## 14. Viva Questions & Answers (Quick Revision)

**Q1: Why did you not send the user's query directly to Groq?**  
*Answer:* Raw user input lack persona, tone constraints, length limits, and output format guidelines. The prompt engineering layer ensures consistent, high-quality, and structured Markdown output while preventing hallucinated personal data.

**Q2: How does audience conditioning work in technical explanations?**  
*Answer:* If the user selects *Beginner*, the prompt template instructs the model to use real-world analogies (e.g. comparing REST APIs to restaurant waiters) and define terms simply. If *Technical Expert* is chosen, the prompt requires discussion of architectural trade-offs, protocols, and implementation considerations.

**Q3: How are the response actions (Improve, Shorten, Expand) implemented?**  
*Answer:* Rather than performing crude string slicing, the backend uses contextual prompt engineering. The previous generated response is fed back into specialized prompts with editorial personas that instruct gpt-oss-120b to rewrite the text appropriately.

**Q4: How does the application prevent raw stack traces from reaching the frontend?**  
*Answer:* The `GroqService` intercepts `ConnectError` and `TimeoutException` from `httpx`, wrapping them into user-friendly application errors (`"Groq is not running. Please start Groq and try again."`) mapped to HTTP 503/504 statuses.

---

## 15. Conclusion & Learning Outcomes

Through building this project, the following core competencies were developed:
1. Orchestrating local LLMs via REST APIs without paid commercial services.
2. Formulating structured, constraint-driven Prompt Engineering templates.
3. Architecting clean, decoupled Python FastAPI backends with Pydantic validation.
4. Implementing local persistence with SQLite and SQLAlchemy.
5. Building responsive, accessible user interfaces using pure web standards (HTML5/CSS3/JavaScript).
=======
# AI_Content_Generation_Chatbot
>>>>>>> 1c8c133cebb8153ea7954d6da1b242fc545feadd
