# AI Content Generation Chatbot

A sophisticated, modern web-based AI assistant built with **FastAPI**, **SQLite**, and **Groq API** (powered by `openai/gpt-oss-120b`). This application features advanced prompt engineering routing, seamless session-based chat UI, and in-place message editing. 

## Features

- **Groq API Integration:** Lightning-fast AI inference utilizing `openai/gpt-oss-120b` instead of local models.
- **Session-Based Architecture:** Persistent conversational history grouped by discrete chat sessions.
- **Advanced Prompt Engineering:** Dynamic injection of constraints (Tone, Audience, Length, Content Type) without polluting the conversational context window.
- **In-Place Prompt Editing:** A robust "Edit" feature that allows users to edit previous prompts, seamlessly truncating subsequent history and regenerating the response.
- **Markdown Rendering:** Beautifully styled responses using `marked.js`, natively supporting tables, bolding, lists, and headers.
- **Transformative Actions:** Built-in actions to *Improve*, *Shorten*, *Expand*, or *Regenerate* previous AI responses intelligently.

## Tech Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy, Pydantic, HTTPX
- **Database:** SQLite (persisted to `chatbot.db`)
- **Frontend:** HTML5, CSS3 (Modern Flexbox/Grid), Vanilla JavaScript (ES6)
- **Deployment:** Pre-configured `render.yaml` for Render Cloud

## Setup & Local Development

1. **Clone the repository and install dependencies:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Rename `.env.example` to `.env` and configure your keys:
   ```ini
   AI_PROVIDER=Groq
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   DATABASE_URL=sqlite:///./chatbot.db
   ```

3. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the Application:**
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Architecture Note

The application employs a dual-layer prompt system. When you submit a prompt, the system:
1. Loads the latest 4 messages of conversational history to give the LLM memory without exceeding Token Limits (TPM limits).
2. Wraps your *most recent* prompt into a heavily engineered template (via `PromptService`) that injects formatting, constraints, and structural directives.
3. Streams the combined payload to the Groq API for near-instant inference.

## Deployment on Render

This project is perfectly optimized for Render Cloud deployment.
- It leverages the dynamic `$PORT` environment variable.
- It includes a `/api/health` endpoint for Render's zero-downtime deployment checks.
- It uses SQLite, which requires a persistent disk on Render to save chat histories across server restarts.

**Steps to deploy:**
1. Push this repository to GitHub.
2. Link the repository in the Render Dashboard as a new Web Service.
3. Ensure you set the `GROQ_API_KEY` Environment Variable in Render.
4. Render will automatically detect the `render.yaml` and install dependencies.
