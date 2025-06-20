from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Response, Query
from api.adk.tools.pdf_tools import save_topic_on_db
from api.models.kiddo import Kiddo
from api.services.agent_engine import build_pdf_content, run_agent
from sqlmodel import select
from typing import List, Optional
import tempfile
from api.adk.agent import pdf_extractor_agent
from api.services.video_db_service import save_pdf_in_vect_db

# Importa la dipendenza e (se usi SQLModel) la funzione di inizializzazione
from .db import create_tables, get_session
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Avvio dell'applicazione in corso...")
    await create_tables()
    print("Setup del database completato.")

    yield

    print("Spegnimento dell'applicazione...")


app = FastAPI(lifespan=lifespan)

# ENDPOINTS

@app.get("/api/kiddos", response_model=List[Kiddo])
async def get_kiddos(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Kiddo))
    kiddos = result.scalars().all()
    return kiddos

@app.get("/api/kiddos/{kiddo_id}", response_model=Kiddo)
async def get_kiddo(kiddo_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
    kiddo = result.scalar_one_or_none()
    if not kiddo:
        return Response(status_code=404)
    return kiddo

@app.post("/api/kiddos", response_model=Kiddo)
async def create_kiddo(kiddo: Kiddo, db: AsyncSession = Depends(get_session)):
    db.add(kiddo)
    await db.commit()
    await db.refresh(kiddo)
    return kiddo

@app.put("/api/kiddos/{kiddo_id}", response_model=Kiddo)
async def update_kiddo(kiddo_id: int, kiddo: Kiddo, db: AsyncSession = Depends(get_session)):
    existing_kiddo = await db.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
    existing_kiddo = existing_kiddo.scalar_one_or_none()
    if not existing_kiddo:
        return Response(status_code=404)
    
    for key, value in kiddo.dict(exclude_unset=True).items():
        setattr(existing_kiddo, key, value)
    
    await db.commit()
    await db.refresh(existing_kiddo)
    return existing_kiddo

@app.delete("/api/kiddos/{kiddo_id}", response_model=Kiddo)
async def delete_kiddo(kiddo_id: int, db: AsyncSession = Depends(get_session)):
    existing_kiddo = await db.execute(select(Kiddo).where(Kiddo.id == kiddo_id))
    existing_kiddo = existing_kiddo.scalar_one_or_none()
    if not existing_kiddo:
        return Response(status_code=404)
    
    await db.delete(existing_kiddo)
    await db.commit()
    return existing_kiddo

@app.post("/api/upload-pdf")
async def upload_file(file: UploadFile = File(...), kiddo_id: int = Query(...)):
    stream = file.file.read()
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(stream)
        content = build_pdf_content(stream)
        
    save_pdf_in_vect_db(tmp.name, file.filename)

    res = run_agent(pdf_extractor_agent, content)

    await save_topic_on_db(res)

    return Response(content="PDF loaded", media_type="text/plain")
