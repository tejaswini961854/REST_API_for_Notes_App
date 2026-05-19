import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBNote(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

class NoteCreate(BaseModel):
    title: str
    content: str

class Note(BaseModel):
    id: int
    title: str
    content: str
    class Config:
        from_attributes = True

@app.get("/notes", response_model=list[Note])
def get_notes():
    db = SessionLocal()
    notes = db.query(DBNote).all()
    db.close()
    return notes

@app.post("/notes", response_model=Note)
def create_note(note: NoteCreate):
    db = SessionLocal()
    new_note = DBNote(title=note.title, content=note.content)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    db.close()
    return new_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    db = SessionLocal()
    db_note = db.query(DBNote).filter(DBNote.id == note_id).first()
    if not db_note:
        db.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(db_note)
    db.commit()
    db.close()
    return {"message": f"Note {note_id} deleted successfully"}