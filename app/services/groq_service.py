"""
Groq Cloud LLM Service (FREE).
Communicates with Groq API for free cloud-based generation.
No credit card required, completely free tier available.
"""

import os
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


class GroqServiceError(Exception):
    """Custom exception for Groq errors."""
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GroqService:
    """Service wrapper for Groq API (FREE)."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.model = os.getenv("GROQ_MODEL", "llama3-8b-8192")
        self.timeout = float(os.getenv("GROQ_TIMEOUT", "120.0"))
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
    
    async def check_status(self) -> Dict[str, Any]:
        """Check if Groq API is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
            
            if response.status_code == 200:
                return {
                    "connected": True,
                    "model": self.model,
                    "available_models": [self.model],
                    "base_url": self.base_url,
                    "message": "Connected to Groq API (FREE)"
                }
            else:
                return {
                    "connected": False,
                    "model": self.model,
                    "available_models": [],
                    "base_url": self.base_url,
                    "message": f"Groq API returned HTTP {response.status_code}"
                }
        except Exception as exc:
            return {
                "connected": False,
                "model": self.model,
                "available_models": [],
                "base_url": self.base_url,
                "message": f"Groq API error: {str(exc)}"
            }
    
    async def generate(self, prompt: str, system_override: Optional[str] = None) -> str:
        """Generate content using Groq API (FREE)."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_override or "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2048
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
            
            if response.status_code == 401:
                raise GroqServiceError(
                    "Invalid Groq API key. Please check your GROQ_API_KEY environment variable.",
                    status_code=401
                )
            elif response.status_code != 200:
                raise GroqServiceError(
                    f"Groq API error: {response.text}",
                    status_code=response.status_code
                )
            
            data = response.json()
            generated_text = data["choices"][0]["message"]["content"].strip()
            
            if not generated_text:
                raise GroqServiceError("Groq returned empty response", status_code=500)
            
            return generated_text
            
        except GroqServiceError:
            raise
        except Exception as exc:
            raise GroqServiceError(
                f"Groq generation error: {str(exc)}",
                status_code=500
            )


# Singleton instance
groq_service = GroqService()