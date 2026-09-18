from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.api.v1.deps import get_current_user, require_admin, require_agent_or_admin
from app.models.models import User, KBArticle
from app.schemas.advanced_schemas import KBArticleCreate, KBArticleResponse

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])

@router.get("/", response_model=List[KBArticleResponse])
def search_kb_articles(
    query: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(KBArticle)
    if category:
        q = q.filter(KBArticle.category.ilike(f"%{category}%"))
    if query:
        pattern = f"%{query}%"
        q = q.filter(
            or_(
                KBArticle.title.ilike(pattern),
                KBArticle.content.ilike(pattern),
                KBArticle.tags.ilike(pattern)
            )
        )
    return q.limit(20).all()

@router.post("/", response_model=KBArticleResponse, status_code=status.HTTP_201_CREATED)
def create_kb_article(
    payload: KBArticleCreate,
    current_user: User = Depends(require_agent_or_admin),
    db: Session = Depends(get_db)
):
    article = KBArticle(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        tags=payload.tags
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

@router.get("/{article_id}", response_model=KBArticleResponse)
def get_kb_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    article = db.query(KBArticle).filter(KBArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="KB Article not found")
    return article
