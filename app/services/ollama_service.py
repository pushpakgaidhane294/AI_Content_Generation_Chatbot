"""
Ollama Local LLM Service.
Communicates with the local Ollama daemon via HTTP REST API.
Handles connection checks, model availability, generation requests, and user-friendly error wrapping.
"""

import os
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()


class OllamaServiceError(Exception):
    """Custom application-level exception for Ollama errors with user-friendly messages."""
    def __init__(self, message: str, status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OllamaService:
    """
    Service wrapper for interacting with the Ollama API.
    """

    def __init__(self):
        # Default to 127.0.0.1 on Windows to avoid IPv6 localhost resolution delays,
        # but respect OLLAMA_BASE_URL if explicitly provided.
        env_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        # Normalize localhost to 127.0.0.1 for reliable local connection on Windows
        if "localhost:11434" in env_url:
            self.base_url = env_url.replace("localhost:11434", "127.0.0.1:11434")
        else:
            self.base_url = env_url

        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "120.0"))

    async def check_status(self) -> Dict[str, Any]:
        """
        Pings Ollama server and verifies if the configured model is installed.
        Returns diagnostic dictionary.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")

            if response.status_code != 200:
                return {
                    "connected": False,
                    "model": self.model,
                    "available_models": [],
                    "base_url": self.base_url,
                    "message": f"Ollama returned HTTP status {response.status_code}."
                }

            data = response.json()
            raw_models = data.get("models", [])
            available_names = [m.get("name", "") for m in raw_models]

            # Check if requested model matches (e.g. 'llama3.2' matches 'llama3.2:latest')
            model_found = any(
                name == self.model or name.startswith(f"{self.model}:")
                for name in available_names
            )

            if not model_found and len(available_names) > 0:
                msg = f"Ollama is connected, but model '{self.model}' was not found. Available: {', '.join(available_names)}. Run 'ollama pull {self.model}'."
            elif not model_found:
                msg = f"Ollama is connected, but no models are installed. Run 'ollama pull {self.model}'."
            else:
                msg = "Connected and model ready."

            return {
                "connected": True,
                "model": self.model,
                "available_models": available_names,
                "base_url": self.base_url,
                "message": msg
            }

        except (httpx.ConnectError, httpx.ConnectTimeout):
            return {
                "connected": False,
                "model": self.model,
                "available_models": [],
                "base_url": self.base_url,
                "message": "Ollama is not running. Please start Ollama and try again."
            }
        except httpx.RequestError as exc:
            return {
                "connected": False,
                "model": self.model,
                "available_models": [],
                "base_url": self.base_url,
                "message": f"Unable to reach Ollama: {str(exc)}"
            }
        except Exception as exc:
            return {
                "connected": False,
                "model": self.model,
                "available_models": [],
                "base_url": self.base_url,
                "message": f"Unexpected error connecting to Ollama: {str(exc)}"
            }

    async def generate(self, prompt: str, system_override: Optional[str] = None) -> str:
        """
        Sends an engineered prompt to Ollama and returns the generated content.
        Raises OllamaServiceError with helpful user-facing messages upon failure.
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            }
        }
        if system_override:
            payload["system"] = system_override

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)

            if response.status_code == 404:
                raise OllamaServiceError(
                    f"Model '{self.model}' not found in Ollama. Please run 'ollama pull {self.model}' in your terminal.",
                    status_code=404
                )
            elif response.status_code != 200:
                raise OllamaServiceError(
                    f"Ollama API returned an error (HTTP {response.status_code}): {response.text}",
                    status_code=response.status_code
                )

            data = response.json()
            generated_text = data.get("response", "").strip()

            if not generated_text:
                raise OllamaServiceError("Ollama returned an empty response. Please try modifying your prompt.", status_code=500)

            return generated_text

        except (httpx.ConnectError, httpx.ConnectTimeout):
            raise OllamaServiceError(
                "Ollama is not running. Please start Ollama and try again.",
                status_code=503
            )
        except httpx.ReadTimeout:
            raise OllamaServiceError(
                "Ollama generation timed out. The local model took too long to respond. Try requesting a shorter length.",
                status_code=504
            )
        except httpx.RequestError as exc:
            raise OllamaServiceError(
                f"Communication error with Ollama service: {str(exc)}",
                status_code=503
            )
        except OllamaServiceError:
            raise
        except Exception as exc:
            raise OllamaServiceError(
                f"An unexpected error occurred during content generation: {str(exc)}",
                status_code=500
            )


# Singleton instance for easy import across routes
ollama_service = OllamaService()
