import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import init_db
from app.routes.health import router as health_router
from app.routes.chat import router as chat_router
from app.routes.history import router as history_router

load_dotenv()

# Initialize tables immediately so test clients and workers have database ready
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    Ensures SQLite tables are present on startup.
    """
    init_db()
    yield


app = FastAPI(
    title="AI Content Generation Chatbot",
    description="Production-style Academic Mini-Project using FastAPI, Groq (openai/gpt-oss-120b), and Prompt Engineering",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local development and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Register API Routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(history_router)


@app.get("/", response_class=HTMLResponse)
async def serve_home(request: Request):
    """
    Serves the primary Single Page Application interface.
    Compatible with Starlette/FastAPI kwargs for TemplateResponse.
    """
    return templates.TemplateResponse(request=request, name="index.html")
