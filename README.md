<<<<<<< HEAD
# AI Content Generation Chatbot Using LLM and Prompt Engineering

A production-style academic mini-project designed for a **Generative AI / AI curriculum**. Built from scratch using **Python FastAPI**, **Vanilla HTML5/CSS3/JavaScript**, **SQLite with SQLAlchemy**, and **Ollama (Llama 3.2)**.

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
- Integrate a local, privacy-preserving LLM runtime (**Ollama with Llama 3.2**) running on local consumer hardware.
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
| **AI Runtime** | Ollama (Local Daemon) | Zero-cost, privacy-first local LLM inference without paid API keys |
| **LLM Model** | Meta Llama 3.2 (3.2B parameters) | State-of-the-art lightweight open-weights instruction model |
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
│   │                          │   └── GET /api/ollama-status │
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
│   └── OllamaService (app/services/ollama_service.py)        │
│        Async HTTP Client connecting to http://127.0.0.1:11434│
├──────────────────────────────┬──────────────────────────────┤
│  Database Layer              │  Local LLM Runtime           │
│   ├── SQLite (chatbot.db)    │   └── Ollama Daemon          │
│   └── SQLAlchemy ORM         │        └── Llama 3.2 (3.2B)  │
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
│   │   └── health.py               # Health & Ollama diagnostic checks
│   │
│   ├── services/
│   │   ├── __init__.py             # Services package exports
│   │   ├── ollama_service.py       # Async HTTP client for Ollama API
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

### Step 1: Install Ollama and Pull Llama 3.2
1. Download Ollama for Windows from [https://ollama.com](https://ollama.com).
2. Open PowerShell and verify installation:
   ```powershell
   ollama --version
   ```
3. Pull the Meta Llama 3.2 model:
   ```powershell
   ollama pull llama3.2
   ```
4. Verify the installed model:
   ```powershell
   ollama list
   ```
5. Ensure Ollama is running (it runs in the background automatically or can be started via):
   ```powershell
   ollama run llama3.2
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
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2
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

### Option 1: Using run.py (Recommended)
```powershell
python run.py
```

### Option 2: Using Uvicorn directly
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
---

## 9. Application Walkthrough & User Guide

### 1. Dashboard View
- Displays real-time **Ollama Runtime Diagnostics** (Connected / Disconnected).
- Displays model status (`llama3.2`), URL (`http://127.0.0.1:11434`), and feature summaries.

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
   - **Regenerate**: Asks Llama 3.2 for an alternative variation with the same constraints.
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
| `GET` | `/api/ollama-status` | Checks Ollama connectivity & model presence | None |
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
- `test_ollama_status_endpoint`: Checks diagnostic response structure.
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

*All unit tests run independently of whether Ollama is active.*

## 13. Conclusion & Learning Outcomes

Through building this project, the following core competencies were developed:
1. Orchestrating local LLMs via REST APIs without paid commercial services.
2. Formulating structured, constraint-driven Prompt Engineering templates.
3. Architecting clean, decoupled Python FastAPI backends with Pydantic validation.
4. Implementing local persistence with SQLite and SQLAlchemy.
5. Building responsive, accessible user interfaces using pure web standards (HTML5/CSS3/JavaScript).
=======
