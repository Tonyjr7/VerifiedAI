import json

from fastapi import HTTPException
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.dependencies import get_db
from models.library import Library

community_router = APIRouter(prefix="/community", tags=["community"])

class CommunityRequest(BaseModel):
    username: str
    debunked_claim: dict
    

@community_router.post("/post")
async def post_claim_debunked(request: CommunityRequest, db: Session = Depends(get_db)):
    """Post claim on community board."""
    try:
        new_debuked = Library(username=request.username, debunked=request.debunked_claim)
        
        db.add(new_debuked)
        db.commit()
        db.refresh(new_debuked)
        return {"message": "Added to community"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@community_router.get("/get")
async def get_community_claims(
    page: int = 1, 
    limit: int = 5, 
    search: str = "", 
    category: str = "All", 
    db: Session = Depends(get_db)
):
    """Get claims from community board with pagination and filtering."""
    try:
        # Load records ordered by newest first
        all_records = db.query(Library).order_by(Library.id.desc()).all()
        
        filtered = []
        for record in all_records:
            # Safely resolve debunked dictionary structure
            deb = record.debunked or {}
            if isinstance(deb, str):
                try:
                    deb = json.loads(deb)
                except Exception:
                    deb = {}
            
            if not isinstance(deb, dict):
                deb = {}

            # Category filter
            rec_cat = deb.get("category", "General")
            if category and category != "All" and rec_cat.lower() != category.lower():
                continue
                
            # Search filter (checks claim and summary text fields)
            if search:
                claim_text = deb.get("claim", "")
                summary_text = deb.get("summary", "")
                s_term = search.lower()
                if s_term not in claim_text.lower() and s_term not in summary_text.lower():
                    continue
            
            filtered.append(record)
            
        total = len(filtered)
        offset = (page - 1) * limit
        paginated_records = filtered[offset : offset + limit]
        
        return {
            "claims": paginated_records,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@community_router.get("/get/{id}")
async def get_community_claim(id: str, db: Session = Depends(get_db)):
    """Get claim from community board."""
    try:
        claim = db.query(Library).filter(Library.claim_id == id).first()
        return {"claim": claim}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@community_router.get("/search")
async def search_claims(query: str, db: Session = Depends(get_db)):
    """Search claim on community board."""
    try:
        claims = db.query(Library).filter(Library.debunked.ilike(f"%{query}%")).all()
        return {"claims": claims}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))