from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Response, Query
from api.models.kiddo import Kiddo
from api.services.agent_engine import build_pdf_content, run_agent
from sqlmodel import select # O from sqlalchemy.future import select ecc.
from typing import List, Optional
from api.services.vector_db_service import load_pdf_on_vector_db
import tempfile
import os
from api.adk.agent import pdf_extractor_agent

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
def upload_file(file: UploadFile = File(...), kiddo_id: int = Query(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        content = build_pdf_content(file.file.read())
        tmp_path = tmp.name
        
    try:
        load_pdf_on_vector_db(tmp_path)
        

        session_obj = {
            "kiddo_id": str(kiddo_id),
        }
        run_agent(pdf_extractor_agent, session_obj, content)
        return Response(content="PDF loaded", media_type="text/plain")
    finally:
        os.remove(tmp_path)
