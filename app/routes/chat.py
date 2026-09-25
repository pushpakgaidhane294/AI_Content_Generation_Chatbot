from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatSession, ChatMessage
from app.schemas import (
    GenerateRequest,
    RegenerateRequest,
    TransformRequest,
    GenerateResponse,
)
from app.services.prompt_service import PromptService
from app.services.groq_service import GroqServiceError
from app.services.ai_provider import get_ai_service

router = APIRouter(prefix="/api", tags=["Content Generation"])

import io
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

class DownloadDocxRequest(BaseModel):
    text: str

@router.post("/download/docx")
async def download_docx(req: DownloadDocxRequest):
    try:
        from docx import Document
    except ImportError:
        raise HTTPException(status_code=500, detail="python-docx not installed")

    import re
    doc = Document()
    
    def _parse_inline(p, text):
        pattern = re.compile(r'(\*\*(.*?)\*\*|\*(.*?)\*|`(.*?)`|\[(.*?)\]\((.*?)\))')
        last_idx = 0
        for match in pattern.finditer(text):
            if match.start() > last_idx:
                p.add_run(text[last_idx:match.start()])
            full_match = match.group(0)
            if full_match.startswith('**'):
                run = p.add_run(match.group(2))
                run.bold = True
            elif full_match.startswith('*'):
                run = p.add_run(match.group(3))
                run.italic = True
            elif full_match.startswith('`'):
                run = p.add_run(match.group(4))
                try:
                    from docx.shared import Pt
                    run.font.name = 'Courier New'
                except:
                    pass
            elif full_match.startswith('['):
                run = p.add_run(match.group(5))
                run.underline = True
                try:
                    from docx.shared import RGBColor
                    run.font.color.rgb = RGBColor(5, 99, 193)
                except:
                    pass
            last_idx = match.end()
        if last_idx < len(text):
            p.add_run(text[last_idx:])

    lines = req.text.split('\n')
    i = 0
    in_code_block = False
    code_block_text = []
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("```"):
            if in_code_block:
                in_code_block = False
                p = doc.add_paragraph('\n'.join(code_block_text))
                p.style = 'No Spacing' if 'No Spacing' in [s.name for s in doc.styles] else 'Normal'
                code_block_text = []
            else:
                in_code_block = True
            i += 1
            continue
            
        if in_code_block:
            code_block_text.append(lines[i])
            i += 1
            continue
            
        if not line:
            i += 1
            continue
            
        if line == '---' or line == '***' or line == '___':
            doc.add_paragraph('_' * 40)
            i += 1
            continue
            
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            heading_text = m.group(2)
            p = doc.add_heading(level=level)
            _parse_inline(p, heading_text)
            i += 1
            continue
            
        m = re.match(r'^[\-\*]\s+(.*)', line)
        if m:
            p = doc.add_paragraph(style='List Bullet')
            _parse_inline(p, m.group(1))
            i += 1
            continue
            
        m = re.match(r'^\d+\.\s+(.*)', line)
        if m:
            p = doc.add_paragraph(style='List Number')
            _parse_inline(p, m.group(1))
            i += 1
            continue
            
        if line.startswith('|') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            # Check if second row is a separator row
            if '---' in lines[i+1]:
                headers = [h for h in line.split('|')[1:-1]]
                table_lines = []
                i += 2
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i].strip())
                    i += 1
                    
                if headers:
                    table = doc.add_table(rows=1, cols=len(headers))
                    table.style = 'Table Grid'
                    hdr_cells = table.rows[0].cells
                    for j, h in enumerate(headers):
                        if j < len(hdr_cells):
                            _parse_inline(hdr_cells[j].paragraphs[0], h.strip())
                            if hdr_cells[j].paragraphs[0].runs:
                                hdr_cells[j].paragraphs[0].runs[0].bold = True
                            
                    for tline in table_lines:
                        row_cells = table.add_row().cells
                        cells = [c for c in tline.split('|')[1:-1]]
                        for j, c in enumerate(cells):
                            if j < len(row_cells):
                                _parse_inline(row_cells[j].paragraphs[0], c.strip())
                continue

        p = doc.add_paragraph()
        _parse_inline(p, line)
        i += 1
        
    f = io.BytesIO()
    doc.save(f)
    f.seek(0)
    
    return StreamingResponse(
        f, 
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=generated_content.docx"}
    )





def _save_generation(
    db: Session,
    session_id: str,
    content_type: str,
    user_prompt: str,
    generated_response: str,
    tone: str,
    audience: str,
    length: str
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        title = user_prompt[:30] + ("..." if len(user_prompt) > 30 else "")
        session = ChatSession(id=session_id, title=title)
        db.add(session)
        db.flush()

    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=user_prompt
    )
    db.add(user_msg)
    db.flush()
    
    asst_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=generated_response,
        content_type=content_type,
        tone=tone,
        audience=audience,
        length=length
    )
    db.add(asst_msg)
    
    from datetime import datetime, timezone, timedelta
    session.updated_at = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    db.commit()
    db.refresh(asst_msg)
    db.refresh(user_msg)
    
    class DummyRecord:
        def __init__(self):
            self.id = asst_msg.id
            self.user_message_id = user_msg.id
            self.session_id = session_id
            self.content_type = content_type
            self.user_prompt = user_prompt
            self.generated_response = generated_response
            self.tone = tone
            self.audience = audience
            self.length = length
            self.created_at = asst_msg.created_at
    return DummyRecord()
@router.post("/generate", response_model=GenerateResponse)
async def generate_content(req: GenerateRequest, db: Session = Depends(get_db)):
    """
    Main content generation endpoint.
    Builds an engineered prompt and queries Groq (Llama 3.2), saving the result to SQLite.
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
        
        history = []
        if req.session_id and req.session_id != "default-session":
            # Fetch only the last 4 messages to save tokens
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id.desc()).limit(4).all()
            past_msgs.reverse()
            for m in past_msgs:
                content = m.content
                # Truncate past messages if they are too long (saving TPM limits)
                if len(content) > 1500:
                    content = content[:1500] + "... [truncated]"
                history.append({"role": m.role, "content": content})
                
        generated_text = await ai_service.generate(engineered_prompt, history=history)

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
            user_message_id=record.user_message_id,
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

    except GroqServiceError as err:
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
        
        history = []
        if req.session_id and req.session_id != "default-session":
            # Fetch only the last 4 messages to save tokens
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id.desc()).limit(4).all()
            past_msgs.reverse()
            for m in past_msgs:
                content = m.content
                # Truncate past messages if they are too long (saving TPM limits)
                if len(content) > 1500:
                    content = content[:1500] + "... [truncated]"
                history.append({"role": m.role, "content": content})
                
        generated_text = await ai_service.generate(engineered_prompt, history=history)

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
            user_message_id=record.user_message_id,
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

    except GroqServiceError as err:
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
        
        history = []
        if req.session_id and req.session_id != "default-session":
            # Fetch only the last 4 messages to save tokens
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id.desc()).limit(4).all()
            past_msgs.reverse()
            for m in past_msgs:
                content = m.content
                # Truncate past messages if they are too long (saving TPM limits)
                if len(content) > 1500:
                    content = content[:1500] + "... [truncated]"
                history.append({"role": m.role, "content": content})
                
        generated_text = await ai_service.generate(engineered_prompt, history=history)

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
            user_message_id=record.user_message_id,
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

    except GroqServiceError as err:
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
        
        history = []
        if req.session_id and req.session_id != "default-session":
            # Fetch only the last 4 messages to save tokens
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id.desc()).limit(4).all()
            past_msgs.reverse()
            for m in past_msgs:
                content = m.content
                # Truncate past messages if they are too long (saving TPM limits)
                if len(content) > 1500:
                    content = content[:1500] + "... [truncated]"
                history.append({"role": m.role, "content": content})
                
        generated_text = await ai_service.generate(engineered_prompt, history=history)

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
            user_message_id=record.user_message_id,
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

    except GroqServiceError as err:
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
        
        history = []
        if req.session_id and req.session_id != "default-session":
            # Fetch only the last 4 messages to save tokens
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == req.session_id).order_by(ChatMessage.id.desc()).limit(4).all()
            past_msgs.reverse()
            for m in past_msgs:
                content = m.content
                # Truncate past messages if they are too long (saving TPM limits)
                if len(content) > 1500:
                    content = content[:1500] + "... [truncated]"
                history.append({"role": m.role, "content": content})
                
        generated_text = await ai_service.generate(engineered_prompt, history=history)

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
            user_message_id=record.user_message_id,
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

    except GroqServiceError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to expand content: {str(err)}"
        )
