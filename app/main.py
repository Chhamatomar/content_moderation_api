from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas
from app.moderation import moderate_text

# Creates the moderation_results table if it doesn't already exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Content Moderation API",
    description="A simple API that analyzes text and returns moderation results.",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "Content Moderation API is running"}


@app.post("/moderate", response_model=schemas.ModerationResponse)
def moderate(request: schemas.ModerationRequest, db: Session = Depends(get_db)):
    # Run the text through our rule-based moderation logic
    result = moderate_text(request.text)

    # Create a new SQLAlchemy model instance with the original text + results
    db_result = models.ModerationResult(
        text=request.text,
        is_flagged=result["is_flagged"],
        category=result["category"],
        confidence=result["confidence"],
    )

    # Save it to PostgreSQL
    db.add(db_result)
    db.commit()
    db.refresh(db_result)  # reloads db_result with DB-generated fields (id, created_at)

    return db_result


@app.get("/moderation/{result_id}", response_model=schemas.ModerationResponse)
def get_moderation_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(models.ModerationResult).filter(
        models.ModerationResult.id == result_id
    ).first()

    if result is None:
        raise HTTPException(status_code=404, detail="Moderation result not found")

    return result


@app.get("/health")
def health_check():
    return {"status": "ok"}