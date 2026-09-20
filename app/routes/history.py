from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatHistory
from app.schemas import HistoryItemResponse, HistoryListResponse

router = APIRouter(prefix="/api/history", tags=["Chat History"])


@router.get("", response_model=HistoryListResponse)
def get_all_history(
    session_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Retrieves saved conversation history ordered by most recent first.
    Optionally filters by session_id.
    """
    query = db.query(ChatHistory)
    if session_id:
        query = query.filter(ChatHistory.session_id == session_id)

    total = query.count()
    items = query.order_by(ChatHistory.created_at.desc()).offset(offset).limit(limit).all()

    formatted = [
        HistoryItemResponse(
            id=item.id,
            session_id=item.session_id,
            content_type=item.content_type,
            user_prompt=item.user_prompt,
            generated_response=item.generated_response,
            tone=item.tone,
            audience=item.audience,
            length=item.length,
            created_at=item.created_at.isoformat() if item.created_at else ""
        )
        for item in items
    ]

    return HistoryListResponse(total=total, items=formatted)


@router.get("/{history_id}", response_model=HistoryItemResponse)
def get_history_by_id(history_id: int, db: Session = Depends(get_db)):
    """
    Fetches a specific chat history entry by ID.
    """
    item = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record #{history_id} not found."
        )

    return HistoryItemResponse(
        id=item.id,
        session_id=item.session_id,
        content_type=item.content_type,
        user_prompt=item.user_prompt,
        generated_response=item.generated_response,
        tone=item.tone,
        audience=item.audience,
        length=item.length,
        created_at=item.created_at.isoformat() if item.created_at else ""
    )


@router.delete("/{history_id}")
def delete_history_item(history_id: int, db: Session = Depends(get_db)):
    """
    Deletes an individual history item by ID.
    """
    item = db.query(ChatHistory).filter(ChatHistory.id == history_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record #{history_id} not found."
        )

    db.delete(item)
    db.commit()
    return {"status": "success", "message": f"History record #{history_id} deleted successfully."}


@router.delete("")
def clear_all_history(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Clears conversation history. If session_id is provided, deletes only that session's history.
    Otherwise clears all records.
    """
    query = db.query(ChatHistory)
    if session_id:
        deleted_count = query.filter(ChatHistory.session_id == session_id).delete(synchronize_session=False)
    else:
        deleted_count = query.delete(synchronize_session=False)

    db.commit()
    return {
        "status": "success",
        "deleted_count": deleted_count,
        "message": f"Cleared {deleted_count} conversation history records."
    }
