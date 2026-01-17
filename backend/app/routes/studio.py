from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.studio import Studio
from app.schemas import studio as schemas

router = APIRouter()


@router.get("/", response_model=list)
def list_studios(db: Session = Depends(get_db)):
    """Get all studios"""
    studios = db.query(Studio).all()
    return studios


@router.post("/", response_model=dict)
def create_studio(studio: dict, db: Session = Depends(get_db)):
    """Create new studio"""
    db_studio = Studio(
        name=studio.get("name"),
        location=studio.get("location"),
        description=studio.get("description"),
    )
    db.add(db_studio)
    db.commit()
    db.refresh(db_studio)
    return {"id": db_studio.id, "name": db_studio.name, "message": "Studio created"}


@router.get("/{studio_id}", response_model=dict)
def get_studio(studio_id: int, db: Session = Depends(get_db)):
    """Get studio by ID"""
    studio = db.query(Studio).filter(Studio.id == studio_id).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    return {"id": studio.id, "name": studio.name, "location": studio.location}


@router.put("/{studio_id}")
def update_studio(studio_id: int, studio: dict, db: Session = Depends(get_db)):
    """Update studio"""
    db_studio = db.query(Studio).filter(Studio.id == studio_id).first()
    if not db_studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    
    if "name" in studio:
        db_studio.name = studio["name"]
    if "location" in studio:
        db_studio.location = studio["location"]
    if "description" in studio:
        db_studio.description = studio["description"]
    
    db.commit()
    return {"message": "Studio updated"}


@router.delete("/{studio_id}")
def delete_studio(studio_id: int, db: Session = Depends(get_db)):
    """Delete studio"""
    db_studio = db.query(Studio).filter(Studio.id == studio_id).first()
    if not db_studio:
        raise HTTPException(status_code=404, detail="Studio not found")
    
    db.delete(db_studio)
    db.commit()
    return {"message": "Studio deleted"}
