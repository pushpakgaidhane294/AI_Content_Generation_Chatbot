from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatSession, ChatMessage
from app.schemas import SessionListResponse, ChatSessionResponse, ChatMessageResponse

router = APIRouter(prefix="/api/sessions", tags=["Chat Sessions"])


@router.get("", response_model=SessionListResponse)
def get_all_sessions(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Retrieves all chat sessions ordered by recently updated.
    """
    query = db.query(ChatSession)
    total = query.count()
    items = query.order_by(ChatSession.updated_at.desc()).offset(offset).limit(limit).all()

    formatted = [
        ChatSessionResponse(
            id=item.id,
            title=item.title,
            created_at=item.created_at.isoformat() if item.created_at else "",
            updated_at=item.updated_at.isoformat() if item.updated_at else ""
        )
        for item in items
    ]

    return SessionListResponse(total=total, items=formatted)


@router.get("/{session_id}", response_model=ChatSessionResponse)
def get_session_by_id(session_id: str, db: Session = Depends(get_db)):
    """
    Fetches a specific chat session and all its messages.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found."
        )

    messages = [
        ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            content_type=m.content_type,
            tone=m.tone,
            audience=m.audience,
            length=m.length,
            created_at=m.created_at.isoformat() if m.created_at else ""
        )
        for m in session.messages
    ]

    return ChatSessionResponse(
        id=session.id,
        title=session.title,
        created_at=session.created_at.isoformat() if session.created_at else "",
        updated_at=session.updated_at.isoformat() if session.updated_at else "",
        messages=messages
    )


@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    Deletes an individual session by ID.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found."
        )

    db.delete(session)
    db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted successfully."}


@router.delete("")
def clear_all_sessions(db: Session = Depends(get_db)):
    """
    Clears all conversation sessions.
    """
    deleted_count = db.query(ChatSession).delete(synchronize_session=False)
    db.commit()
    return {
        "status": "success",
        "deleted_count": deleted_count,
        "message": f"Cleared {deleted_count} conversation sessions."
    }

from pydantic import BaseModel
class EditMessageRequest(BaseModel):
    message_id: int
    new_prompt: str
    content_type: str = "GENERAL CONTENT"
    tone: str = "Professional"
    audience: str = "General Audience"
    length: str = "Medium"

from app.services.prompt_service import PromptService
from app.services.ai_provider import get_ai_service

@router.put("/{session_id}/edit_prompt")
async def edit_prompt(session_id: str, req: EditMessageRequest, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    user_msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id, ChatMessage.session_id == session_id).first()
    if not user_msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    # Update the prompt
    user_msg.content = req.new_prompt
    
    # Delete all messages in the session after this message
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id, ChatMessage.id > req.message_id).delete(synchronize_session=False)
    db.commit()
    
    # Now generate new response
    engineered_prompt = PromptService.build_prompt(
        user_prompt=req.new_prompt,
        content_type=req.content_type,
        tone=req.tone,
        audience=req.audience,
        length=req.length,
    )
    
    ai_service = get_ai_service()
    history = []
    # Fetch last 4 messages and exclude the newly updated user_msg
    past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id.desc()).limit(5).all()
    past_msgs.reverse()
    for m in past_msgs[:-1]: 
        content = m.content
        if len(content) > 1500:
            content = content[:1500] + "... [truncated]"
        history.append({"role": m.role, "content": content})
        
    generated_text = await ai_service.generate(engineered_prompt, history=history)
    
    # Save the new assistant message
    asst_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=generated_text,
        content_type=req.content_type,
        tone=req.tone,
        audience=req.audience,
        length=req.length
    )
    db.add(asst_msg)
    
    from datetime import datetime, timezone, timedelta
    session.updated_at = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    db.commit()
    db.refresh(user_msg)
    db.refresh(asst_msg)
    
    return {
        "user_message": {
            "id": user_msg.id,
            "role": user_msg.role,
            "content": user_msg.content
        },
        "assistant_message": {
            "id": asst_msg.id,
            "role": asst_msg.role,
            "content": asst_msg.content,
            "content_type": asst_msg.content_type,
            "tone": asst_msg.tone,
            "audience": asst_msg.audience,
            "length": asst_msg.length
        }
    }
