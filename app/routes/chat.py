from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatHistory
from app.schemas import (
    GenerateRequest,
    RegenerateRequest,
    TransformRequest,
    GenerateResponse,
)
from app.services.prompt_service import PromptService
from app.services.ollama_service import OllamaServiceError
from app.services.ai_provider import get_ai_service

router = APIRouter(prefix="/api", tags=["Content Generation"])


def _save_generation(
    db: Session,
    session_id: str,
    content_type: str,
    user_prompt: str,
    generated_response: str,
    tone: str,
    audience: str,
    length: str
) -> ChatHistory:
    """Helper function to record generation into SQLite database."""
    record = ChatHistory(
        session_id=session_id,
        content_type=content_type,
        user_prompt=user_prompt,
        generated_response=generated_response,
        tone=tone,
        audience=audience,
        length=length,
        created_at=datetime.now(timezone.utc)
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(req: GenerateRequest, db: Session = Depends(get_db)):
    """
    Main content generation endpoint.
    Builds an engineered prompt and queries Ollama (Llama 3.2), saving the result to SQLite.
    """
    try:
        engineered_prompt = PromptService.build_prompt(
            user_prompt=req.user_prompt,
            content_type=req.content_type,
            tone=req.tone,
            audience=req.audience,
            length=req.length,
        )

        ai_service = get_ai_service()
        generated_text = await ai_service.generate(engineered_prompt)

        record = _save_generation(
            db=db,
            session_id=req.session_id or "default-session",
            content_type=req.content_type.value,
            user_prompt=req.user_prompt,
            generated_response=generated_text,
            tone=req.tone.value,
            audience=req.audience.value,
            length=req.length.value,
        )

        return GenerateResponse(
            id=record.id,
            session_id=record.session_id,
            content_type=record.content_type,
            user_prompt=record.user_prompt,
            generated_response=record.generated_response,
            tone=record.tone,
            audience=record.audience,
            length=record.length,
            created_at=record.created_at.isoformat(),
            model=ai_service.model if hasattr(ai_service, 'model') else 'unknown'
        )

    except OllamaServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while generating content: {str(err)}"
        )


@router.post("/regenerate", response_model=GenerateResponse)
async def regenerate_content(req: RegenerateRequest, db: Session = Depends(get_db)):
    """
    Regenerates alternative content using the same original parameters.
    """
    try:
        engineered_prompt = PromptService.build_regenerate_prompt(
            user_prompt=req.user_prompt,
            content_type=req.content_type.value,
            tone=req.tone.value,
            audience=req.audience.value,
            length=req.length.value,
            previous_response=req.previous_response
        )

        ai_service = get_ai_service()
        generated_text = await ai_service.generate(engineered_prompt)

        record = _save_generation(
            db=db,
            session_id=req.session_id or "default-session",
            content_type=req.content_type.value,
            user_prompt=f"[Regenerated] {req.user_prompt}",
            generated_response=generated_text,
            tone=req.tone.value,
            audience=req.audience.value,
            length=req.length.value,
        )

        return GenerateResponse(
            id=record.id,
            session_id=record.session_id,
            content_type=record.content_type,
            user_prompt=record.user_prompt,
            generated_response=record.generated_response,
            tone=record.tone,
            audience=record.audience,
            length=record.length,
            created_at=record.created_at.isoformat(),
            model=ai_service.model if hasattr(ai_service, 'model') else 'unknown'
        )

    except OllamaServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate response: {str(err)}"
        )


@router.post("/improve", response_model=GenerateResponse)
async def improve_content(req: TransformRequest, db: Session = Depends(get_db)):
    """
    Polishes and improves the clarity, vocabulary, and impact of the previous response.
    """
    try:
        engineered_prompt = PromptService.build_improve_prompt(
            previous_response=req.previous_response,
            content_type=req.content_type.value,
            tone=req.tone.value,
            audience=req.audience.value,
            length=req.length.value,
            user_prompt=req.user_prompt or ""
        )

        ai_service = get_ai_service()
        generated_text = await ai_service.generate(engineered_prompt)

        record = _save_generation(
            db=db,
            session_id=req.session_id or "default-session",
            content_type=req.content_type.value,
            user_prompt=f"[Improved] {req.user_prompt or 'Polished content'}",
            generated_response=generated_text,
            tone=req.tone.value,
            audience=req.audience.value,
            length=req.length.value,
        )

        return GenerateResponse(
            id=record.id,
            session_id=record.session_id,
            content_type=record.content_type,
            user_prompt=record.user_prompt,
            generated_response=record.generated_response,
            tone=record.tone,
            audience=record.audience,
            length=record.length,
            created_at=record.created_at.isoformat(),
            model=ai_service.model if hasattr(ai_service, 'model') else 'unknown'
        )

    except OllamaServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to improve content: {str(err)}"
        )


@router.post("/shorten", response_model=GenerateResponse)
async def shorten_content(req: TransformRequest, db: Session = Depends(get_db)):
    """
    Condenses the previous response into high-impact brevity while preserving core substance.
    """
    try:
        engineered_prompt = PromptService.build_shorten_prompt(
            previous_response=req.previous_response,
            content_type=req.content_type.value,
            tone=req.tone.value,
            audience=req.audience.value,
            user_prompt=req.user_prompt or ""
        )

        ai_service = get_ai_service()
        generated_text = await ai_service.generate(engineered_prompt)

        record = _save_generation(
            db=db,
            session_id=req.session_id or "default-session",
            content_type=req.content_type.value,
            user_prompt=f"[Shortened] {req.user_prompt or 'Condensed content'}",
            generated_response=generated_text,
            tone=req.tone.value,
            audience=req.audience.value,
            length="Short",
        )

        return GenerateResponse(
            id=record.id,
            session_id=record.session_id,
            content_type=record.content_type,
            user_prompt=record.user_prompt,
            generated_response=record.generated_response,
            tone=record.tone,
            audience=record.audience,
            length="Short",
            created_at=record.created_at.isoformat(),
            model=ai_service.model if hasattr(ai_service, 'model') else 'unknown'
        )

    except OllamaServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to shorten content: {str(err)}"
        )


@router.post("/expand", response_model=GenerateResponse)
async def expand_content(req: TransformRequest, db: Session = Depends(get_db)):
    """
    Expands the previous response with deeper explanation, examples, and comprehensive coverage.
    """
    try:
        engineered_prompt = PromptService.build_expand_prompt(
            previous_response=req.previous_response,
            content_type=req.content_type.value,
            tone=req.tone.value,
            audience=req.audience.value,
            user_prompt=req.user_prompt or ""
        )

        ai_service = get_ai_service()
        generated_text = await ai_service.generate(engineered_prompt)

        record = _save_generation(
            db=db,
            session_id=req.session_id or "default-session",
            content_type=req.content_type.value,
            user_prompt=f"[Expanded] {req.user_prompt or 'Elaborated content'}",
            generated_response=generated_text,
            tone=req.tone.value,
            audience=req.audience.value,
            length="Detailed",
        )

        return GenerateResponse(
            id=record.id,
            session_id=record.session_id,
            content_type=record.content_type,
            user_prompt=record.user_prompt,
            generated_response=record.generated_response,
            tone=record.tone,
            audience=record.audience,
            length="Detailed",
            created_at=record.created_at.isoformat(),
            model=ai_service.model if hasattr(ai_service, 'model') else 'unknown'
        )

    except OllamaServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand content: {str(err)}"
        )
