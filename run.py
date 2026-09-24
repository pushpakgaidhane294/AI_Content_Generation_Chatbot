import os
import uvicorn
from dotenv import load_dotenv

load_dotenv(override=True)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() in ("true", "1", "yes")

    print(f"Starting AI Content Generation Chatbot on http://{host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )
